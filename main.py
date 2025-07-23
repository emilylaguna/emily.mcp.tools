"""
Emily.Tools

Main entry point for the Emily.Tools MCP server using FastMCP server composition.
Uses server mounting for modular, live-linked architecture.
"""
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from pathlib import Path
from fastmcp import FastMCP
import asyncio

from core import UnifiedMemoryStore
from tools.todo.todo_server import create_todo_server
from tools.automation.automation_server import create_automation_server
from tools.handoff.handoff_server import create_handoff_server
from tools.knowledgebase.knowledge_graph_server import create_knowledge_graph_server
from tools.codebase.codebase_server import create_codebase_server
from intelligence.intelligence_server import create_intelligence_server

import coloredlogs, logging
from workflows.engine import WorkflowEngine

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

# Integrate static analysis tools so that higher-level MCP skills can import
# `analysis` without additional setup.  The import is lightweight and does not
# run any expensive parsing at startup.
import analysis


def create_mcp_server() -> FastMCP:
    """Create and configure the main MCP server using server composition."""
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize unified memory store first (without workflow engine)
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    
    # Initialize workflow engine with memory store
    workflow_engine = WorkflowEngine(memory_store)
    
    # Update memory store with workflow engine for auto-triggering
    memory_store.workflow_engine = workflow_engine
    logger.info(f"Workflow automation enabled: {memory_store.workflow_engine is not None}")

    # Initialize main MCP server

    # Create individual service servers
    todo_server = create_todo_server(memory_store)
    automation_server = create_automation_server(memory_store, data_dir, workflow_engine)
    handoff_server = create_handoff_server(memory_store)
    kg_server = create_knowledge_graph_server(memory_store, data_dir)
    # codebase_server = create_codebase_server(data_dir)
    intelligence_server = create_intelligence_server(memory_store)

    main_server = FastMCP("Emily.Tools")

    # Mount servers WITHOUT prefixes since tools already have meaningful prefixes
    # This avoids double-prefixing (e.g., todo_todo_create_area -> todo_create_area)
    main_server.mount(todo_server)           # Tools: todo_create_area, todo_create_project, etc.
    main_server.mount(automation_server)     # Tools: automation_register_workflow, automation_list_workflows, etc.
    main_server.mount(handoff_server)        # Tools: handoff_save, handoff_get, handoff_list, etc.
    main_server.mount(kg_server)             # Tools: graph_create_entity, graph_find_related, etc.
    # main_server.mount(codebase_server)       # Tools: codebase_parse_file, codebase_analyse_repo, etc.
    main_server.mount(intelligence_server)   # Tools: intelligent_search, natural_query, complex_query, etc.

    # logger.info("Main server initialized with composed services:")
    # logger.info("- TodoService: todo_* tools")
    # logger.info("- AutomationService: automation_* tools")
    # logger.info("- HandoffService: handoff_* tools") 
    # logger.info("- KnowledgeGraphService: graph_* tools")
    # logger.info("- CodebaseService: codebase_* tools")
    # logger.info("- IntelligenceService: intelligent_*, natural_query, complex_query, etc.")

    return main_server

mcp = create_mcp_server()

def main():
    mcp.run()

if __name__ == "__main__":
    main()
