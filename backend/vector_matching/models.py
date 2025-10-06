"""
Pydantic модели для API и валидации данных Pacific.ai
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class CategoryType(str, Enum):
    """Типы категорий для векторизации"""
    SKILLS = "skills"
    CAREER = "career"
    CULTURE = "culture"
    SALARY = "salary"

class EntityType(str, Enum):
    """Типы сущностей"""
    CANDIDATE = "candidate"
    VACANCY = "vacancy"

# ===== Модели для создания embeddings =====

class EmbeddingCreateRequest(BaseModel):
    """Запрос на создание embedding"""
    entity_id: str = Field(..., description="Уникальный ID сущности")
    entity_type: EntityType = Field(..., description="Тип сущности (candidate/vacancy)")
    text: str = Field(..., min_length=10, max_length=10000, description="Текст для векторизации")
    category: CategoryType = Field(..., description="Категория текста")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Дополнительные метаданные")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()

class EmbeddingResponse(BaseModel):
    """Ответ с созданным embedding"""
    entity_id: str
    entity_type: EntityType
    category: CategoryType
    vector_id: str
    created_at: datetime
    success: bool = True

# ===== Модели для мэтчинга =====

class MatchWeights(BaseModel):
    """Веса для различных категорий мэтчинга"""
    skills: float = Field(0.4, ge=0.0, le=1.0, description="Вес навыков")
    career: float = Field(0.3, ge=0.0, le=1.0, description="Вес карьеры")
    culture: float = Field(0.2, ge=0.0, le=1.0, description="Вес культуры")
    salary: float = Field(0.1, ge=0.0, le=1.0, description="Вес зарплаты")
    
    @validator('skills', 'career', 'culture', 'salary')
    def validate_weights(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Веса должны быть от 0 до 1')
        return v
    
    @validator('*', pre=True)
    def normalize_weights(cls, v, values):
        # Нормализуем веса так, чтобы их сумма была равна 1
        total = sum(values.values()) + v
        if total > 0:
            return v / total
        return v

class MatchRequest(BaseModel):
    """Запрос на поиск совпадений"""
    candidate_id: str = Field(..., description="ID кандидата")
    vacancy_ids: Optional[List[str]] = Field(None, description="Список ID вакансий для поиска (если не указан, ищем по всем)")
    top_k: int = Field(10, ge=1, le=100, description="Количество топ совпадений")
    weights: Optional[MatchWeights] = Field(None, description="Кастомные веса для мэтчинга")
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Минимальный порог схожести")

class MatchResult(BaseModel):
    """Результат одного совпадения"""
    vacancy_id: str
    match_score: float = Field(..., ge=0.0, le=1.0, description="Общий балл совпадения")
    category_scores: Dict[CategoryType, float] = Field(..., description="Баллы по категориям")
    explanation: Optional[str] = Field(None, description="Объяснение совпадения")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные вакансии")

class MatchResponse(BaseModel):
    """Ответ с результатами мэтчинга"""
    candidate_id: str
    matches: List[MatchResult]
    total_found: int
    search_time_ms: float
    weights_used: MatchWeights

# ===== Модели для объяснений =====

class ExplanationRequest(BaseModel):
    """Запрос на генерацию объяснения"""
    candidate_id: str
    vacancy_id: str
    match_score: float
    category_scores: Dict[CategoryType, float]

class ExplanationResponse(BaseModel):
    """Ответ с объяснением совпадения"""
    explanation: str
    key_factors: List[str]
    improvement_suggestions: Optional[List[str]] = None

# ===== Модели для обновления весов =====

class WeightsUpdateRequest(BaseModel):
    """Запрос на обновление весов мэтчинга"""
    weights: MatchWeights
    user_id: Optional[str] = Field(None, description="ID пользователя, обновившего веса")

class WeightsUpdateResponse(BaseModel):
    """Ответ об обновлении весов"""
    success: bool
    message: str
    updated_weights: MatchWeights
    updated_at: datetime

# ===== Модели для здоровья системы =====

class HealthResponse(BaseModel):
    """Ответ проверки здоровья системы"""
    status: str = Field(..., description="Статус системы (healthy/unhealthy)")
    timestamp: datetime
    services: Dict[str, str] = Field(..., description="Статус различных сервисов")
    version: str = Field(..., description="Версия модуля")

# ===== Модели для ошибок =====

class ErrorResponse(BaseModel):
    """Стандартный ответ об ошибке"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

# ===== Внутренние модели для работы с БД =====

class VectorRecord(BaseModel):
    """Запись в векторной БД"""
    id: str
    entity_id: str
    entity_type: EntityType
    category: CategoryType
    vector: List[float]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class CandidateProfile(BaseModel):
    """Профиль кандидата с векторами"""
    candidate_id: str
    vectors: Dict[CategoryType, List[float]]
    metadata: Dict[str, Any]
    created_at: datetime

class VacancyProfile(BaseModel):
    """Профиль вакансии с векторами"""
    vacancy_id: str
    vectors: Dict[CategoryType, List[float]]
    metadata: Dict[str, Any]
    created_at: datetime
