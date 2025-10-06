"""
FastAPI сервер для модуля векторного мэтчинга Pacific.ai
Интеграция с Next.js фронтендом
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import config
from .models import (
    EmbeddingCreateRequest, EmbeddingResponse, MatchRequest, MatchResponse,
    ExplanationRequest, ExplanationResponse, WeightsUpdateRequest, 
    WeightsUpdateResponse, HealthResponse, ErrorResponse
)
from .embeddings import embedding_generator
from .vector_db import vector_db
from .matcher import vector_matcher
from .explain import match_explainer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные для инициализации
app_initialized = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global app_initialized
    
    # Инициализация при запуске
    logger.info("Starting Pacific.ai Vector Matching Module...")
    
    try:
        # Валидируем конфигурацию
        config.validate_config()
        
        # Инициализируем компоненты
        await vector_db.initialize()
        await vector_matcher.initialize()
        
        app_initialized = True
        logger.info("Application initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise e
    
    # Очистка при завершении
    logger.info("Shutting down application...")

# Создание FastAPI приложения
app = FastAPI(
    title="Pacific.ai Vector Matching API",
    description="API для векторного мэтчинга кандидатов и вакансий",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS для Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ===== Middleware для логирования =====

@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware для логирования запросов"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

# ===== Обработчики ошибок =====

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Обработчик ошибок валидации"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Обработчик общих ошибок"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred"
        ).dict()
    )

# ===== Dependency для проверки инициализации =====

async def check_initialization():
    """Проверяет, что приложение инициализировано"""
    if not app_initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application is not initialized"
        )

# ===== Эндпоинты API =====

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Проверка состояния сервиса
    """
    try:
        services = {
            "vector_db": "healthy" if app_initialized else "unhealthy",
            "embedding_generator": "healthy",
            "matcher": "healthy" if app_initialized else "unhealthy",
            "explainer": "healthy"
        }
        
        overall_status = "healthy" if all(
            status == "healthy" for status in services.values()
        ) else "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services=services,
            version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            services={"error": str(e)},
            version="1.0.0"
        )

@app.post("/api/embeddings", response_model=EmbeddingResponse)
async def create_embedding(
    request: EmbeddingCreateRequest,
    _: None = Depends(check_initialization)
):
    """
    Создает embedding для текста кандидата или вакансии
    """
    try:
        # Генерируем embedding
        embedding_vector = await embedding_generator.generate_embedding(request.text)
        
        # Создаем запись для векторной БД
        vector_id = f"{request.entity_type.value}_{request.entity_id}_{request.category.value}_{int(time.time())}"
        
        from .models import VectorRecord
        vector_record = VectorRecord(
            id=vector_id,
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            category=request.category,
            vector=embedding_vector,
            metadata=request.metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Сохраняем в векторную БД
        success = await vector_db.upsert_vector(vector_record)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save embedding to vector database"
            )
        
        logger.info(f"Created embedding for {request.entity_type.value} {request.entity_id}")
        
        return EmbeddingResponse(
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            category=request.category,
            vector_id=vector_id,
            created_at=vector_record.created_at,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create embedding: {str(e)}"
        )

@app.post("/api/matches", response_model=MatchResponse)
async def find_matches(
    request: MatchRequest,
    _: None = Depends(check_initialization)
):
    """
    Находит топ-N совпадений кандидата с вакансиями
    """
    try:
        # Выполняем мэтчинг
        match_response = await vector_matcher.find_matches(request)
        
        logger.info(f"Found {len(match_response.matches)} matches for candidate {request.candidate_id}")
        
        return match_response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find matches: {str(e)}"
        )

@app.get("/api/matches/{candidate_id}/{vacancy_id}", response_model=ExplanationResponse)
async def get_match_explanation(
    candidate_id: str,
    vacancy_id: str,
    _: None = Depends(check_initialization)
):
    """
    Получает объяснение совпадения кандидата с вакансией
    """
    try:
        # Получаем профили кандидата и вакансии
        from .models import CandidateProfile, VacancyProfile, EntityType, CategoryType
        
        candidate_vectors = await vector_db.get_vectors_by_entity(candidate_id, EntityType.CANDIDATE)
        vacancy_vectors = await vector_db.get_vectors_by_entity(vacancy_id, EntityType.VACANCY)
        
        if not candidate_vectors or not vacancy_vectors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate or vacancy not found"
            )
        
        # Вычисляем scores по категориям
        category_scores = {}
        for category in CategoryType:
            candidate_vector = candidate_vectors.get(category)
            vacancy_vector = vacancy_vectors.get(category)
            
            if candidate_vector and vacancy_vector:
                similarity = embedding_generator.calculate_cosine_similarity(
                    candidate_vector.vector, vacancy_vector.vector
                )
                category_scores[category] = similarity
            else:
                category_scores[category] = 0.0
        
        # Вычисляем общий score
        weights = await vector_matcher.get_current_weights()
        total_score = vector_matcher.calculate_weighted_score(category_scores, weights)
        
        # Создаем запрос на объяснение
        explanation_request = ExplanationRequest(
            candidate_id=candidate_id,
            vacancy_id=vacancy_id,
            match_score=total_score,
            category_scores=category_scores
        )
        
        # Генерируем объяснение
        explanation = await match_explainer.generate_explanation(explanation_request)
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match explanation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match explanation: {str(e)}"
        )

@app.post("/api/weights", response_model=WeightsUpdateResponse)
async def update_weights(
    request: WeightsUpdateRequest,
    _: None = Depends(check_initialization)
):
    """
    Обновляет веса критериев мэтчинга
    """
    try:
        # Обновляем веса
        success = await vector_matcher.update_weights(request.weights)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update weights"
            )
        
        logger.info(f"Updated matching weights: {request.weights.dict()}")
        
        return WeightsUpdateResponse(
            success=True,
            message="Weights updated successfully",
            updated_weights=request.weights,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error updating weights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update weights: {str(e)}"
        )

@app.get("/api/weights", response_model=WeightsUpdateResponse)
async def get_weights(_: None = Depends(check_initialization)):
    """
    Получает текущие веса критериев мэтчинга
    """
    try:
        current_weights = await vector_matcher.get_current_weights()
        
        return WeightsUpdateResponse(
            success=True,
            message="Current weights retrieved successfully",
            updated_weights=current_weights,
            updated_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting weights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weights: {str(e)}"
        )

# ===== Дополнительные эндпоинты =====

@app.post("/api/embeddings/batch", response_model=List[EmbeddingResponse])
async def create_batch_embeddings(
    requests: List[EmbeddingCreateRequest],
    _: None = Depends(check_initialization)
):
    """
    Создает embeddings для нескольких текстов одновременно
    """
    try:
        if len(requests) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size cannot exceed 100"
            )
        
        responses = []
        
        for request in requests:
            try:
                # Генерируем embedding
                embedding_vector = await embedding_generator.generate_embedding(request.text)
                
                # Создаем запись
                vector_id = f"{request.entity_type.value}_{request.entity_id}_{request.category.value}_{int(time.time())}"
                
                from .models import VectorRecord
                vector_record = VectorRecord(
                    id=vector_id,
                    entity_id=request.entity_id,
                    entity_type=request.entity_type,
                    category=request.category,
                    vector=embedding_vector,
                    metadata=request.metadata or {},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # Сохраняем в БД
                success = await vector_db.upsert_vector(vector_record)
                
                if success:
                    responses.append(EmbeddingResponse(
                        entity_id=request.entity_id,
                        entity_type=request.entity_type,
                        category=request.category,
                        vector_id=vector_id,
                        created_at=vector_record.created_at,
                        success=True
                    ))
                else:
                    responses.append(EmbeddingResponse(
                        entity_id=request.entity_id,
                        entity_type=request.entity_type,
                        category=request.category,
                        vector_id="",
                        created_at=datetime.now(),
                        success=False
                    ))
                    
            except Exception as e:
                logger.error(f"Error processing batch request for {request.entity_id}: {str(e)}")
                responses.append(EmbeddingResponse(
                    entity_id=request.entity_id,
                    entity_type=request.entity_type,
                    category=request.category,
                    vector_id="",
                    created_at=datetime.now(),
                    success=False
                ))
        
        logger.info(f"Processed {len(requests)} batch embedding requests")
        return responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating batch embeddings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch embeddings: {str(e)}"
        )

# ===== Запуск сервера =====

if __name__ == "__main__":
    uvicorn.run(
        "backend.vector_matching.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_DEBUG,
        log_level="info"
    )
