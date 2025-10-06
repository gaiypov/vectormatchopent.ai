"""
Модуль для генерации embeddings с использованием OpenAI API
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
import openai
from openai import AsyncOpenAI
import numpy as np
from .config import config
from .models import CategoryType, EntityType

# Настройка логирования
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Класс для генерации embeddings с помощью OpenAI API"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_EMBEDDING_MODEL
        self.dimensions = config.OPENAI_EMBEDDING_DIMENSIONS
        
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Генерирует embedding для одного текста
        
        Args:
            text: Текст для векторизации
            
        Returns:
            List[float]: Вектор embedding
            
        Raises:
            Exception: При ошибке API OpenAI
        """
        try:
            # Очищаем и подготавливаем текст
            cleaned_text = self._preprocess_text(text)
            
            # Генерируем embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=cleaned_text,
                dimensions=self.dimensions
            )
            
            embedding = response.data[0].embedding
            
            # Нормализуем вектор для cosine similarity
            normalized_embedding = self._normalize_vector(embedding)
            
            logger.info(f"Generated embedding for text length: {len(cleaned_text)}")
            return normalized_embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Генерирует embeddings для списка текстов
        
        Args:
            texts: Список текстов для векторизации
            
        Returns:
            List[List[float]]: Список векторов embeddings
        """
        try:
            # Очищаем тексты
            cleaned_texts = [self._preprocess_text(text) for text in texts]
            
            # Генерируем embeddings батчами (OpenAI поддерживает до 2048 текстов за раз)
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(cleaned_texts), batch_size):
                batch_texts = cleaned_texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch_texts,
                    dimensions=self.dimensions
                )
                
                batch_embeddings = [self._normalize_vector(data.embedding) for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Небольшая задержка между батчами
                await asyncio.sleep(0.1)
            
            logger.info(f"Generated {len(all_embeddings)} embeddings in batch")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")
    
    async def generate_category_embeddings(
        self, 
        text: str, 
        categories: List[CategoryType]
    ) -> Dict[CategoryType, List[float]]:
        """
        Генерирует embeddings для текста в разных категориях
        
        Args:
            text: Исходный текст
            categories: Список категорий для генерации
            
        Returns:
            Dict[CategoryType, List[float]]: Словарь категория -> embedding
        """
        try:
            # Создаем промпты для разных категорий
            category_prompts = self._create_category_prompts(text, categories)
            
            # Генерируем embeddings для каждой категории
            embeddings = {}
            for category, prompt in category_prompts.items():
                embedding = await self.generate_embedding(prompt)
                embeddings[category] = embedding
            
            logger.info(f"Generated embeddings for categories: {list(categories)}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating category embeddings: {str(e)}")
            raise Exception(f"Failed to generate category embeddings: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """
        Предобработка текста перед векторизацией
        
        Args:
            text: Исходный текст
            
        Returns:
            str: Обработанный текст
        """
        # Удаляем лишние пробелы и переносы строк
        cleaned = " ".join(text.split())
        
        # Ограничиваем длину (OpenAI имеет лимит на токены)
        max_length = 8000  # Примерно 8000 символов
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """
        Нормализует вектор для cosine similarity
        
        Args:
            vector: Исходный вектор
            
        Returns:
            List[float]: Нормализованный вектор
        """
        vector_array = np.array(vector)
        norm = np.linalg.norm(vector_array)
        
        if norm == 0:
            return vector
        
        return (vector_array / norm).tolist()
    
    def _create_category_prompts(self, text: str, categories: List[CategoryType]) -> Dict[CategoryType, str]:
        """
        Создает промпты для разных категорий векторизации
        
        Args:
            text: Исходный текст
            categories: Список категорий
            
        Returns:
            Dict[CategoryType, str]: Словарь категория -> промпт
        """
        prompts = {}
        
        for category in categories:
            if category == CategoryType.SKILLS:
                prompts[category] = f"""
                Навыки и технические компетенции: {text}
                
                Извлеки и опиши только технические навыки, инструменты, технологии, 
                языки программирования, фреймворки, методологии разработки.
                """
                
            elif category == CategoryType.CAREER:
                prompts[category] = f"""
                Карьерные цели и опыт: {text}
                
                Извлеки и опиши карьерные амбиции, профессиональный опыт, 
                достижения, мотивацию к развитию, планы на будущее.
                """
                
            elif category == CategoryType.CULTURE:
                prompts[category] = f"""
                Культурные ценности и предпочтения: {text}
                
                Извлеки и опиши ценности, стиль работы, предпочтения по команде, 
                подход к решению задач, коммуникационный стиль.
                """
                
            elif category == CategoryType.SALARY:
                prompts[category] = f"""
                Финансовые ожидания и условия: {text}
                
                Извлеки и опиши зарплатные ожидания, условия работы, 
                бенефиты, готовность к переезду, гибкость в условиях.
                """
        
        return prompts
    
    def calculate_cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """
        Вычисляет cosine similarity между двумя векторами
        
        Args:
            vector1: Первый вектор
            vector2: Второй вектор
            
        Returns:
            float: Значение cosine similarity от -1 до 1
        """
        try:
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            # Проверяем, что векторы имеют одинаковую размерность
            if len(v1) != len(v2):
                raise ValueError("Vectors must have the same dimension")
            
            # Вычисляем cosine similarity
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0

# Глобальный экземпляр генератора
embedding_generator = EmbeddingGenerator()
