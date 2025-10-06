# 🚀 Pacific.ai Vector Matching Module

Полнофункциональный модуль векторного мэтчинга для Pacific.ai с использованием OpenAI Embeddings и Pinecone Vector Database.

## ✨ Возможности

- **🧠 AI Embeddings** с помощью OpenAI text-embedding-3-large
- **🔍 Векторный поиск** в Pinecone или Supabase Vector
- **🎯 Умный мэтчинг** по 4 категориям: навыки, карьера, культура, зарплата
- **💡 Объяснения совпадений** с помощью GPT-4
- **🚀 REST API** на FastAPI с CORS для Next.js
- **⚡ Готов к деплою** в Replit

## 🏗 Архитектура

```
backend/
├── vector_matching/          # Основной модуль
│   ├── __init__.py
│   ├── api.py               # FastAPI сервер
│   ├── config.py            # Конфигурация
│   ├── models.py            # Pydantic модели
│   ├── embeddings.py        # OpenAI embeddings
│   ├── vector_db.py         # Векторная БД
│   ├── matcher.py           # Логика мэтчинга
│   └── explain.py           # GPT объяснения
├── requirements.txt         # Python зависимости
├── env.example             # Пример конфигурации
├── run_server.py           # Скрипт запуска
└── example_usage.py        # Примеры использования
```

## 🚀 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r backend/requirements.txt
```

### 2. Настройка переменных окружения
```bash
cp backend/env.example .env
# Отредактируйте .env файл с вашими API ключами
```

### 3. Запуск сервера
```bash
python backend/run_server.py
```

Сервер будет доступен по адресу: `http://localhost:8001`

## 🔧 API Эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/health` | Проверка состояния сервиса |
| `POST` | `/api/embeddings` | Создание embedding |
| `POST` | `/api/embeddings/batch` | Батчевое создание embeddings |
| `POST` | `/api/matches` | Поиск совпадений |
| `GET` | `/api/matches/{candidate_id}/{vacancy_id}` | Объяснение совпадения |
| `POST` | `/api/weights` | Обновление весов мэтчинга |
| `GET` | `/api/weights` | Получение текущих весов |

## 🧮 Формула мэтчинга

```python
score = (
    w1 * cosine(skills_vector_a, skills_vector_b) +
    w2 * cosine(career_vector_a, career_vector_b) +
    w3 * cosine(culture_vector_a, culture_vector_b) +
    w4 * cosine(salary_vector_a, salary_vector_b)
)
```

**Веса по умолчанию:**
- Навыки: 40%
- Карьера: 30%
- Культура: 20%
- Зарплата: 10%

## 🧪 Примеры использования

### Python клиент
```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Создание embedding
        response = await client.post(
            "http://localhost:8001/api/embeddings",
            json={
                "entity_id": "candidate_123",
                "entity_type": "candidate",
                "text": "Python разработчик с опытом FastAPI",
                "category": "skills"
            }
        )
        print(response.json())

        # Поиск совпадений
        response = await client.post(
            "http://localhost:8001/api/matches",
            json={
                "candidate_id": "candidate_123",
                "top_k": 5
            }
        )
        print(response.json())

asyncio.run(main())
```

### cURL примеры
```bash
# Проверка здоровья
curl http://localhost:8001/health

# Создание embedding
curl -X POST "http://localhost:8001/api/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "test_candidate",
    "entity_type": "candidate",
    "text": "Python разработчик",
    "category": "skills"
  }'
```

## 🚀 Деплой в Replit

### Способ 1: Импорт из GitHub
1. Зайдите на [replit.com](https://replit.com)
2. Нажмите "Import from GitHub"
3. Вставьте URL этого репозитория
4. Replit автоматически клонирует проект

### Способ 2: Прямая загрузка
1. Создайте новый Python Repl
2. Загрузите файлы из этого репозитория
3. Следуйте инструкциям в `REPLIT_SETUP.md`

### Настройка в Replit
1. Установите зависимости: `pip install -r backend/requirements.txt`
2. Настройте Secrets:
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `API_HOST` = 0.0.0.0
   - `API_PORT` = 8000
   - `API_DEBUG` = True
3. Запустите сервер: `python backend/run_server.py`

## 📚 Документация

- **API Docs**: http://localhost:8001/docs
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Подробная инструкция**: `REPLIT_SETUP.md`
- **Быстрый старт**: `REPLIT_QUICK_START.md`

## 🔒 Безопасность

- **CORS** настроен для Next.js доменов
- **API ключи** в переменных окружения
- **Валидация** всех входных данных
- **Логирование** без PII данных

## 🧪 Тестирование

```bash
# Запуск примера использования
python backend/example_usage.py

# Проверка здоровья сервиса
curl http://localhost:8001/health

# API документация
open http://localhost:8001/docs
```

## 📊 Мониторинг

- **Health check**: `GET /health`
- **Логирование**: Структурированные логи
- **Метрики**: Время выполнения запросов, количество совпадений

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License

## 🆘 Поддержка

- Создайте Issue для багов и feature requests
- Email: support@pacific.ai

---

**Создано для Pacific.ai** 🚀
