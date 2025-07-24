"""
Time Service Server - Dedicated FastMCP server for time functionality.
"""

import logging
import asyncio
from pathlib import Path
from fastmcp import FastMCP
import time_service

from emily_core import UnifiedMemoryStore

logger = logging.getLogger(__name__)

def create_time_service_server(memory_store: UnifiedMemoryStore = None) -> FastMCP:
    """Create and configure the Time Service server."""
    server = FastMCP("TimeService")
    
    memory_store = memory_store or UnifiedMemoryStore(db_path="time_service.db")
    time_service_tool = TimeServiceTool(memory_store)
    time_service_tool.register(server)

    return server 

mcp = create_mcp_server()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
