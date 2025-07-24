"""
Knowledge Graph Server - Dedicated FastMCP server for knowledge graph functionality.
"""

import logging
import asyncio
from pathlib import Path
from fastmcp import FastMCP
from .unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool

from emily_core import UnifiedMemoryStore
logger = logging.getLogger(__name__)


def create_knowledge_graph_server(memory_store: UnifiedMemoryStore, data_dir: Path) -> FastMCP:
    """Create and configure the Knowledge Graph server."""
    server = FastMCP("KnowledgeGraphService")
    
    # Initialize knowledge graph tool
    kg_tool = UnifiedKnowledgeGraphTool(memory_store, data_dir)
    kg_tool.register(server)
    
    return server 