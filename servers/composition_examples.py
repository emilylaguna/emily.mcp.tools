"""
FastMCP Server Composition Examples

This module demonstrates different server composition patterns
based on the FastMCP documentation.
"""

import asyncio
from pathlib import Path
from fastmcp import FastMCP

from core import UnifiedMemoryStore
from tools.todo.todo_server import create_todo_server
from tools.automation.automation_server import create_automation_server
from tools.handoff.handoff_server import create_handoff_server
from tools.knowledgebase.knowledge_graph_server import create_knowledge_graph_server
from intelligence.intelligence_server import create_intelligence_server
from workflows.engine import WorkflowEngine


def example_mounting_with_prefixes():
    """Example: Mount servers with prefixes for organized namespacing."""
    data_dir = Path("data")
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    workflow_engine = WorkflowEngine(memory_store)
    
    # Main server
    main_server = FastMCP("Emily.Tools.Organized")
    
    # Create and mount individual servers with clear prefixes
    todo_server = create_todo_server(memory_store)
    automation_server = create_automation_server(memory_store, data_dir, workflow_engine)
    
    main_server.mount(todo_server, prefix="todo")
    main_server.mount(automation_server, prefix="workflow")
    
    return main_server


def example_mounting_without_prefixes():
    """Example: Mount servers without prefixes for flat namespace."""
    data_dir = Path("data")
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    
    # Main server
    main_server = FastMCP("Emily.Tools.Flat")
    
    # Create and mount servers without prefixes
    # Note: This may cause naming conflicts if tools have same names
    todo_server = create_todo_server(memory_store)
    handoff_server = create_handoff_server(memory_store)
    
    main_server.mount(todo_server)  # No prefix
    main_server.mount(handoff_server)  # No prefix
    
    return main_server


async def example_importing_vs_mounting():
    """Example: Demonstrate difference between importing (static) and mounting (live)."""
    data_dir = Path("data")
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    
    # Example 1: Importing (static composition)
    static_server = FastMCP("Emily.Tools.Static")
    todo_server_for_import = create_todo_server(memory_store)
    
    # Import creates a one-time copy
    await static_server.import_server(todo_server_for_import, prefix="imported_todo")
    
    # Example 2: Mounting (live composition) 
    live_server = FastMCP("Emily.Tools.Live")
    todo_server_for_mount = create_todo_server(memory_store)
    
    # Mount creates a live link
    live_server.mount(todo_server_for_mount, prefix="mounted_todo")
    
    return static_server, live_server


def example_modular_architecture():
    """Example: Create a modular architecture with domain-specific servers."""
    data_dir = Path("data")
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    workflow_engine = WorkflowEngine(memory_store)
    
    # Create domain-specific composite servers
    
    # Task Management Domain
    task_management = FastMCP("TaskManagement")
    todo_server = create_todo_server(memory_store)
    automation_server = create_automation_server(memory_store, data_dir, workflow_engine)
    task_management.mount(todo_server, prefix="tasks")
    task_management.mount(automation_server, prefix="workflows")
    
    # Knowledge Domain  
    knowledge_domain = FastMCP("KnowledgeDomain")
    kg_server = create_knowledge_graph_server(memory_store, data_dir)
    handoff_server = create_handoff_server(memory_store)
    intelligence_server = create_intelligence_server(memory_store)
    knowledge_domain.mount(kg_server, prefix="graph")
    knowledge_domain.mount(handoff_server, prefix="handoff")
    knowledge_domain.mount(intelligence_server, prefix="ai")
    
    # Main application server
    main_app = FastMCP("Emily.Tools.Modular")
    main_app.mount(task_management, prefix="task_mgmt")
    main_app.mount(knowledge_domain, prefix="knowledge")
    
    return main_app


def example_team_based_composition():
    """Example: Compose servers as if different teams built different components."""
    data_dir = Path("data")
    memory_store = UnifiedMemoryStore(data_dir / "memory.db")
    workflow_engine = WorkflowEngine(memory_store)
    
    # Team A: Task Management Team
    team_a_server = FastMCP("TeamA.TaskTools")
    todo_server = create_todo_server(memory_store)
    automation_server = create_automation_server(memory_store, data_dir, workflow_engine)
    team_a_server.mount(todo_server)
    team_a_server.mount(automation_server, prefix="auto")
    
    # Team B: Knowledge Team
    team_b_server = FastMCP("TeamB.KnowledgeTools")
    kg_server = create_knowledge_graph_server(memory_store, data_dir)
    intelligence_server = create_intelligence_server(memory_store)
    team_b_server.mount(kg_server)
    team_b_server.mount(intelligence_server, prefix="search")
    
    # Integration team combines everything
    integrated_app = FastMCP("Emily.Tools.Integrated")
    integrated_app.mount(team_a_server, prefix="tasks")
    integrated_app.mount(team_b_server, prefix="knowledge")
    
    return integrated_app


if __name__ == "__main__":
    # Demonstrate different composition patterns
    print("FastMCP Server Composition Examples")
    print("===================================")
    
    # Mount with prefixes
    server1 = example_mounting_with_prefixes()
    print(f"1. Organized server: {server1.name}")
    
    # Mount without prefixes
    server2 = example_mounting_without_prefixes()
    print(f"2. Flat server: {server2.name}")
    
    # Modular architecture
    server3 = example_modular_architecture()
    print(f"3. Modular server: {server3.name}")
    
    # Team-based composition
    server4 = example_team_based_composition()
    print(f"4. Team-based server: {server4.name}")
    
    print("\nAll examples created successfully!")
    print("Choose any server and run server.run() to start it.") 