"""
Модуль для генерации объяснений совпадений с использованием GPT
"""

import logging
from typing import List, Dict, Optional
import openai
from openai import AsyncOpenAI
import json

from .config import config
from .models import ExplanationRequest, ExplanationResponse, CategoryType

# Настройка логирования
logger = logging.getLogger(__name__)

class MatchExplainer:
    """Класс для генерации объяснений совпадений"""
    
    def __init__(self):
        """Инициализация клиента OpenAI"""
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = "gpt-4"  # Используем GPT-4 для качественных объяснений
    
    async def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Генерирует объяснение совпадения
        
        Args:
            request: Запрос на генерацию объяснения
            
        Returns:
            ExplanationResponse: Объяснение совпадения
        """
        try:
            # Создаем промпт для генерации объяснения
            prompt = self._create_explanation_prompt(request)
            
            # Генерируем объяснение с помощью GPT
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - эксперт по HR и подбору персонала. Твоя задача - объяснить, почему кандидат подходит для вакансии, основываясь на анализе различных категорий совпадений."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            explanation_text = response.choices[0].message.content.strip()
            
            # Извлекаем ключевые факторы и предложения по улучшению
            key_factors = self._extract_key_factors(request)
            improvement_suggestions = await self._generate_improvement_suggestions(request)
            
            logger.info(f"Generated explanation for match {request.candidate_id} -> {request.vacancy_id}")
            
            return ExplanationResponse(
                explanation=explanation_text,
                key_factors=key_factors,
                improvement_suggestions=improvement_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            # Возвращаем базовое объяснение в случае ошибки
            return self._create_fallback_explanation(request)
    
    def _create_explanation_prompt(self, request: ExplanationRequest) -> str:
        """
        Создает промпт для генерации объяснения
        
        Args:
            request: Запрос на объяснение
            
        Returns:
            str: Промпт для GPT
        """
        # Форматируем scores по категориям
        category_descriptions = {
            CategoryType.SKILLS: "Навыки и технические компетенции",
            CategoryType.CAREER: "Карьерные цели и опыт",
            CategoryType.CULTURE: "Культурные ценности и предпочтения",
            CategoryType.SALARY: "Финансовые ожидания и условия"
        }
        
        scores_text = "\n".join([
            f"- {category_descriptions[category]}: {score:.2f} ({self._score_to_quality(score)})"
            for category, score in request.category_scores.items()
        ])
        
        prompt = f"""
        Проанализируй совпадение кандидата и вакансии:
        
        Кандидат ID: {request.candidate_id}
        Вакансия ID: {request.vacancy_id}
        Общий балл совпадения: {request.match_score:.2f}
        
        Детальные баллы по категориям:
        {scores_text}
        
        Создай краткое и понятное объяснение (2-3 предложения), почему этот кандидат подходит для вакансии.
        Выдели основные сильные стороны совпадения и объясни, что делает его привлекательным.
        
        Объяснение должно быть:
        - Конкретным и информативным
        - Понятным для HR-менеджера
        - Сфокусированным на ключевых преимуществах
        - Профессиональным по тону
        """
        
        return prompt
    
    def _score_to_quality(self, score: float) -> str:
        """
        Преобразует числовой score в качественное описание
        
        Args:
            score: Числовой score от 0 до 1
            
        Returns:
            str: Качественное описание
        """
        if score >= 0.9:
            return "отличное совпадение"
        elif score >= 0.7:
            return "хорошее совпадение"
        elif score >= 0.5:
            return "умеренное совпадение"
        elif score >= 0.3:
            return "слабое совпадение"
        else:
            return "очень слабое совпадение"
    
    def _extract_key_factors(self, request: ExplanationRequest) -> List[str]:
        """
        Извлекает ключевые факторы совпадения
        
        Args:
            request: Запрос на объяснение
            
        Returns:
            List[str]: Список ключевых факторов
        """
        factors = []
        
        # Сортируем категории по убыванию score
        sorted_categories = sorted(
            request.category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Добавляем топ-3 фактора
        for category, score in sorted_categories[:3]:
            if score > 0.3:  # Только значимые совпадения
                factor_name = self._get_category_factor_name(category)
                factors.append(f"{factor_name} ({score:.2f})")
        
        return factors
    
    def _get_category_factor_name(self, category: CategoryType) -> str:
        """
        Возвращает название фактора для категории
        
        Args:
            category: Категория совпадения
            
        Returns:
            str: Название фактора
        """
        factor_names = {
            CategoryType.SKILLS: "Технические навыки",
            CategoryType.CAREER: "Карьерный опыт",
            CategoryType.CULTURE: "Культурное соответствие",
            CategoryType.SALARY: "Финансовые ожидания"
        }
        return factor_names.get(category, "Неизвестный фактор")
    
    async def _generate_improvement_suggestions(
        self, 
        request: ExplanationRequest
    ) -> Optional[List[str]]:
        """
        Генерирует предложения по улучшению совпадения
        
        Args:
            request: Запрос на объяснение
            
        Returns:
            List[str]: Список предложений по улучшению
        """
        try:
            # Находим категории с низкими scores
            low_score_categories = [
                category for category, score in request.category_scores.items()
                if score < 0.5
            ]
            
            if not low_score_categories:
                return None
            
            # Создаем промпт для предложений по улучшению
            prompt = self._create_improvement_prompt(low_score_categories)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Ты - HR-консультант. Дай конкретные и практичные советы по улучшению профиля кандидата."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            
            # Парсим предложения (предполагаем, что каждое предложение на новой строке)
            suggestions = [
                suggestion.strip() 
                for suggestion in suggestions_text.split('\n') 
                if suggestion.strip() and suggestion.strip().startswith(('-', '•', '1.', '2.', '3.'))
            ]
            
            return suggestions[:5]  # Ограничиваем 5 предложениями
            
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {str(e)}")
            return None
    
    def _create_improvement_prompt(self, low_score_categories: List[CategoryType]) -> str:
        """
        Создает промпт для генерации предложений по улучшению
        
        Args:
            low_score_categories: Категории с низкими scores
            
        Returns:
            str: Промпт для GPT
        """
        category_names = {
            CategoryType.SKILLS: "навыки и технические компетенции",
            CategoryType.CAREER: "карьерный опыт и достижения",
            CategoryType.CULTURE: "культурные ценности и стиль работы",
            CategoryType.SALARY: "финансовые ожидания и условия"
        }
        
        weak_areas = [category_names[cat] for cat in low_score_categories]
        
        prompt = f"""
        Кандидат имеет слабые показатели в следующих областях:
        {', '.join(weak_areas)}
        
        Дай 3-5 конкретных и практичных советов, как кандидат может улучшить свой профиль в этих областях.
        Советы должны быть:
        - Конкретными и выполнимыми
        - Релевантными для IT-сферы
        - Краткими (1-2 предложения каждое)
        
        Формат: каждый совет с новой строки, начинающийся с "-"
        """
        
        return prompt
    
    def _create_fallback_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Создает базовое объяснение в случае ошибки
        
        Args:
            request: Запрос на объяснение
            
        Returns:
            ExplanationResponse: Базовое объяснение
        """
        # Находим лучшую категорию
        best_category = max(request.category_scores.items(), key=lambda x: x[1])
        best_score = best_category[1]
        
        if best_score > 0.7:
            quality = "хорошее"
        elif best_score > 0.5:
            quality = "умеренное"
        else:
            quality = "базовое"
        
        explanation = f"Кандидат демонстрирует {quality} совпадение с вакансией (общий балл: {request.match_score:.2f}). "
        
        if best_category[0] == CategoryType.SKILLS:
            explanation += "Наибольшее совпадение наблюдается в технических навыках."
        elif best_category[0] == CategoryType.CAREER:
            explanation += "Наибольшее совпадение наблюдается в карьерном опыте."
        elif best_category[0] == CategoryType.CULTURE:
            explanation += "Наибольшее совпадение наблюдается в культурных ценностях."
        else:
            explanation += "Наибольшее совпадение наблюдается в финансовых ожиданиях."
        
        return ExplanationResponse(
            explanation=explanation,
            key_factors=[f"Общий балл: {request.match_score:.2f}"],
            improvement_suggestions=None
        )
    
    async def generate_batch_explanations(
        self, 
        requests: List[ExplanationRequest]
    ) -> List[ExplanationResponse]:
        """
        Генерирует объяснения для нескольких совпадений
        
        Args:
            requests: Список запросов на объяснение
            
        Returns:
            List[ExplanationResponse]: Список объяснений
        """
        try:
            # Генерируем объяснения параллельно
            tasks = [self.generate_explanation(request) for request in requests]
            explanations = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            results = []
            for i, explanation in enumerate(explanations):
                if isinstance(explanation, Exception):
                    logger.error(f"Error generating explanation {i}: {str(explanation)}")
                    results.append(self._create_fallback_explanation(requests[i]))
                else:
                    results.append(explanation)
            
            logger.info(f"Generated {len(results)} explanations in batch")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch explanation generation: {str(e)}")
            # Возвращаем fallback объяснения для всех запросов
            return [self._create_fallback_explanation(req) for req in requests]

# Глобальный экземпляр объяснителя
match_explainer = MatchExplainer()
