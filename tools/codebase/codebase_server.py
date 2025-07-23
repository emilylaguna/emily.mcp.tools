"""
Codebase Server - Dedicated FastMCP server for codebase analysis functionality.
"""

import logging
import asyncio
from pathlib import Path
from fastmcp import FastMCP
from .analysis_tool import CodebaseAnalysisTool

logger = logging.getLogger(__name__)


def create_codebase_server(data_dir: Path) -> FastMCP:
    """Create and configure the Codebase Analysis server."""
    server = FastMCP("CodebaseService")
    
    # Initialize codebase analysis tool
    codebase_tool = CodebaseAnalysisTool(data_dir)
    
    # Initialize synchronously
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(codebase_tool.initialize(server))
        loop.close()
        logger.info("Codebase server initialized")
    except RuntimeError:
        asyncio.create_task(codebase_tool.initialize(server))
        logger.info("Codebase server initialization scheduled")
    
    return server 