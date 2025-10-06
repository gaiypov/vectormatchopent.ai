# 📦 Экспорт в Replit - Пошаговая инструкция

## 🎯 Быстрый способ

### 1. Создайте ZIP архив
```bash
# В папке pacific.ai
zip -r pacific-ai-vector-matching.zip backend/ .replit replit.nix REPLIT_SETUP.md
```

### 2. Загрузите в Replit
1. Создайте новый Python Repl на [replit.com](https://replit.com)
2. Нажмите "Upload" в файловом менеджере
3. Загрузите `pacific-ai-vector-matching.zip`
4. Распакуйте архив в Replit

## 📋 Список файлов для загрузки

### Обязательные файлы:
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
.replit
replit.nix
REPLIT_SETUP.md
```

## 🔧 Настройка в Replit

### 1. Установите зависимости
```bash
pip install -r backend/requirements.txt
```

### 2. Настройте Secrets
В Replit добавьте в Secrets:
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `API_HOST` = 0.0.0.0
- `API_PORT` = 8000
- `API_DEBUG` = True

### 3. Запустите сервер
```bash
python backend/run_server.py
```

## 🧪 Тестирование

### 1. Проверка здоровья
```bash
curl https://your-repl-url.repl.co/health
```

### 2. API документация
Откройте: `https://your-repl-url.repl.co/docs`

### 3. Пример использования
```bash
python backend/example_usage.py
```

## 🚀 Готово!

Ваш модуль векторного мэтчинга теперь работает в Replit!
