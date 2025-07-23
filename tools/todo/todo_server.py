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
    todo_tool.register(server)

    return server 
