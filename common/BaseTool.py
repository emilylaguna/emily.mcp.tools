from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseTool(ABC):
    """Base class for all tools in the Emily Tools server."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_file = data_dir / f"{self.name}.jsonl"

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for MCP clients."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """List of tool capabilities."""
        pass

    async def initialize(self, mcp) -> None:
        """Initialize the tool (e.g., create database tables, register tools with MCP server."""
        self.register(mcp)

    async def cleanup(self) -> None:
        """Cleanup resources when the tool is shut down."""
        pass

    def get_tool_functions(self) -> List[Dict[str, Any]]:
        """Get MCP tool function definitions for this tool."""
        return []

    @abstractmethod
    def register(self, mcp):
        """Register all tool functions and resources with the MCP server."""
        pass