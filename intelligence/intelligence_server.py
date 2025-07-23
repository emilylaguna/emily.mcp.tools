"""
Intelligence Server - Dedicated FastMCP server for intelligent search functionality.
"""

import logging
from fastmcp import FastMCP
from .search_mcp import IntelligentSearchMCPTools

try:
    from ..core import UnifiedMemoryStore
except ImportError:
    from core import UnifiedMemoryStore

logger = logging.getLogger(__name__)


def create_intelligence_server(memory_store: UnifiedMemoryStore) -> FastMCP:
    """Create and configure the Intelligence server."""
    server = FastMCP("IntelligenceService")
    
    # Initialize intelligent search tools
    search_tools = IntelligentSearchMCPTools(memory_store)
    
    # Register tools directly (this should be synchronous)
    search_tools.register_tools(server)
    logger.info("Intelligence server initialized")
    
    return server 