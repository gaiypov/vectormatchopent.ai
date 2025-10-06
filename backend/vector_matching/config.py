"""
Конфигурация модуля векторного мэтчинга для Pacific.ai
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Основные настройки приложения"""
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    OPENAI_EMBEDDING_DIMENSIONS = 3072
    
    # Pinecone Vector DB
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pacific-ai-vectors")
    
    # Supabase Vector (альтернатива Pinecone)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "embeddings")
    
    # PostgreSQL для метаданных
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/pacific_ai")
    
    # Настройки мэтчинга
    DEFAULT_TOP_K = 10
    DEFAULT_WEIGHTS = {
        "skills": 0.4,
        "career": 0.3,
        "culture": 0.2,
        "salary": 0.1
    }
    
    # Настройки API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8001"))  # Другой порт для Pacific.ai
    API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # CORS настройки для Next.js
    CORS_ORIGINS = [
        "http://localhost:3000",  # Next.js dev server
        "https://pacific.ai",     # Production domain
        "https://www.pacific.ai", # Production domain with www
    ]
    
    # Безопасность
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    @classmethod
    def validate_config(cls) -> bool:
        """Проверяет наличие обязательных конфигураций"""
        required_vars = [
            "OPENAI_API_KEY",
            "PINECONE_API_KEY" if not cls.SUPABASE_URL else "SUPABASE_URL"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
        
        return True

# Глобальный экземпляр конфигурации
config = Config()
