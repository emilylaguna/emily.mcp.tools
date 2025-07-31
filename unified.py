import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from pathlib import Path
from fastmcp import FastMCP
import asyncio
from typing import Dict, Any
import coloredlogs, logging

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')
from fastmcp import Client

def create_gateway_server(client: Client) -> FastMCP:
    """Create a gateway MCP server that acts as a proxy for the main server's tools."""
    
    # Create gateway server
    gateway_server: FastMCP = FastMCP("Emily.Tools.Gateway")
    
    @gateway_server.tool(
        name="call_tool",
        description="Call any tool from the main server by specifying the tool name and parameters",
        tags={"gateway", "proxy", "call", "tool"},
    )
    async def call_tool(tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Call any tool from the main server.

        Args:
            tool_name: The name of the tool to call (e.g., 'todo_create_task', 'handoff_save', etc.)
            parameters: The parameters to pass to the tool (optional)

        Returns:
        The result from the called tool
        """
        logger.info(f"Gateway calling tool: {tool_name} with parameters: {parameters}")

        # Call the tool on the main server
        result = await client.call_tool(tool_name, parameters)
        return result.data
            
    
    @gateway_server.tool(
        name="list_available_tools",
        description="List all available tools from the main Emily.Tools server",
        tags={"gateway", "list", "tools", "discovery"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def list_available_tools() -> list:
        """
        List all available tools from the main Emily.Tools server.
    
        """
        try:
            # Get all tools from the main server
            return await client.list_tools()
            
        except Exception as e:
            logger.error(f"Failed to list available tools: {e}")
            return []

    logger.info("Gateway server initialized with proxy tools")
    return gateway_server

async def main() -> None:
    async with Client("main.py") as client:
        mcp = create_gateway_server(client)
        await mcp.run_async(transport="http", host="0.0.0.0", port=9090)
        
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())    

