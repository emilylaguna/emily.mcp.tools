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
    automation_tool.register(server)
    logger.info("Automation server initialized")
    
    return server 