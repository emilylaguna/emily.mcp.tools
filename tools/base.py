"""
Base tool interface for Emily Tools MCP server.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

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
        """Initialize the tool (e.g., create database tables, register toolsith MCP server."""
        # self.data_file.parent.mkdir(parents=True, exist_ok=True)
        # self.data_file.touch(exist_ok=True)
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