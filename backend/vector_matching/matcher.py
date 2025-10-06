"""
Модуль для мэтчинга и ранжирования кандидатов и вакансий
"""

import logging
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import asyncio

from .models import (
    MatchRequest, MatchResponse, MatchResult, MatchWeights, 
    CategoryType, EntityType, CandidateProfile, VacancyProfile
)
from .embeddings import embedding_generator
from .vector_db import vector_db
from .config import config

# Настройка логирования
logger = logging.getLogger(__name__)

class VectorMatcher:
    """Класс для мэтчинга кандидатов и вакансий"""
    
    def __init__(self):
        """Инициализация матчера"""
        self.weights = MatchWeights(**config.DEFAULT_WEIGHTS)
        self.initialized = False
    
    async def initialize(self):
        """Инициализация векторной БД"""
        try:
            await vector_db.initialize()
            self.initialized = True
            logger.info("VectorMatcher initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing VectorMatcher: {str(e)}")
            raise Exception(f"Failed to initialize VectorMatcher: {str(e)}")
    
    async def find_matches(self, request: MatchRequest) -> MatchResponse:
        """
        Находит совпадения для кандидата с вакансиями
        
        Args:
            request: Запрос на поиск совпадений
            
        Returns:
            MatchResponse: Результаты мэтчинга
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                await self.initialize()
            
            # Получаем профиль кандидата
            candidate_profile = await self._get_candidate_profile(request.candidate_id)
            if not candidate_profile:
                raise ValueError(f"Candidate {request.candidate_id} not found")
            
            # Определяем веса для мэтчинга
            weights = request.weights or self.weights
            
            # Получаем список вакансий для поиска
            vacancy_ids = request.vacancy_ids
            if not vacancy_ids:
                # Если не указаны конкретные вакансии, ищем по всем
                vacancy_ids = await self._get_all_vacancy_ids()
            
            # Выполняем мэтчинг для каждой вакансии
            matches = []
            for vacancy_id in vacancy_ids:
                try:
                    match_result = await self._match_candidate_vacancy(
                        candidate_profile, vacancy_id, weights
                    )
                    if match_result and match_result.match_score >= request.min_score:
                        matches.append(match_result)
                except Exception as e:
                    logger.warning(f"Error matching candidate {request.candidate_id} with vacancy {vacancy_id}: {str(e)}")
                    continue
            
            # Сортируем по убыванию score и берем топ-K
            matches.sort(key=lambda x: x.match_score, reverse=True)
            top_matches = matches[:request.top_k]
            
            search_time = (time.time() - start_time) * 1000  # в миллисекундах
            
            logger.info(f"Found {len(top_matches)} matches for candidate {request.candidate_id} in {search_time:.2f}ms")
            
            return MatchResponse(
                candidate_id=request.candidate_id,
                matches=top_matches,
                total_found=len(matches),
                search_time_ms=search_time,
                weights_used=weights
            )
            
        except Exception as e:
            logger.error(f"Error finding matches: {str(e)}")
            raise Exception(f"Failed to find matches: {str(e)}")
    
    async def _get_candidate_profile(self, candidate_id: str) -> Optional[CandidateProfile]:
        """
        Получает профиль кандидата со всеми векторами
        
        Args:
            candidate_id: ID кандидата
            
        Returns:
            CandidateProfile: Профиль кандидата или None
        """
        try:
            # Получаем все векторы кандидата
            vectors = await vector_db.get_vectors_by_entity(candidate_id, EntityType.CANDIDATE)
            
            if not vectors:
                return None
            
            # Группируем векторы по категориям
            vectors_by_category = {}
            metadata = {}
            
            for category, vector_record in vectors.items():
                vectors_by_category[category] = vector_record.vector
                metadata.update(vector_record.metadata)
            
            return CandidateProfile(
                candidate_id=candidate_id,
                vectors=vectors_by_category,
                metadata=metadata,
                created_at=vectors[list(vectors.keys())[0]].created_at
            )
            
        except Exception as e:
            logger.error(f"Error getting candidate profile: {str(e)}")
            return None
    
    async def _get_all_vacancy_ids(self) -> List[str]:
        """
        Получает список всех ID вакансий
        
        Returns:
            List[str]: Список ID вакансий
        """
        try:
            # Это упрощенная реализация - в реальности нужно будет
            # добавить метод в vector_db для получения всех entity_id по типу
            # Пока возвращаем пустой список - в реальном приложении
            # это должно быть реализовано через отдельную таблицу метаданных
            return []
        except Exception as e:
            logger.error(f"Error getting vacancy IDs: {str(e)}")
            return []
    
    async def _match_candidate_vacancy(
        self, 
        candidate_profile: CandidateProfile, 
        vacancy_id: str, 
        weights: MatchWeights
    ) -> Optional[MatchResult]:
        """
        Выполняет мэтчинг кандидата с конкретной вакансией
        
        Args:
            candidate_profile: Профиль кандидата
            vacancy_id: ID вакансии
            weights: Веса для мэтчинга
            
        Returns:
            MatchResult: Результат мэтчинга или None
        """
        try:
            # Получаем профиль вакансии
            vacancy_vectors = await vector_db.get_vectors_by_entity(vacancy_id, EntityType.VACANCY)
            if not vacancy_vectors:
                return None
            
            # Вычисляем scores по категориям
            category_scores = {}
            total_score = 0.0
            
            for category in CategoryType:
                candidate_vector = candidate_profile.vectors.get(category)
                vacancy_vector = vacancy_vectors.get(category)
                
                if not candidate_vector or not vacancy_vector:
                    category_scores[category] = 0.0
                    continue
                
                # Вычисляем cosine similarity
                similarity = embedding_generator.calculate_cosine_similarity(
                    candidate_vector, vacancy_vector.vector
                )
                
                category_scores[category] = similarity
                
                # Добавляем к общему score с учетом веса
                weight = getattr(weights, category.value)
                total_score += weight * similarity
            
            # Нормализуем общий score
            normalized_score = min(max(total_score, 0.0), 1.0)
            
            # Получаем метаданные вакансии
            vacancy_metadata = {}
            if vacancy_vectors:
                vacancy_metadata = list(vacancy_vectors.values())[0].metadata
            
            return MatchResult(
                vacancy_id=vacancy_id,
                match_score=normalized_score,
                category_scores=category_scores,
                metadata=vacancy_metadata
            )
            
        except Exception as e:
            logger.error(f"Error matching candidate with vacancy {vacancy_id}: {str(e)}")
            return None
    
    async def update_weights(self, new_weights: MatchWeights) -> bool:
        """
        Обновляет веса для мэтчинга
        
        Args:
            new_weights: Новые веса
            
        Returns:
            bool: Успешность обновления
        """
        try:
            self.weights = new_weights
            logger.info(f"Updated matching weights: {new_weights.dict()}")
            return True
        except Exception as e:
            logger.error(f"Error updating weights: {str(e)}")
            return False
    
    async def get_current_weights(self) -> MatchWeights:
        """
        Получает текущие веса мэтчинга
        
        Returns:
            MatchWeights: Текущие веса
        """
        return self.weights
    
    def calculate_weighted_score(
        self, 
        category_scores: Dict[CategoryType, float], 
        weights: MatchWeights
    ) -> float:
        """
        Вычисляет взвешенный score на основе scores по категориям
        
        Args:
            category_scores: Scores по категориям
            weights: Веса для категорий
            
        Returns:
            float: Взвешенный score
        """
        total_score = 0.0
        
        for category in CategoryType:
            score = category_scores.get(category, 0.0)
            weight = getattr(weights, category.value)
            total_score += weight * score
        
        return min(max(total_score, 0.0), 1.0)
    
    async def batch_match_candidates(
        self, 
        candidate_ids: List[str], 
        vacancy_ids: List[str],
        weights: Optional[MatchWeights] = None
    ) -> Dict[str, List[MatchResult]]:
        """
        Выполняет мэтчинг для нескольких кандидатов с несколькими вакансиями
        
        Args:
            candidate_ids: Список ID кандидатов
            vacancy_ids: Список ID вакансий
            weights: Веса для мэтчинга
            
        Returns:
            Dict[str, List[MatchResult]]: Результаты мэтчинга по кандидатам
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            weights = weights or self.weights
            results = {}
            
            # Выполняем мэтчинг параллельно для всех кандидатов
            tasks = []
            for candidate_id in candidate_ids:
                task = self._batch_match_single_candidate(candidate_id, vacancy_ids, weights)
                tasks.append(task)
            
            # Ждем завершения всех задач
            candidate_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for i, candidate_id in enumerate(candidate_ids):
                result = candidate_results[i]
                if isinstance(result, Exception):
                    logger.error(f"Error in batch match for candidate {candidate_id}: {str(result)}")
                    results[candidate_id] = []
                else:
                    results[candidate_id] = result
            
            logger.info(f"Completed batch matching for {len(candidate_ids)} candidates")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch matching: {str(e)}")
            raise Exception(f"Failed batch matching: {str(e)}")
    
    async def _batch_match_single_candidate(
        self, 
        candidate_id: str, 
        vacancy_ids: List[str], 
        weights: MatchWeights
    ) -> List[MatchResult]:
        """
        Выполняет мэтчинг для одного кандидата с несколькими вакансиями
        
        Args:
            candidate_id: ID кандидата
            vacancy_ids: Список ID вакансий
            weights: Веса для мэтчинга
            
        Returns:
            List[MatchResult]: Результаты мэтчинга
        """
        try:
            # Получаем профиль кандидата
            candidate_profile = await self._get_candidate_profile(candidate_id)
            if not candidate_profile:
                return []
            
            # Выполняем мэтчинг с каждой вакансией
            matches = []
            for vacancy_id in vacancy_ids:
                match_result = await self._match_candidate_vacancy(
                    candidate_profile, vacancy_id, weights
                )
                if match_result:
                    matches.append(match_result)
            
            # Сортируем по убыванию score
            matches.sort(key=lambda x: x.match_score, reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Error in single candidate batch match: {str(e)}")
            return []

# Глобальный экземпляр матчера
vector_matcher = VectorMatcher()
