# Pacific.ai Vector Matching Module

Модуль векторного мэтчинга для Pacific.ai, интегрированный с Next.js фронтендом.

## 🚀 Возможности

- **AI Embeddings** с помощью OpenAI text-embedding-3-large
- **Векторный поиск** в Pinecone или Supabase Vector
- **Умный мэтчинг** по 4 категориям: навыки, карьера, культура, зарплата
- **Объяснения совпадений** с помощью GPT-4
- **REST API** на FastAPI с CORS для Next.js
- **React компоненты** для интеграции с фронтендом

## 📁 Структура проекта

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

## 🛠 Установка и запуск

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp env.example .env
# Отредактируйте .env файл с вашими API ключами
```

**Обязательные переменные:**
```env
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 3. Запуск сервера

```bash
python run_server.py
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

## 🎯 Примеры использования

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

### JavaScript/TypeScript (Next.js)

```typescript
import { vectorMatchingAPI } from '@/lib/vectorMatching';

// Создание embedding
const embedding = await vectorMatchingAPI.createEmbedding({
  entity_id: 'candidate_123',
  entity_type: 'candidate',
  text: 'Python разработчик с опытом FastAPI',
  category: 'skills'
});

// Поиск совпадений
const matches = await vectorMatchingAPI.findMatches({
  candidate_id: 'candidate_123',
  top_k: 5
});
```

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

## 🔗 Интеграция с Next.js

### 1. Настройка переменных окружения

В `.env.local`:
```env
NEXT_PUBLIC_VECTOR_API_URL=http://localhost:8001
```

### 2. Использование компонентов

```tsx
import CandidateProfileForm from '@/components/VectorMatching/CandidateProfileForm';
import MatchResults from '@/components/VectorMatching/MatchResults';

export default function MyPage() {
  const [candidateId, setCandidateId] = useState<string | null>(null);

  return (
    <div>
      <CandidateProfileForm onProfileCreated={setCandidateId} />
      <MatchResults candidateId={candidateId} />
    </div>
  );
}
```

### 3. Использование API клиента

```tsx
import { vectorMatchingAPI, vectorMatchingUtils } from '@/lib/vectorMatching';

// Создание профиля кандидата
const candidateProfile = vectorMatchingUtils.createCandidateProfile({
  skills: "Python, FastAPI, PostgreSQL",
  career: "Стремлюсь к росту в ML",
  culture: "Agile, удаленная работа",
  salary: "200,000 - 300,000 рублей"
});

const results = await vectorMatchingAPI.createBatchEmbeddings(candidateProfile);
```

## 🧪 Тестирование

```bash
# Запуск примера использования
python example_usage.py

# Проверка здоровья сервиса
curl http://localhost:8001/health

# API документация
open http://localhost:8001/docs
```

## 📊 Мониторинг

- **Health check**: `GET /health`
- **Логирование**: Структурированные логи
- **Метрики**: Время выполнения запросов, количество совпадений

## 🔒 Безопасность

- **CORS** настроен для Next.js доменов
- **API ключи** в переменных окружения
- **Валидация** всех входных данных
- **Логирование** без PII данных

## 🚀 Деплой

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY vector_matching/ ./vector_matching/
CMD ["python", "run_server.py"]
```

### Переменные окружения для продакшна

```env
API_HOST=0.0.0.0
API_PORT=8001
API_DEBUG=False
CORS_ORIGINS=["https://pacific.ai", "https://www.pacific.ai"]
```

## 📚 Документация

- **API Docs**: http://localhost:8001/docs
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

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
