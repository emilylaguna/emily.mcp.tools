"""
Emily.Tools

Main entry point for the Emily.Tools MCP server with all tools registered.
"""

from pathlib import Path

from mcp.server.fastmcp import Context, FastMCP

from core import UnifiedMemoryStore
from intelligence import IntelligentSearchMCPTools
from tools import *
import coloredlogs, logging

logger = logging.getLogger(__name__)

# coloredlogs.install(level='INFO')

# Integrate static analysis tools so that higher-level MCP skills can import
# `analysis` without additional setup.  The import is lightweight and does not
# run any expensive parsing at startup.
import analysis

def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize unified memory store first (without workflow engine)
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    
    # Initialize workflow engine with memory store
    from workflows.engine import WorkflowEngine
    workflow_engine = WorkflowEngine(memory_store)
    
    # Update memory store with workflow engine for auto-triggering
    memory_store.workflow_engine = workflow_engine
    logger.info(f"Workflow automation enabled: {memory_store.workflow_engine is not None}")

    # Initialize MCP server
    mcp = FastMCP("Emily.Tools")

    # Initialize unified tools with memory store and workflow engine
    import asyncio
    asyncio.run(AutomationTool(memory_store, data_dir, workflow_engine).initialize(mcp))
    asyncio.run(UnifiedTodoTool(memory_store).initialize(mcp))
    asyncio.run(UnifiedHandoffTool(memory_store).initialize(mcp))
    asyncio.run(UnifiedKnowledgeGraphTool(memory_store, data_dir).initialize(mcp))
    asyncio.run(CodebaseAnalysisTool(data_dir).initialize(mcp))
    
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
