# Emily Tools - Intelligent Unified Memory System

A Model Context Protocol (MCP) server that provides intelligent productivity tools with unified memory architecture, AI-powered search, and cross-domain intelligence.

## 🚀 Key Features

### 🧠 Unified Memory Architecture
- **Single Source of Truth**: All data stored in SQLite with vector search
- **Cross-Domain Intelligence**: Connect conversations, tasks, code, and people
- **AI-Powered Search**: Semantic search across all data types
- **Automatic Entity Extraction**: AI identifies people, projects, files, and more

### 🛠️ Enhanced Tools
- **Smart Todo Management**: Things-style todos with context awareness
- **Intelligent Handoff**: AI-enhanced context preservation
- **Knowledge Graph**: Multi-codebase knowledge with relationships
- **Workflow Automation**: AI-powered workflow suggestions and execution

### 🔍 Advanced Search
- **Semantic Search**: Find content by meaning, not just keywords
- **Cross-Domain Queries**: "Show me all tasks related to the authentication project"
- **Entity Linking**: Automatic linking of related entities
- **Timeline View**: Unified timeline of all activities

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                        │
├─────────────────────────────────────────────────────────────┤
│                Tool Wrapper Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Handoff     │ │ Todo        │ │ Knowledge   │          │
│  │ Wrapper     │ │ Wrapper     │ │ Graph       │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│              Unified Memory Store                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ SQLite      │ │ Vector      │ │ AI          │          │
│  │ Database    │ │ Search      │ │ Extraction  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd emily.mcp.tools

# Install dependencies
uv sync

# Run the server
uv run python main.py
```

## 🚀 Quick Start

### 1. Start the Server

```bash
# Development mode with MCP Inspector
uv run mcp dev main.py

# Install in Claude Desktop
uv run mcp install main.py
```

### 2. Use Smart Todo Management

```python
# Create a task with AI enhancement
mcp.call("todo_create_task", 
         title="Implement authentication",
         description="Add OAuth2 support to the API")

# Search for related tasks
mcp.call("todo_search_tasks", 
         query="authentication OAuth2")
```

### 3. Use Intelligent Handoff

```python
# Save context with AI enhancement
mcp.call("handoff_save_context", 
         context="Working on authentication implementation")

# Get AI-enhanced context
mcp.call("handoff_get_latest_context")
```

### 4. Use Knowledge Graph

```python
# Add code knowledge
mcp.call("knowledge_add_entity",
         name="auth.py",
         entity_type="file",
         content="OAuth2 authentication implementation")

# Find related knowledge
mcp.call("knowledge_search", 
         query="authentication patterns")
```

## 🔧 Configuration

### Environment Variables

```bash
# Database configuration
MEMORY_DB_PATH=data/memory.db
EMBEDDING_MODEL=all-MiniLM-L6-v2
ENABLE_VECTOR_SEARCH=true
ENABLE_AI_EXTRACTION=true

# Performance tuning
MAX_CONNECTIONS=10
BATCH_SIZE=100
VECTOR_DIMENSION=384
```

### Database Schema

The unified memory system uses 4 main tables:

- **memory_entities**: All entities (tasks, people, files, projects)
- **memory_relations**: Relationships between entities
- **memory_contexts**: Contextual information (conversations, sessions)
- **memory_embeddings**: Vector embeddings for semantic search

## 📚 Documentation

- [API Reference](docs/api_reference.md)
- [Migration Guide](docs/migration_guide.md)
- [Architecture Guide](docs/architecture.md)
- [User Guides](docs/)

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/test_core.py
uv run pytest tests/test_handoff.py
uv run pytest tests/test_todo.py
```

## 🔄 Migration from Legacy System

If you're upgrading from the JSONL-based system:

```bash
# Run migration
uv run python migration_cli.py migrate --data-dir data/ --output-db data/memory.db

# Verify migration
uv run python migration_cli.py verify --db-path data/memory.db
```

See [Migration Guide](docs/migration_guide.md) for detailed instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License

## 📁 Project Structure

```
emily.mcp.tools/
├── main.py                  # Main MCP server entry point
├── server.py                # Core server implementation
├── core.py                  # Unified memory store
├── models.py                # Data models (MemoryEntity, MemoryRelation, MemoryContext)
├── database.py              # Database management
├── ai_extraction.py         # AI entity extraction
├── migration.py             # Migration utilities
├── migration_cli.py         # Migration command-line interface
├── tools/                   # Tool modules
│   ├── __init__.py
│   ├── base.py              # Base tool interface
│   ├── handoff/
│   │   ├── handoff.py       # Legacy handoff tool
│   │   └── unified_handoff_tool.py  # Enhanced handoff wrapper
│   ├── todo/
│   │   ├── todo.py          # Legacy todo tool
│   │   └── unified_todo_tool.py     # Enhanced todo wrapper
│   ├── knowledgebase/
│   │   ├── knowledgebase.py # Legacy knowledgebase tool
│   │   └── unified_knowledge_graph_tool.py  # Enhanced knowledge graph wrapper
│   ├── calendar/
│   │   └── calendar.py      # Calendar tool
│   ├── async_tasks/
│   │   └── async_tasks.py   # Async task management
│   ├── time_service/
│   │   └── time_service.py  # Time service
│   └── memory_graph/
│       └── memory_graph.py  # Memory graph tool
├── data/                    # Data storage
│   ├── memory.db            # Unified SQLite database
│   ├── async_tasks.jsonl    # Legacy JSONL files
│   ├── calendar.jsonl
│   ├── handoff.jsonl
│   ├── knowledgebase.jsonl
│   ├── memory_graph.jsonl
│   ├── time_service.jsonl
│   └── todo.jsonl
├── docs/                    # Documentation
│   ├── api_reference.md     # API documentation
│   ├── migration_guide.md   # Migration guide
│   └── ...                  # Other documentation
├── tests/                   # Test suites
│   ├── test_core.py         # Core functionality tests
│   ├── test_handoff.py      # Handoff tool tests
│   ├── test_todo.py         # Todo tool tests
│   └── ...                  # Other test files
├── pyproject.toml           # Project dependencies and config
├── uv.lock                  # Lockfile for uv
├── configure.sh             # Configuration script
├── start.sh                 # Startup script
└── README.md                # Project documentation
```
