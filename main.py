"""
Emily.Tools

Main entry point for the Emily.Tools MCP server with all tools registered.
"""

from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from core import UnifiedMemoryStore
from intelligence import IntelligentSearchMCPTools
from tools import *

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize unified memory store
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    
    # Initialize MCP server
    mcp = FastMCP("Emily.Tools")

    # Initialize unified tools with memory store
    import asyncio
    asyncio.run(AutomationTool(memory_store, data_dir).initialize(mcp))
    asyncio.run(UnifiedTodoTool(memory_store).initialize(mcp))
    asyncio.run(UnifiedHandoffTool(memory_store).initialize(mcp))
    asyncio.run(UnifiedKnowledgeGraphTool(memory_store, data_dir).initialize(mcp))
    
    # Initialize intelligent search tools
    intelligent_search_tools = IntelligentSearchMCPTools(memory_store)
    intelligent_search_tools.register_tools(mcp)

    return mcp

# Expose a global MCP server object for MCP CLI compatibility
mcp = create_mcp_server()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
