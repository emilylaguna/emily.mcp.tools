"""
Tools package for Emily Tools MCP server.
Now supporting FastMCP server composition.
"""

# Individual tool classes (for direct use)
from .todo.unified_todo_tool import UnifiedTodoTool
from .calendar.calendar import CalendarTool
from .knowledgebase.unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool
from .async_tasks.async_tasks import AsyncTasksTool
from .time_service.time_service import TimeServiceTool
from .handoff.unified_handoff_tool import UnifiedHandoffTool
from .automation.automation import AutomationTool
from .codebase.analysis_tool import CodebaseAnalysisTool

# Server composition functions (for modular architecture)
from .todo.todo_server import create_todo_server
from .automation.automation_server import create_automation_server
from .handoff.handoff_server import create_handoff_server
from .knowledgebase.knowledge_graph_server import create_knowledge_graph_server
from .codebase.codebase_server import create_codebase_server

__all__ = [
    # Individual tools
    "UnifiedTodoTool", 
    "CalendarTool",
    "UnifiedKnowledgeGraphTool",
    "AsyncTasksTool",
    "TimeServiceTool",
    "UnifiedHandoffTool",
    "AutomationTool",
    "CodebaseAnalysisTool",
    
    # Server composition functions
    "create_todo_server",
    "create_automation_server", 
    "create_handoff_server",
    "create_knowledge_graph_server",
    "create_codebase_server",
] 