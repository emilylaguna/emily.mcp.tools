# FastMCP Server Composition Architecture

This document explains how Emily.Tools has been refactored to use **FastMCP Server Composition** for better modularity, reusability, and organization.

## Overview

Emily.Tools now uses FastMCP's server composition features to create a modular architecture where individual services can be developed, tested, and deployed independently while being composed into a unified application.

## Architecture Changes

### Before: Monolithic Server
Previously, all tools were registered in a single FastMCP server in `main.py`:

```python
# Old approach - everything in one server
mcp = FastMCP("Emily.Tools")
asyncio.run(AutomationTool(...).initialize(mcp))
asyncio.run(UnifiedTodoTool(...).initialize(mcp))
# ... all tools in one place
```

### After: Composed Server Architecture
Now we have individual servers for each domain that are mounted into a main server:

```python
# New approach - modular composition
main_server = FastMCP("Emily.Tools")

# Create individual service servers
todo_server = create_todo_server(memory_store)
automation_server = create_automation_server(memory_store, data_dir, workflow_engine)

# Mount with prefixes for organized namespacing
main_server.mount(todo_server, prefix="todo")
main_server.mount(automation_server, prefix="automation")
```

## Individual Service Servers

### 1. TodoService (`tools/todo/todo_server.py`)
- **Purpose**: Task and project management
- **Prefix**: `todo_*`
- **Tools**: All todo-related MCP tools
- **Resources**: Task and project data

### 2. AutomationService (`tools/automation/automation_server.py`)
- **Purpose**: Workflow automation and triggers
- **Prefix**: `automation_*`
- **Tools**: Workflow management, triggers, suggestions
- **Dependencies**: WorkflowEngine

### 3. HandoffService (`tools/handoff/handoff_server.py`)
- **Purpose**: Session context and handoff management
- **Prefix**: `handoff_*`
- **Tools**: Context saving, retrieval, insights

### 4. KnowledgeGraphService (`tools/knowledgebase/knowledge_graph_server.py`)
- **Purpose**: Entity relationships and knowledge management
- **Prefix**: `graph_*`
- **Tools**: Entity CRUD, relations, graph algorithms

### 5. CodebaseService (`tools/codebase/codebase_server.py`)
- **Purpose**: Code analysis and insights
- **Prefix**: `codebase_*`
- **Tools**: File parsing, complexity analysis, hotspots

### 6. IntelligenceService (`intelligence/intelligence_server.py`)
- **Purpose**: AI-powered search and suggestions
- **Prefix**: `intelligence_*`
- **Tools**: Semantic search, natural queries, smart suggestions

## Server Composition Benefits

### 1. **Modularity**
- Each service is self-contained with its own lifecycle
- Services can be developed and tested independently
- Clear separation of concerns

### 2. **Reusability**
- Individual servers can be reused in different compositions
- Easy to create specialized versions (e.g., todo-only server)
- Services can be shared across different applications

### 3. **Team Development**
- Different teams can own different services
- Parallel development without conflicts
- Independent deployment and versioning

### 4. **Live Composition**
- Uses mounting (not importing) for live links
- Changes to individual servers are immediately reflected
- Dynamic updates without restarting the main server

## Tool Naming Convention

With server composition, tools are prefixed to avoid naming conflicts:

| Service | Prefix | Example Tool | Full Name |
|---------|--------|-------------|-----------|
| TodoService | `todo_` | `create_task` | `todo_create_task` |
| AutomationService | `automation_` | `register_workflow` | `automation_register_workflow` |
| HandoffService | `handoff_` | `save` | `handoff_save` |
| KnowledgeGraphService | `graph_` | `create_entity` | `graph_create_entity` |
| CodebaseService | `codebase_` | `parse_file` | `codebase_parse_file` |
| IntelligenceService | `intelligence_` | `search` | `intelligence_search` |

## Usage Examples

### Basic Usage (Current Default)
```python
from main import create_mcp_server

# Create the fully composed server
server = create_mcp_server()
server.run()
```

### Custom Composition
```python
from tools.todo.todo_server import create_todo_server
from tools.automation.automation_server import create_automation_server
from core import UnifiedMemoryStore

# Create a task-focused server
memory_store = UnifiedMemoryStore("data/memory.db")
task_server = FastMCP("TaskFocused")

todo_server = create_todo_server(memory_store)
automation_server = create_automation_server(memory_store, data_dir, workflow_engine)

task_server.mount(todo_server)
task_server.mount(automation_server, prefix="workflows")

task_server.run()
```

### Domain-Specific Servers
```python
# Knowledge-focused server
knowledge_server = FastMCP("KnowledgeTools")
knowledge_server.mount(create_knowledge_graph_server(...))
knowledge_server.mount(create_intelligence_server(...))
knowledge_server.mount(create_handoff_server(...))

# Task-focused server
task_server = FastMCP("TaskTools")
task_server.mount(create_todo_server(...))
task_server.mount(create_automation_server(...))
```

## Development Workflow

### Adding a New Service
1. Create `tools/new_service/new_service_server.py`
2. Implement `create_new_service_server()` function
3. Add to `tools/__init__.py` exports
4. Mount in `main.py` with appropriate prefix

### Testing Individual Services
```python
# Test a single service
from tools.todo.todo_server import create_todo_server

server = create_todo_server(memory_store)
# Test just the todo functionality
```

### Modifying Existing Services
- Changes to individual servers are automatically reflected (live mounting)
- No need to restart the main server during development
- Services maintain their own lifecycle and cleanup

## Configuration Options

### Resource Prefix Format
Emily.Tools uses the default **path format** for resource prefixes:
```
data://todo/tasks/123  # Path format (default)
```

To use legacy protocol format:
```python
import fastmcp
fastmcp.settings.resource_prefix_format = "protocol"
# Results in: todo+data://tasks/123
```

### Mounting vs Importing
- **Current**: Uses mounting for live links
- **Alternative**: Use importing for static composition

```python
# Live mounting (current approach)
main_server.mount(todo_server, prefix="todo")

# Static importing (alternative)
await main_server.import_server(todo_server, prefix="todo")
```

## Examples and Patterns

See `servers/composition_examples.py` for comprehensive examples of:
- Mounting with and without prefixes
- Importing vs mounting comparison
- Modular domain-specific architecture
- Team-based composition patterns

## Migration from Old Architecture

The old architecture is fully backward compatible. Individual tool classes are still available for direct use:

```python
# Still works - direct tool usage
from tools import UnifiedTodoTool
todo_tool = UnifiedTodoTool(memory_store)
```

New code should prefer the server composition approach for better modularity and future scalability.

## Best Practices

1. **Use descriptive prefixes** to avoid naming conflicts
2. **Group related functionality** in the same server
3. **Prefer mounting over importing** for development flexibility
4. **Test individual servers** before composition
5. **Document service dependencies** clearly
6. **Use lifespan management** for proper resource cleanup

## Future Enhancements

- Configuration-based server composition
- Remote server proxying for distributed architecture
- Service discovery and registration
- Health checks and monitoring per service
- Dynamic service loading/unloading 