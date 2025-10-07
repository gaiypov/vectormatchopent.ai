# 🚀 MCP Quick Start для Pacific.ai Vector Matching

## ✅ MCP Integration добавлена!

Ваш модуль векторного мэтчинга теперь поддерживает **MCP (Model Context Protocol)** для интеграции с AI-ассистентами!

## 🎯 Что добавлено

### MCP Сервер
- **`mcp_server.py`** - Полнофункциональный MCP сервер
- **7 инструментов** для работы с векторным мэтчингом
- **Поддержка** Claude Desktop, Cursor IDE, и других MCP-совместимых инструментов

### Конфигурация
- **`mcp_config.json`** - Готовая конфигурация MCP
- **`mcp_requirements.txt`** - Зависимости для MCP
- **`run_mcp_server.py`** - Скрипт запуска

### Документация
- **`MCP_INTEGRATION.md`** - Подробная документация
- **Обновленный README** с разделом MCP

## 🔧 Быстрая настройка

### 1. Установка MCP зависимостей

```bash
# В папке проекта
pip install -r mcp_requirements.txt
```

### 2. Настройка переменных окружения

```bash
# Скопируйте и настройте
cp backend/env.example .env

# Отредактируйте .env
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

## 🤖 Интеграция с AI-ассистентами

### Claude Desktop

1. **Откройте настройки Claude Desktop**
2. **Добавьте MCP сервер:**

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

## 🛠 Доступные MCP инструменты

| Инструмент | Описание |
|------------|----------|
| `create_embedding` | Создание векторного представления |
| `find_matches` | Поиск совпадений между кандидатами и вакансиями |
| `get_explanation` | Получение объяснения совпадения |
| `update_weights` | Обновление весов мэтчинга |
| `get_weights` | Получение текущих весов |
| `health_check` | Проверка состояния сервиса |
| `batch_create_embeddings` | Батчевое создание embeddings |

## 🧪 Примеры использования

### Создание embedding через MCP

```python
# В AI-ассистенте
result = await mcp_client.call_tool("create_embedding", {
    "entity_id": "candidate_123",
    "entity_type": "candidate",
    "text": "Python разработчик с опытом FastAPI",
    "category": "skills"
})
```

### Поиск совпадений

```python
matches = await mcp_client.call_tool("find_matches", {
    "candidate_id": "candidate_123",
    "top_k": 5,
    "min_score": 0.7
})
```

### Получение объяснения

```python
explanation = await mcp_client.call_tool("get_explanation", {
    "candidate_id": "candidate_123",
    "vacancy_id": "vacancy_456"
})
```

## 🚀 Деплой в Replit

### 1. Импортируйте проект в Replit

```bash
# Клонируйте репозиторий
git clone https://github.com/gaiypov/vectormatchopent.ai.git
```

### 2. Установите зависимости

```bash
# MCP зависимости
pip install -r mcp_requirements.txt

# Основные зависимости
pip install -r backend/requirements.txt
```

### 3. Настройте Secrets в Replit

- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `PINECONE_INDEX_NAME`

### 4. Запустите MCP сервер

```bash
python mcp_server.py
```

## 📚 Документация

- **Основная документация**: [MCP_INTEGRATION.md](MCP_INTEGRATION.md)
- **Обновленный README**: [README.md](README.md)
- **GitHub репозиторий**: https://github.com/gaiypov/vectormatchopent.ai.git

## 🎉 Готово!

Теперь у вас есть:

✅ **Полнофункциональный модуль** векторного мэтчинга  
✅ **REST API** для веб-приложений  
✅ **MCP сервер** для AI-ассистентов  
✅ **Готовый к деплою** проект для Replit  
✅ **Подробную документацию** и примеры  

**Следующие шаги:**
1. Настройте MCP в вашем AI-ассистенте
2. Протестируйте инструменты
3. Интегрируйте в ваши проекты
4. Деплойте в Replit

Удачи с вашим модулем векторного мэтчинга! 🚀
