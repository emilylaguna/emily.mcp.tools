"""
Automation Server - Dedicated FastMCP server for workflow automation.
"""

import logging
import asyncio
from pathlib import Path
from fastmcp import FastMCP
from .automation import AutomationTool

try:
    from ...core import UnifiedMemoryStore
    from ...workflows.engine import WorkflowEngine
except ImportError:
    from core import UnifiedMemoryStore
    from workflows.engine import WorkflowEngine

logger = logging.getLogger(__name__)


def create_automation_server(
    memory_store: UnifiedMemoryStore, 
    data_dir: Path, 
    workflow_engine: WorkflowEngine
) -> FastMCP:
    """Create and configure the Automation server."""
    server = FastMCP("AutomationService")
    
    # Initialize automation tool
    automation_tool = AutomationTool(memory_store, data_dir, workflow_engine)
    
    # Initialize synchronously
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(automation_tool.initialize(server))
        loop.close()
        logger.info("Automation server initialized")
    except RuntimeError:
        asyncio.create_task(automation_tool.initialize(server))
        logger.info("Automation server initialization scheduled")
    
    return server 