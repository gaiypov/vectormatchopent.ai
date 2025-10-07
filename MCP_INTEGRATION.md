# 🔗 MCP Integration для Pacific.ai Vector Matching

## Что такое MCP?

MCP (Model Context Protocol) - это стандарт для интеграции AI-ассистентов с внешними инструментами и сервисами. Наш MCP сервер позволяет использовать модуль векторного мэтчинга в различных AI-ассистентах.

## 🚀 Возможности MCP сервера

### Доступные инструменты:

1. **`create_embedding`** - Создание векторного представления
2. **`find_matches`** - Поиск совпадений между кандидатами и вакансиями
3. **`get_explanation`** - Получение объяснения совпадения
4. **`update_weights`** - Обновление весов мэтчинга
5. **`get_weights`** - Получение текущих весов
6. **`health_check`** - Проверка состояния сервиса
7. **`batch_create_embeddings`** - Батчевое создание embeddings

## 📋 Установка и настройка

### 1. Установка зависимостей

```bash
# Установка MCP зависимостей
pip install -r mcp_requirements.txt

# Установка зависимостей модуля векторного мэтчинга
pip install -r backend/requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопируйте и настройте переменные
cp backend/env.example .env

# Отредактируйте .env файл
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=pacific-ai-vectors
```

### 3. Запуск MCP сервера

```bash
# Прямой запуск
python mcp_server.py

# Или через скрипт
python run_mcp_server.py
```

## 🔧 Интеграция с AI-ассистентами

### Claude Desktop

1. **Откройте настройки Claude Desktop**
2. **Добавьте MCP сервер в конфигурацию:**

```json
{
  "mcpServers": {
    "pacific-ai-vector-matching": {
      "command": "python",
      "args": ["/path/to/vectormatchopent-ai/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your_key_here",
        "PINECONE_API_KEY": "your_key_here"
      }
    }
  }
}
```

### Cursor IDE

1. **Откройте настройки Cursor**
2. **Добавьте MCP конфигурацию:**

```json
{
  "mcpServers": {
    "pacific-ai-vector-matching": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/vectormatchopent-ai"
    }
  }
}
```

### Другие AI-ассистенты

MCP сервер совместим с любыми AI-ассистентами, поддерживающими MCP протокол.

## 🧪 Примеры использования

### Создание embedding

```python
# Через MCP инструмент
result = await mcp_client.call_tool("create_embedding", {
    "entity_id": "candidate_123",
    "entity_type": "candidate",
    "text": "Python разработчик с опытом FastAPI",
    "category": "skills",
    "metadata": {"experience": "5_years"}
})
```

### Поиск совпадений

```python
# Поиск совпадений для кандидата
matches = await mcp_client.call_tool("find_matches", {
    "candidate_id": "candidate_123",
    "top_k": 5,
    "min_score": 0.7,
    "weights": {
        "skills": 0.5,
        "career": 0.3,
        "culture": 0.15,
        "salary": 0.05
    }
})
```

### Получение объяснения

```python
# Объяснение совпадения
explanation = await mcp_client.call_tool("get_explanation", {
    "candidate_id": "candidate_123",
    "vacancy_id": "vacancy_456"
})
```

### Батчевое создание embeddings

```python
# Создание нескольких embeddings
embeddings = await mcp_client.call_tool("batch_create_embeddings", {
    "embeddings": [
        {
            "entity_id": "candidate_123",
            "entity_type": "candidate",
            "text": "Python, FastAPI, PostgreSQL",
            "category": "skills"
        },
        {
            "entity_id": "candidate_123",
            "entity_type": "candidate",
            "text": "Стремлюсь к росту в ML",
            "category": "career"
        }
    ]
})
```

## 🔍 Мониторинг и отладка

### Проверка состояния

```python
# Проверка здоровья сервиса
health = await mcp_client.call_tool("health_check", {})
print(health)
```

### Логирование

MCP сервер выводит подробные логи:
- Инициализация модулей
- Выполнение инструментов
- Ошибки и предупреждения

## 🚀 Деплой в Replit

### 1. Загрузите проект в Replit

```bash
# Клонируйте репозиторий
git clone https://github.com/gaiypov/vectormatchopent.ai.git
```

### 2. Установите зависимости

```bash
pip install -r mcp_requirements.txt
pip install -r backend/requirements.txt
```

### 3. Настройте переменные окружения

В Replit добавьте в Secrets:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `PINECONE_INDEX_NAME`

### 4. Запустите MCP сервер

```bash
python mcp_server.py
```

## 📚 API Reference

### create_embedding

**Описание:** Создает векторное представление для текста

**Параметры:**
- `entity_id` (string) - Уникальный ID сущности
- `entity_type` (string) - Тип: "candidate" или "vacancy"
- `text` (string) - Текст для embedding
- `category` (string) - Категория: "skills", "career", "culture", "salary"
- `metadata` (object, optional) - Дополнительные метаданные

**Возвращает:** Объект с информацией о созданном embedding

### find_matches

**Описание:** Находит совпадения между кандидатом и вакансиями

**Параметры:**
- `candidate_id` (string) - ID кандидата
- `vacancy_ids` (array, optional) - Список ID вакансий
- `top_k` (integer, optional) - Количество результатов (по умолчанию 5)
- `min_score` (number, optional) - Минимальный балл (по умолчанию 0.3)
- `weights` (object, optional) - Веса для категорий

**Возвращает:** Список совпадений с баллами

### get_explanation

**Описание:** Получает объяснение совпадения

**Параметры:**
- `candidate_id` (string) - ID кандидата
- `vacancy_id` (string) - ID вакансии

**Возвращает:** Объяснение совпадения с ключевыми факторами

## 🔒 Безопасность

- **API ключи** передаются через переменные окружения
- **Валидация** всех входных параметров
- **Логирование** без чувствительных данных
- **CORS** настройки для безопасности

## 🆘 Поддержка

- **GitHub Issues**: https://github.com/gaiypov/vectormatchopent.ai/issues
- **Документация**: README.md
- **Примеры**: backend/example_usage.py

---

**Создано для Pacific.ai** 🚀
