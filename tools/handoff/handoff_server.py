"""
Handoff Server - Dedicated FastMCP server for handoff functionality.
"""

import logging
import asyncio
from fastmcp import FastMCP
from .unified_handoff_tool import UnifiedHandoffTool

try:
    from ...core import UnifiedMemoryStore
except ImportError:
    from core import UnifiedMemoryStore

logger = logging.getLogger(__name__)


def create_handoff_server(memory_store: UnifiedMemoryStore) -> FastMCP:
    """Create and configure the Handoff server."""
    server = FastMCP("HandoffService")
    
    # Initialize handoff tool
    handoff_tool = UnifiedHandoffTool(memory_store)
    handoff_tool.register(server)
    
    return server 