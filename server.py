"""
Core MCP server implementation with extensible tool architecture.
"""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

from tools.base import BaseTool

class AppContext(BaseModel):
    """Application context with tool registry and data directory."""
    
    tools: Dict[str, Any]  # Using Any to avoid Pydantic schema issues with BaseTool
    data_dir: Path

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with tool initialization."""
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize tools
    tools: Dict[str, BaseTool] = {}
    
    try:
        yield AppContext(tools=tools, data_dir=data_dir)
    finally:
        # Cleanup tools
        for tool in tools.values():
            if hasattr(tool, 'cleanup'):
                await tool.cleanup()


class EmilyToolsServer:
    """Main server class that manages tools and MCP integration."""
    
    def __init__(self):
        self.mcp = FastMCP("Emily Tools", lifespan=app_lifespan)
        self._register_core_tools()
    
    def _register_core_tools(self):
        """Register core tools with the MCP server."""
        
        @self.mcp.tool()
        async def list_tools(ctx: Context) -> List[Dict[str, Any]]:
            """List all available tools and their capabilities."""
            app_ctx = ctx.request_context.lifespan_context
            return [
                {
                    "name": name,
                    "description": tool.description,
                    "capabilities": tool.get_capabilities()
                }
                for name, tool in app_ctx.tools.items()
            ]
        
        @self.mcp.tool()
        async def get_tool_info(tool_name: str, ctx: Context) -> Dict[str, Any]:
            """Get detailed information about a specific tool."""
            app_ctx = ctx.request_context.lifespan_context
            if tool_name not in app_ctx.tools:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            tool = app_ctx.tools[tool_name]
            return {
                "name": tool_name,
                "description": tool.description,
                "capabilities": tool.get_capabilities(),
                "status": "active"
            }
    
    def register_tool(self, name: str, tool: BaseTool):
        """Register a new tool with the server."""
        # Store tool in context (will be available after server starts)
        # In a real implementation, you'd need to handle this differently
        # For now, we'll use a class variable to store tools
        if not hasattr(self, '_pending_tools'):
            self._pending_tools = {}
        self._pending_tools[name] = tool
    
    def run(self, transport: str = "stdio"):
        """Run the MCP server."""
        self.mcp.run(transport=transport)


# Global server instance
server = EmilyToolsServer()
