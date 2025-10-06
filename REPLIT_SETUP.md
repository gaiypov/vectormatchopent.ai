# 🚀 Настройка Pacific.ai Vector Matching в Replit

## 📋 Что нужно сделать

### 1. Создайте новый Repl
- Зайдите на [replit.com](https://replit.com)
- Нажмите "Create Repl"
- Выберите "Python" как язык
- Назовите его "pacific-ai-vector-matching"

### 2. Загрузите файлы
Скопируйте следующие файлы в Replit:

#### Backend файлы:
```
backend/
├── vector_matching/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── models.py
│   ├── embeddings.py
│   ├── vector_db.py
│   ├── matcher.py
│   └── explain.py
├── requirements.txt
├── env.example
├── run_server.py
└── example_usage.py
```

#### Конфигурационные файлы:
```
.replit
replit.nix
```

### 3. Настройте переменные окружения
В Replit:
1. Нажмите на иконку "Secrets" (🔒) в левой панели
2. Добавьте следующие переменные:
   - `OPENAI_API_KEY` = ваш ключ OpenAI
   - `PINECONE_API_KEY` = ваш ключ Pinecone
   - `API_HOST` = 0.0.0.0
   - `API_PORT` = 8000
   - `API_DEBUG` = True

### 4. Установите зависимости
В консоли Replit выполните:
```bash
pip install -r backend/requirements.txt
```

### 5. Запустите сервер
```bash
python backend/run_server.py
```

## 🎯 Использование

### 1. Проверка работы
- Откройте вкладку "Webview"
- Перейдите по ссылке (обычно `https://your-repl-name.your-username.repl.co`)
- Добавьте `/health` для проверки состояния

### 2. API документация
- Добавьте `/docs` к URL для Swagger UI
- Добавьте `/redoc` для ReDoc

### 3. Тестирование
```bash
python backend/example_usage.py
```

## 🔧 Настройка для продакшна

### 1. Включите "Always On"
- В настройках Repl включите "Always On" для постоянной работы

### 2. Настройте домен
- В настройках Repl настройте кастомный домен (опционально)

### 3. Мониторинг
- Используйте встроенные логи Replit для мониторинга
- Настройте уведомления об ошибках

## 📚 API Эндпоинты

После запуска сервера будут доступны:

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/health` | Проверка состояния |
| `POST` | `/api/embeddings` | Создание embedding |
| `POST` | `/api/matches` | Поиск совпадений |
| `GET` | `/api/matches/{candidate_id}/{vacancy_id}` | Объяснение |
| `POST` | `/api/weights` | Обновление весов |
| `GET` | `/api/weights` | Получение весов |

## 🧪 Примеры использования

### Python клиент
```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Проверка здоровья
        response = await client.get("https://your-repl-url.repl.co/health")
        print(response.json())
        
        # Создание embedding
        response = await client.post(
            "https://your-repl-url.repl.co/api/embeddings",
            json={
                "entity_id": "test_candidate",
                "entity_type": "candidate",
                "text": "Python разработчик с опытом FastAPI",
                "category": "skills"
            }
        )
        print(response.json())

asyncio.run(test_api())
```

### cURL примеры
```bash
# Проверка здоровья
curl https://your-repl-url.repl.co/health

# Создание embedding
curl -X POST "https://your-repl-url.repl.co/api/embeddings" \
  -H "Content-Type: application/json" \
  -d '{
    "entity_id": "test_candidate",
    "entity_type": "candidate",
    "text": "Python разработчик",
    "category": "skills"
  }'
```

## 🔍 Отладка

### 1. Проверка логов
- Логи сервера отображаются в консоли Replit
- Проверьте наличие ошибок инициализации

### 2. Проверка переменных окружения
```python
import os
print("OPENAI_API_KEY:", "***" if os.getenv("OPENAI_API_KEY") else "Not set")
print("PINECONE_API_KEY:", "***" if os.getenv("PINECONE_API_KEY") else "Not set")
```

### 3. Тестирование компонентов
```python
# Тест конфигурации
from backend.vector_matching.config import config
print("Config loaded:", config.OPENAI_API_KEY is not None)
```

## 🚀 Готово!

Теперь у вас есть полнофункциональный модуль векторного мэтчинга, работающий в Replit!

**Следующие шаги:**
1. Настройте API ключи
2. Запустите сервер
3. Протестируйте API
4. Интегрируйте с вашими приложениями
5. Настройте мониторинг
