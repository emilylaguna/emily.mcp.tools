# Emily Tools - Extensible MCP Server

A Model Context Protocol (MCP) server that provides a collection of local productivity tools in an extensible architecture.

## Features

### Core Tools
- **TODO List** - Task management with priorities, due dates, and status tracking
- **Calendar** - Event management and scheduling
- **Codebase Knowledgebase** - Knowledge graph for multiple codebases
- **Async Tasks** - Background task execution and scheduling
- **Time Service** - Current date/time information for LLMs
- **Handoff** - Save and retrieve chat context for handoff between sessions

### Architecture
- **Modular Design** - Each tool is self-contained and independently extensible
- **Local Storage** - All data stored locally using SQLite databases
- **Plugin System** - Easy to add new tools without modifying core code
- **Type Safety** - Full type hints and Pydantic models for data validation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd emily.tools

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

1. Create a new tool module in `tools/`
2. Implement the tool interface
3. Register the tool in `main.py`
4. Add any required dependencies to `pyproject.toml`

## Project Structure

```
emily.tools/
├── main.py                 # Main MCP server entry point
├── server.py              # Core server implementation
├── tools/                 # Tool modules
│   ├── __init__.py
│   ├── todo.py           # TODO list tool
│   ├── calendar.py       # Calendar tool
│   ├── knowledgebase.py  # Codebase knowledgebase
│   ├── async_tasks.py    # Async task management
│   ├── time_service.py   # Time service
│   ├── handoff/         # Handoff tool
├── data/                 # Local data storage
├── utils/                # Shared utilities
└── tests/                # Test suite
```

## License

MIT License
