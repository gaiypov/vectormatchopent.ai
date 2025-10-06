#!/usr/bin/env python3
"""
Пример использования Pacific.ai Vector Matching Module
"""

import asyncio
import httpx
import json
from typing import Dict, Any

# Конфигурация
API_BASE_URL = "http://localhost:8001"

async def create_embedding(client: httpx.AsyncClient, entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Создает embedding для сущности"""
    response = await client.post(f"{API_BASE_URL}/api/embeddings", json=entity_data)
    response.raise_for_status()
    return response.json()

async def find_matches(client: httpx.AsyncClient, candidate_id: str, top_k: int = 5) -> Dict[str, Any]:
    """Находит совпадения для кандидата"""
    request_data = {
        "candidate_id": candidate_id,
        "top_k": top_k,
        "min_score": 0.3
    }
    response = await client.post(f"{API_BASE_URL}/api/matches", json=request_data)
    response.raise_for_status()
    return response.json()

async def get_explanation(client: httpx.AsyncClient, candidate_id: str, vacancy_id: str) -> Dict[str, Any]:
    """Получает объяснение совпадения"""
    response = await client.get(f"{API_BASE_URL}/api/matches/{candidate_id}/{vacancy_id}")
    response.raise_for_status()
    return response.json()

async def update_weights(client: httpx.AsyncClient, weights: Dict[str, float]) -> Dict[str, Any]:
    """Обновляет веса мэтчинга"""
    request_data = {"weights": weights}
    response = await client.post(f"{API_BASE_URL}/api/weights", json=request_data)
    response.raise_for_status()
    return response.json()

async def main():
    """Основная функция с примерами использования"""
    print("🚀 Пример использования Pacific.ai Vector Matching Module")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Проверяем здоровье сервиса
            print("\n1. Проверка здоровья сервиса...")
            health_response = await client.get(f"{API_BASE_URL}/health")
            health_data = health_response.json()
            print(f"   Статус: {health_data['status']}")
            print(f"   Сервисы: {health_data['services']}")
            
            # 2. Создаем embeddings для кандидата
            print("\n2. Создание embeddings для кандидата...")
            
            candidate_embeddings = [
                {
                    "entity_id": "candidate_001",
                    "entity_type": "candidate",
                    "text": "Я Python разработчик с 5-летним опытом работы с FastAPI, Django, PostgreSQL, Docker. Участвовал в разработке микросервисной архитектуры.",
                    "category": "skills",
                    "metadata": {"experience_years": 5, "location": "Moscow"}
                },
                {
                    "entity_id": "candidate_001",
                    "entity_type": "candidate",
                    "text": "Стремлюсь к карьерному росту в области машинного обучения и AI. Хочу работать в инновационной компании с интересными проектами.",
                    "category": "career",
                    "metadata": {"career_goals": ["ML", "AI"], "motivation": "high"}
                },
                {
                    "entity_id": "candidate_001",
                    "entity_type": "candidate",
                    "text": "Предпочитаю agile-методологии, работу в команде, открытое общение. Готов к удаленной работе и гибкому графику.",
                    "category": "culture",
                    "metadata": {"work_style": "agile", "remote_ok": True}
                },
                {
                    "entity_id": "candidate_001",
                    "entity_type": "candidate",
                    "text": "Ожидаю зарплату от 200,000 до 300,000 рублей. Рассматриваю опционы, медицинскую страховку, обучение за счет компании.",
                    "category": "salary",
                    "metadata": {"salary_min": 200000, "salary_max": 300000, "benefits": ["options", "insurance", "training"]}
                }
            ]
            
            for embedding_data in candidate_embeddings:
                result = await create_embedding(client, embedding_data)
                print(f"   ✅ Создан embedding для {embedding_data['category']}: {result['vector_id']}")
            
            # 3. Создаем embeddings для вакансий
            print("\n3. Создание embeddings для вакансий...")
            
            vacancy_embeddings = [
                {
                    "entity_id": "vacancy_001",
                    "entity_type": "vacancy",
                    "text": "Ищем Senior Python разработчика для работы с FastAPI, PostgreSQL, микросервисами. Опыт работы с Docker, Kubernetes, Redis.",
                    "category": "skills",
                    "metadata": {"company": "TechCorp", "level": "Senior", "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Redis"]}
                },
                {
                    "entity_id": "vacancy_001",
                    "entity_type": "vacancy",
                    "text": "Возможность карьерного роста до Tech Lead, работа с современными технологиями, участие в архитектурных решениях.",
                    "category": "career",
                    "metadata": {"growth_opportunities": True, "tech_stack": "modern", "architecture": True}
                },
                {
                    "entity_id": "vacancy_001",
                    "entity_type": "vacancy",
                    "text": "Agile-команда, удаленная работа, гибкий график, открытая корпоративная культура, регулярные ретроспективы.",
                    "category": "culture",
                    "metadata": {"methodology": "agile", "remote": True, "flexible_hours": True, "culture": "open"}
                },
                {
                    "entity_id": "vacancy_001",
                    "entity_type": "vacancy",
                    "text": "Зарплата 250,000 - 350,000 рублей, опционы, ДМС, обучение, корпоративные мероприятия, современный офис.",
                    "category": "salary",
                    "metadata": {"salary_min": 250000, "salary_max": 350000, "benefits": ["options", "dms", "training", "events", "modern_office"]}
                }
            ]
            
            for embedding_data in vacancy_embeddings:
                result = await create_embedding(client, embedding_data)
                print(f"   ✅ Создан embedding для вакансии {embedding_data['entity_id']} ({embedding_data['category']}): {result['vector_id']}")
            
            # 4. Ищем совпадения
            print("\n4. Поиск совпадений...")
            matches = await find_matches(client, "candidate_001", top_k=3)
            print(f"   Найдено совпадений: {matches['total_found']}")
            print(f"   Время поиска: {matches['search_time_ms']:.2f}ms")
            print(f"   Использованные веса: {matches['weights_used']}")
            
            for i, match in enumerate(matches['matches'], 1):
                print(f"\n   🎯 Совпадение #{i}:")
                print(f"      Вакансия: {match['vacancy_id']}")
                print(f"      Общий балл: {match['match_score']:.3f}")
                print(f"      Баллы по категориям:")
                for category, score in match['category_scores'].items():
                    print(f"        - {category.value}: {score:.3f}")
                if match.get('metadata'):
                    print(f"      Метаданные: {match['metadata']}")
            
            # 5. Получаем объяснения для топ совпадений
            if matches['matches']:
                print("\n5. Объяснения совпадений...")
                for i, match in enumerate(matches['matches'][:2], 1):  # Только первые 2
                    print(f"\n   📝 Объяснение #{i} (кандидат candidate_001 -> вакансия {match['vacancy_id']}):")
                    try:
                        explanation = await get_explanation(client, "candidate_001", match['vacancy_id'])
                        print(f"      Объяснение: {explanation['explanation']}")
                        if explanation.get('key_factors'):
                            print(f"      Ключевые факторы: {', '.join(explanation['key_factors'])}")
                        if explanation.get('improvement_suggestions'):
                            print(f"      Предложения по улучшению:")
                            for suggestion in explanation['improvement_suggestions']:
                                print(f"        - {suggestion}")
                    except Exception as e:
                        print(f"      ❌ Ошибка получения объяснения: {e}")
            
            # 6. Обновляем веса мэтчинга
            print("\n6. Обновление весов мэтчинга...")
            new_weights = {
                "skills": 0.5,    # Увеличиваем важность навыков
                "career": 0.3,    # Оставляем карьеру
                "culture": 0.15,  # Уменьшаем культуру
                "salary": 0.05    # Уменьшаем зарплату
            }
            
            weights_result = await update_weights(client, new_weights)
            print(f"   ✅ Веса обновлены: {weights_result['updated_weights']}")
            
            # 7. Повторный поиск с новыми весами
            print("\n7. Повторный поиск с новыми весами...")
            matches_v2 = await find_matches(client, "candidate_001", top_k=3)
            print(f"   Найдено совпадений: {matches_v2['total_found']}")
            print(f"   Новые веса: {matches_v2['weights_used']}")
            
            for i, match in enumerate(matches_v2['matches'], 1):
                print(f"   🎯 Совпадение #{i}: {match['vacancy_id']} (балл: {match['match_score']:.3f})")
            
            print("\n🎉 Пример использования завершен успешно!")
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP ошибка: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"❌ Ошибка запроса: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    print("⚠️  Убедитесь, что сервер запущен на http://localhost:8001")
    print("   Запустите: python run_server.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершено пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)
