"""
Todo Server - Dedicated FastMCP server for todo functionality.
"""

import logging
import asyncio
from pathlib import Path
from fastmcp import FastMCP
from .unified_todo_tool import UnifiedTodoTool

try:
    from ...core import UnifiedMemoryStore
except ImportError:
    from core import UnifiedMemoryStore

logger = logging.getLogger(__name__)


def create_todo_server(memory_store: UnifiedMemoryStore) -> FastMCP:
    """Create and configure the Todo server."""
    server = FastMCP("TodoService")
    
    # Initialize todo tool
    todo_tool = UnifiedTodoTool(memory_store)
    
    # Initialize synchronously - the tool.initialize() method handles async setup
    try:
        # Run the async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(todo_tool.initialize(server))
        loop.close()
        logger.info("Todo server initialized")
    except RuntimeError:
        # If we're already in an event loop, schedule the initialization
        asyncio.create_task(todo_tool.initialize(server))
        logger.info("Todo server initialization scheduled")
    
    return server 