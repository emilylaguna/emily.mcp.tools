# Emily Tools - Extensible MCP Server

A Model Context Protocol (MCP) server that provides a collection of local productivity tools in an extensible architecture.

## Features

### Core Tools
- **TODO List** - Task management with priorities, due dates, and status tracking
- **Calendar** - Event management and scheduling
- **Codebase Knowledgebase** - Knowledge graph for multiple codebases
- **Async Tasks** - Background task execution and scheduling
- **Time Service** - Current date/time information for LLMs
- **Memory Graph** - Persistent memory graph for entities, relations, and observations
- **Handoff** - Save and retrieve chat context for handoff between sessions

### Architecture
- **Modular Design** - Each tool is self-contained and independently extensible
- **Local Storage** - All data stored locally using JSONL files
- **Plugin System** - Easy to add new tools without modifying core code
- **Type Safety** - Full type hints and Pydantic models for data validation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd emily.mcp.tools

# Install dependencies
uv sync

# Run the server
uv run python main.py
```

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

## Usage

### Running the Server

```bash
# Development mode with MCP Inspector
uv run mcp dev main.py

# Install in Claude Desktop
uv run mcp install main.py

# Direct execution
uv run python main.py
```

### Handoff Tool Example

The Handoff tool allows you to save and retrieve chat context for seamless session handoff:

```python
# Save context
mcp.call("handoff_save_context", context="Current chat summary or state")

# Get the latest context
mcp.call("handoff_get_latest_context")

# List recent contexts
mcp.call("handoff_list_contexts", limit=5)
```

### Adding New Tools

1. Create a new tool module in `tools/` (use a subfolder if needed, e.g., `tools/mytool/mytool.py`)
2. Implement the tool interface (subclass `BaseTool`)
3. Register the tool in `main.py`
4. Add any required dependencies to `pyproject.toml`

## Project Structure

```
emily.mcp.tools/
├── main.py                  # Main MCP server entry point
├── server.py                # Core server implementation
├── tools/                   # Tool modules
│   ├── __init__.py
│   ├── base.py              # Base tool interface
│   ├── todo/
│   │   └── todo.py          # TODO list tool
│   ├── calendar/
│   │   └── calendar.py      # Calendar tool
│   ├── knowledgebase/
│   │   └── knowledgebase.py # Codebase knowledgebase
│   ├── async_tasks/
│   │   └── async_tasks.py   # Async task management
│   ├── time_service/
│   │   └── time_service.py  # Time service
│   ├── memory_graph/
│   │   └── memory_graph.py  # Memory graph tool
│   ├── handoff/
│   │   └── handoff.py       # Handoff tool
├── data/                    # Local data storage (JSONL files)
│   ├── async_tasks.jsonl
│   ├── calendar.jsonl
│   ├── handoff.jsonl
│   ├── knowledgebase.jsonl
│   ├── memory_graph.jsonl
│   ├── time_service.jsonl
│   └── todo.jsonl
├── utils/                   # Shared utilities
│   └── __init__.py
├── pyproject.toml           # Project dependencies and config
├── uv.lock                  # Lockfile for uv
├── configure.sh             # Configuration script
├── start.sh                 # Startup script
└── README.md                # Project documentation
```

## License

MIT License
