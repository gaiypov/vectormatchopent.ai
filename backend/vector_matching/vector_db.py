"""
Модуль для работы с векторной базой данных (Pinecone / Supabase Vector)
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import asyncio
import json

# Импорты для Pinecone
try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# Импорты для Supabase Vector
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

from .config import config
from .models import VectorRecord, CategoryType, EntityType

# Настройка логирования
logger = logging.getLogger(__name__)

class VectorDatabase:
    """Базовый класс для работы с векторной БД"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Инициализация подключения к БД"""
        raise NotImplementedError
    
    async def upsert_vector(self, record: VectorRecord) -> bool:
        """Добавляет или обновляет вектор в БД"""
        raise NotImplementedError
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Получает вектор по ID"""
        raise NotImplementedError
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        category: CategoryType,
        entity_type: EntityType,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Ищет похожие векторы"""
        raise NotImplementedError
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Удаляет вектор из БД"""
        raise NotImplementedError
    
    async def get_vectors_by_entity(
        self, 
        entity_id: str, 
        entity_type: EntityType
    ) -> Dict[CategoryType, VectorRecord]:
        """Получает все векторы для сущности по категориям"""
        raise NotImplementedError

class PineconeVectorDB(VectorDatabase):
    """Реализация для Pinecone Vector DB"""
    
    def __init__(self):
        super().__init__()
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone library not installed. Install with: pip install pinecone-client")
        
        self.pc = None
        self.index = None
    
    async def initialize(self):
        """Инициализация Pinecone"""
        try:
            self.pc = Pinecone(api_key=config.PINECONE_API_KEY)
            
            # Проверяем существование индекса
            if config.PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
                # Создаем индекс если не существует
                self.pc.create_index(
                    name=config.PINECONE_INDEX_NAME,
                    dimension=config.OPENAI_EMBEDDING_DIMENSIONS,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=config.PINECONE_ENVIRONMENT
                    )
                )
                logger.info(f"Created Pinecone index: {config.PINECONE_INDEX_NAME}")
            
            self.index = self.pc.Index(config.PINECONE_INDEX_NAME)
            self.initialized = True
            logger.info("Pinecone initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            raise Exception(f"Failed to initialize Pinecone: {str(e)}")
    
    async def upsert_vector(self, record: VectorRecord) -> bool:
        """Добавляет или обновляет вектор в Pinecone"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Подготавливаем метаданные
            metadata = {
                "entity_id": record.entity_id,
                "entity_type": record.entity_type.value,
                "category": record.category.value,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                **record.metadata
            }
            
            # Upsert в Pinecone
            self.index.upsert(
                vectors=[{
                    "id": record.id,
                    "values": record.vector,
                    "metadata": metadata
                }]
            )
            
            logger.info(f"Upserted vector {record.id} to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vector to Pinecone: {str(e)}")
            return False
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Получает вектор по ID из Pinecone"""
        try:
            if not self.initialized:
                await self.initialize()
            
            result = self.index.fetch(ids=[vector_id])
            
            if vector_id not in result.vectors:
                return None
            
            vector_data = result.vectors[vector_id]
            metadata = vector_data.metadata
            
            return VectorRecord(
                id=vector_data.id,
                entity_id=metadata["entity_id"],
                entity_type=EntityType(metadata["entity_type"]),
                category=CategoryType(metadata["category"]),
                vector=vector_data.values,
                metadata={k: v for k, v in metadata.items() 
                         if k not in ["entity_id", "entity_type", "category", "created_at", "updated_at"]},
                created_at=datetime.fromisoformat(metadata["created_at"]),
                updated_at=datetime.fromisoformat(metadata["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error getting vector from Pinecone: {str(e)}")
            return None
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        category: CategoryType,
        entity_type: EntityType,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Ищет похожие векторы в Pinecone"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Подготавливаем фильтр
            filter_conditions = {
                "category": category.value,
                "entity_type": entity_type.value
            }
            
            if filter_dict:
                filter_conditions.update(filter_dict)
            
            # Выполняем поиск
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_conditions
            )
            
            # Формируем результат
            similar_vectors = []
            for match in results.matches:
                similar_vectors.append((
                    match.id,
                    match.score,
                    match.metadata
                ))
            
            logger.info(f"Found {len(similar_vectors)} similar vectors in Pinecone")
            return similar_vectors
            
        except Exception as e:
            logger.error(f"Error searching similar vectors in Pinecone: {str(e)}")
            return []
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Удаляет вектор из Pinecone"""
        try:
            if not self.initialized:
                await self.initialize()
            
            self.index.delete(ids=[vector_id])
            logger.info(f"Deleted vector {vector_id} from Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vector from Pinecone: {str(e)}")
            return False
    
    async def get_vectors_by_entity(
        self, 
        entity_id: str, 
        entity_type: EntityType
    ) -> Dict[CategoryType, VectorRecord]:
        """Получает все векторы для сущности по категориям"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Ищем все векторы для сущности
            results = self.index.query(
                vector=[0.0] * config.OPENAI_EMBEDDING_DIMENSIONS,  # Dummy vector
                top_k=1000,  # Максимальное количество
                include_metadata=True,
                filter={
                    "entity_id": entity_id,
                    "entity_type": entity_type.value
                }
            )
            
            # Группируем по категориям
            vectors_by_category = {}
            for match in results.matches:
                category = CategoryType(match.metadata["category"])
                vectors_by_category[category] = VectorRecord(
                    id=match.id,
                    entity_id=match.metadata["entity_id"],
                    entity_type=EntityType(match.metadata["entity_type"]),
                    category=category,
                    vector=match.values,
                    metadata={k: v for k, v in match.metadata.items() 
                             if k not in ["entity_id", "entity_type", "category", "created_at", "updated_at"]},
                    created_at=datetime.fromisoformat(match.metadata["created_at"]),
                    updated_at=datetime.fromisoformat(match.metadata["updated_at"])
                )
            
            return vectors_by_category
            
        except Exception as e:
            logger.error(f"Error getting vectors by entity from Pinecone: {str(e)}")
            return {}

class SupabaseVectorDB(VectorDatabase):
    """Реализация для Supabase Vector (pgvector)"""
    
    def __init__(self):
        super().__init__()
        if not SUPABASE_AVAILABLE:
            raise ImportError("Supabase library not installed. Install with: pip install supabase")
        
        self.supabase: Optional[Client] = None
    
    async def initialize(self):
        """Инициализация Supabase"""
        try:
            self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            self.initialized = True
            logger.info("Supabase Vector initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Supabase: {str(e)}")
            raise Exception(f"Failed to initialize Supabase: {str(e)}")
    
    async def upsert_vector(self, record: VectorRecord) -> bool:
        """Добавляет или обновляет вектор в Supabase"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Подготавливаем данные для вставки
            data = {
                "id": record.id,
                "entity_id": record.entity_id,
                "entity_type": record.entity_type.value,
                "category": record.category.value,
                "vector": record.vector,
                "metadata": json.dumps(record.metadata),
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat()
            }
            
            # Upsert в Supabase
            result = self.supabase.table(config.SUPABASE_TABLE).upsert(data).execute()
            
            logger.info(f"Upserted vector {record.id} to Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vector to Supabase: {str(e)}")
            return False
    
    async def get_vector(self, vector_id: str) -> Optional[VectorRecord]:
        """Получает вектор по ID из Supabase"""
        try:
            if not self.initialized:
                await self.initialize()
            
            result = self.supabase.table(config.SUPABASE_TABLE).select("*").eq("id", vector_id).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            return VectorRecord(
                id=row["id"],
                entity_id=row["entity_id"],
                entity_type=EntityType(row["entity_type"]),
                category=CategoryType(row["category"]),
                vector=row["vector"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error getting vector from Supabase: {str(e)}")
            return None
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        category: CategoryType,
        entity_type: EntityType,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Ищет похожие векторы в Supabase"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Строим SQL запрос для поиска похожих векторов
            query = f"""
            SELECT id, vector, metadata, 
                   1 - (vector <=> '{query_vector}') as similarity
            FROM {config.SUPABASE_TABLE}
            WHERE category = '{category.value}' 
            AND entity_type = '{entity_type.value}'
            ORDER BY vector <=> '{query_vector}'
            LIMIT {top_k}
            """
            
            result = self.supabase.rpc('search_similar_vectors', {
                'query_vector': query_vector,
                'category': category.value,
                'entity_type': entity_type.value,
                'top_k': top_k
            }).execute()
            
            # Формируем результат
            similar_vectors = []
            for row in result.data:
                similar_vectors.append((
                    row["id"],
                    row["similarity"],
                    json.loads(row["metadata"]) if row["metadata"] else {}
                ))
            
            logger.info(f"Found {len(similar_vectors)} similar vectors in Supabase")
            return similar_vectors
            
        except Exception as e:
            logger.error(f"Error searching similar vectors in Supabase: {str(e)}")
            return []
    
    async def delete_vector(self, vector_id: str) -> bool:
        """Удаляет вектор из Supabase"""
        try:
            if not self.initialized:
                await self.initialize()
            
            result = self.supabase.table(config.SUPABASE_TABLE).delete().eq("id", vector_id).execute()
            logger.info(f"Deleted vector {vector_id} from Supabase")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vector from Supabase: {str(e)}")
            return False
    
    async def get_vectors_by_entity(
        self, 
        entity_id: str, 
        entity_type: EntityType
    ) -> Dict[CategoryType, VectorRecord]:
        """Получает все векторы для сущности по категориям"""
        try:
            if not self.initialized:
                await self.initialize()
            
            result = self.supabase.table(config.SUPABASE_TABLE).select("*").eq("entity_id", entity_id).eq("entity_type", entity_type.value).execute()
            
            # Группируем по категориям
            vectors_by_category = {}
            for row in result.data:
                category = CategoryType(row["category"])
                vectors_by_category[category] = VectorRecord(
                    id=row["id"],
                    entity_id=row["entity_id"],
                    entity_type=EntityType(row["entity_type"]),
                    category=category,
                    vector=row["vector"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"])
                )
            
            return vectors_by_category
            
        except Exception as e:
            logger.error(f"Error getting vectors by entity from Supabase: {str(e)}")
            return {}

def get_vector_db() -> VectorDatabase:
    """Фабричная функция для создания экземпляра векторной БД"""
    if config.SUPABASE_URL:
        return SupabaseVectorDB()
    elif config.PINECONE_API_KEY:
        return PineconeVectorDB()
    else:
        raise ValueError("No vector database configuration found. Set either SUPABASE_URL or PINECONE_API_KEY")

# Глобальный экземпляр векторной БД
vector_db = get_vector_db()
