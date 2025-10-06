# 🚀 Быстрый старт в Replit

## ✅ Архив готов!

Создан файл: `pacific-ai-vector-matching-replit.zip`

## 📋 Пошаговая инструкция

### 1. Создайте новый Repl
- Зайдите на [replit.com](https://replit.com)
- Нажмите "Create Repl"
- Выберите "Python" как язык
- Назовите его "pacific-ai-vector-matching"

### 2. Загрузите архив
- В Replit нажмите на иконку "Files" (📁)
- Нажмите "Upload" 
- Загрузите файл `pacific-ai-vector-matching-replit.zip`
- Распакуйте архив (нажмите на ZIP файл)

### 3. Настройте Secrets
В Replit добавьте в Secrets (🔒):
```
OPENAI_API_KEY = ваш_ключ_openai
PINECONE_API_KEY = ваш_ключ_pinecone
API_HOST = 0.0.0.0
API_PORT = 8000
API_DEBUG = True
```

### 4. Установите зависимости
В консоли Replit:
```bash
pip install -r backend/requirements.txt
```

### 5. Запустите сервер
```bash
python backend/run_server.py
```

### 6. Проверьте работу
- Откройте вкладку "Webview"
- Перейдите по ссылке
- Добавьте `/health` для проверки состояния
- Добавьте `/docs` для API документации

## 🧪 Тестирование

```bash
# Запустите пример
python backend/example_usage.py

# Или проверьте API
curl https://your-repl-url.repl.co/health
```

## 🎯 API Эндпоинты

После запуска будут доступны:
- `GET /health` - Проверка состояния
- `POST /api/embeddings` - Создание embedding
- `POST /api/matches` - Поиск совпадений
- `GET /api/matches/{candidate_id}/{vacancy_id}` - Объяснение
- `POST /api/weights` - Обновление весов
- `GET /api/weights` - Получение весов

## 📚 Документация

- **API Docs**: `https://your-repl-url.repl.co/docs`
- **Swagger UI**: `https://your-repl-url.repl.co/docs`
- **ReDoc**: `https://your-repl-url.repl.co/redoc`

## 🔧 Настройка для продакшна

1. **Включите "Always On"** в настройках Repl
2. **Настройте кастомный домен** (опционально)
3. **Мониторьте логи** в консоли Replit

## 🎉 Готово!

Ваш модуль векторного мэтчинга теперь работает в Replit!

**Что вы получили:**
- ✅ Полнофункциональный API сервер
- ✅ OpenAI Embeddings + Pinecone
- ✅ Умный мэтчинг по 4 категориям
- ✅ GPT объяснения совпадений
- ✅ Готовые примеры использования
- ✅ Полную документацию

**Следующие шаги:**
1. Настройте API ключи
2. Протестируйте функциональность
3. Интегрируйте с вашими приложениями
4. Настройте мониторинг
