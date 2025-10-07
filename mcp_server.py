#!/usr/bin/env python3
"""
MCP Server для Pacific.ai Vector Matching Module
Позволяет интегрировать модуль векторного мэтчинга с AI-ассистентами
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# Импортируем наш модуль векторного мэтчинга
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from vector_matching.api import app
from vector_matching.config import config
from vector_matching.models import (
    EmbeddingCreateRequest,
    MatchRequest,
    WeightsUpdateRequest
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем MCP сервер
mcp_server = Server("pacific-ai-vector-matching")

@mcp_server.list_tools()
async def list_tools() -> List[Tool]:
    """Возвращает список доступных инструментов"""
    return [
        Tool(
            name="create_embedding",
            description="Создает векторное представление (embedding) для текста",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Уникальный идентификатор сущности"
                    },
                    "entity_type": {
                        "type": "string",
                        "enum": ["candidate", "vacancy"],
                        "description": "Тип сущности: кандидат или вакансия"
                    },
                    "text": {
                        "type": "string",
                        "description": "Текст для создания embedding"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["skills", "career", "culture", "salary"],
                        "description": "Категория текста"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Дополнительные метаданные",
                        "additionalProperties": True
                    }
                },
                "required": ["entity_id", "entity_type", "text", "category"]
            }
        ),
        Tool(
            name="find_matches",
            description="Находит совпадения между кандидатом и вакансиями",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_id": {
                        "type": "string",
                        "description": "ID кандидата для поиска совпадений"
                    },
                    "vacancy_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Список ID вакансий для поиска (опционально)"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Количество лучших совпадений",
                        "default": 5
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Минимальный балл совпадения",
                        "default": 0.3
                    },
                    "weights": {
                        "type": "object",
                        "properties": {
                            "skills": {"type": "number"},
                            "career": {"type": "number"},
                            "culture": {"type": "number"},
                            "salary": {"type": "number"}
                        },
                        "description": "Веса для категорий мэтчинга"
                    }
                },
                "required": ["candidate_id"]
            }
        ),
        Tool(
            name="get_explanation",
            description="Получает объяснение совпадения между кандидатом и вакансией",
            inputSchema={
                "type": "object",
                "properties": {
                    "candidate_id": {
                        "type": "string",
                        "description": "ID кандидата"
                    },
                    "vacancy_id": {
                        "type": "string",
                        "description": "ID вакансии"
                    }
                },
                "required": ["candidate_id", "vacancy_id"]
            }
        ),
        Tool(
            name="update_weights",
            description="Обновляет веса для категорий мэтчинга",
            inputSchema={
                "type": "object",
                "properties": {
                    "weights": {
                        "type": "object",
                        "properties": {
                            "skills": {"type": "number"},
                            "career": {"type": "number"},
                            "culture": {"type": "number"},
                            "salary": {"type": "number"}
                        },
                        "description": "Новые веса для категорий"
                    }
                },
                "required": ["weights"]
            }
        ),
        Tool(
            name="get_weights",
            description="Получает текущие веса для категорий мэтчинга",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="health_check",
            description="Проверяет состояние сервиса векторного мэтчинга",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="batch_create_embeddings",
            description="Создает несколько embeddings одновременно",
            inputSchema={
                "type": "object",
                "properties": {
                    "embeddings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "entity_id": {"type": "string"},
                                "entity_type": {"type": "string", "enum": ["candidate", "vacancy"]},
                                "text": {"type": "string"},
                                "category": {"type": "string", "enum": ["skills", "career", "culture", "salary"]},
                                "metadata": {"type": "object", "additionalProperties": True}
                            },
                            "required": ["entity_id", "entity_type", "text", "category"]
                        },
                        "description": "Список данных для создания embeddings"
                    }
                },
                "required": ["embeddings"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Выполняет вызов инструмента"""
    try:
        if name == "create_embedding":
            return await handle_create_embedding(arguments)
        elif name == "find_matches":
            return await handle_find_matches(arguments)
        elif name == "get_explanation":
            return await handle_get_explanation(arguments)
        elif name == "update_weights":
            return await handle_update_weights(arguments)
        elif name == "get_weights":
            return await handle_get_weights(arguments)
        elif name == "health_check":
            return await handle_health_check(arguments)
        elif name == "batch_create_embeddings":
            return await handle_batch_create_embeddings(arguments)
        else:
            return [TextContent(
                type="text",
                text=f"Неизвестный инструмент: {name}"
            )]
    except Exception as e:
        logger.error(f"Ошибка выполнения инструмента {name}: {e}")
        return [TextContent(
            type="text",
            text=f"Ошибка: {str(e)}"
        )]

async def handle_create_embedding(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка создания embedding"""
    try:
        from vector_matching.embeddings import create_embedding
        
        result = await create_embedding(
            entity_id=arguments["entity_id"],
            entity_type=arguments["entity_type"],
            text=arguments["text"],
            category=arguments["category"],
            metadata=arguments.get("metadata", {})
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result.dict(), ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка создания embedding: {str(e)}"
        )]

async def handle_find_matches(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка поиска совпадений"""
    try:
        from vector_matching.matcher import find_matches
        
        result = await find_matches(
            candidate_id=arguments["candidate_id"],
            vacancy_ids=arguments.get("vacancy_ids"),
            top_k=arguments.get("top_k", 5),
            min_score=arguments.get("min_score", 0.3),
            weights=arguments.get("weights")
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result.dict(), ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка поиска совпадений: {str(e)}"
        )]

async def handle_get_explanation(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка получения объяснения"""
    try:
        from vector_matching.explain import get_match_explanation
        
        result = await get_match_explanation(
            candidate_id=arguments["candidate_id"],
            vacancy_id=arguments["vacancy_id"]
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result.dict(), ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка получения объяснения: {str(e)}"
        )]

async def handle_update_weights(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка обновления весов"""
    try:
        from vector_matching.config import update_weights
        
        weights = arguments["weights"]
        result = update_weights(weights)
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка обновления весов: {str(e)}"
        )]

async def handle_get_weights(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка получения весов"""
    try:
        from vector_matching.config import config
        
        weights = {
            "skills": config.WEIGHTS["skills"],
            "career": config.WEIGHTS["career"],
            "culture": config.WEIGHTS["culture"],
            "salary": config.WEIGHTS["salary"]
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(weights, ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка получения весов: {str(e)}"
        )]

async def handle_health_check(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка проверки здоровья"""
    try:
        from vector_matching.vector_db import vector_db
        from vector_matching.embeddings import embeddings_client
        
        # Проверяем подключения
        pinecone_status = "healthy" if vector_db.is_connected() else "unhealthy"
        openai_status = "healthy" if embeddings_client.is_available() else "unhealthy"
        
        health_data = {
            "status": "healthy" if pinecone_status == "healthy" and openai_status == "healthy" else "unhealthy",
            "services": {
                "pinecone": pinecone_status,
                "openai": openai_status
            },
            "timestamp": str(asyncio.get_event_loop().time())
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(health_data, ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка проверки здоровья: {str(e)}"
        )]

async def handle_batch_create_embeddings(arguments: Dict[str, Any]) -> List[TextContent]:
    """Обработка батчевого создания embeddings"""
    try:
        from vector_matching.embeddings import create_batch_embeddings
        
        embeddings_data = arguments["embeddings"]
        results = await create_batch_embeddings(embeddings_data)
        
        return [TextContent(
            type="text",
            text=json.dumps([result.dict() for result in results], ensure_ascii=False, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Ошибка батчевого создания embeddings: {str(e)}"
        )]

async def main():
    """Главная функция MCP сервера"""
    logger.info("Запуск MCP сервера для Pacific.ai Vector Matching...")
    
    # Инициализация модуля векторного мэтчинга
    try:
        from vector_matching.config import config
        from vector_matching.vector_db import vector_db
        from vector_matching.embeddings import embeddings_client
        
        # Проверяем подключения
        await vector_db.initialize()
        await embeddings_client.initialize()
        
        logger.info("Модуль векторного мэтчинга инициализирован")
    except Exception as e:
        logger.error(f"Ошибка инициализации: {e}")
        return
    
    # Запуск MCP сервера
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pacific-ai-vector-matching",
                server_version="1.0.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
