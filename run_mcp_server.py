#!/usr/bin/env python3
"""
Скрипт для запуска MCP сервера Pacific.ai Vector Matching
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулю векторного мэтчинга
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"
sys.path.insert(0, str(backend_dir))

async def main():
    """Запуск MCP сервера"""
    print("🚀 Запуск MCP сервера для Pacific.ai Vector Matching...")
    
    try:
        # Импортируем и запускаем MCP сервер
        from mcp_server import main as mcp_main
        await mcp_main()
    except KeyboardInterrupt:
        print("\n👋 MCP сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска MCP сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
