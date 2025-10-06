#!/usr/bin/env python3
"""
Скрипт для запуска Pacific.ai Vector Matching API сервера
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from vector_matching.api import app
from vector_matching.config import config
import uvicorn

def main():
    """Основная функция запуска сервера"""
    print("🚀 Запуск Pacific.ai Vector Matching API...")
    print(f"📍 Хост: {config.API_HOST}")
    print(f"🔌 Порт: {config.API_PORT}")
    print(f"🌐 CORS Origins: {config.CORS_ORIGINS}")
    print(f"📚 API документация: http://{config.API_HOST}:{config.API_PORT}/docs")
    print("=" * 60)
    
    try:
        uvicorn.run(
            app,
            host=config.API_HOST,
            port=config.API_PORT,
            reload=config.API_DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
