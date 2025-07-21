"""
Emily Tools - Extensible MCP Server

Main entry point for the Emily Tools MCP server with all tools registered.
"""

from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from tools import *

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize MCP server
    mcp = FastMCP("Emily Tools")

    # Initialize tools (this will also register them with MCP)
    import asyncio
    asyncio.run(TodoTool(data_dir).initialize(mcp))
    asyncio.run(CalendarTool(data_dir).initialize(mcp))
    asyncio.run(KnowledgebaseTool(data_dir).initialize(mcp))
    asyncio.run(AsyncTasksTool(data_dir).initialize(mcp))
    asyncio.run(TimeServiceTool(data_dir).initialize(mcp))
    asyncio.run(MemoryGraphTool(data_dir).initialize(mcp))
    asyncio.run(HandoffTool(data_dir).initialize(mcp))
    
    return mcp

# Expose a global MCP server object for MCP CLI compatibility
mcp = create_mcp_server()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
