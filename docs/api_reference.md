# API Reference

## UnifiedMemoryStore

The core memory store that provides intelligent storage and retrieval capabilities.

### Initialization

```python
from core import UnifiedMemoryStore

# Basic initialization
store = UnifiedMemoryStore("data/memory.db")

# With custom settings
store = UnifiedMemoryStore(
    db_path="data/memory.db",
    embedding_model="all-MiniLM-L6-v2",
    embedding_dimension=384,
    enable_vector_search=True,
    enable_ai_extraction=True
)
```

### Core Methods

#### Entity Management

- `save_entity(entity: MemoryEntity) -> MemoryEntity`
  - Save a new entity to the memory store
  - Returns the saved entity with generated ID and timestamps

- `get_entity(entity_id: str) -> Optional[MemoryEntity]`
  - Retrieve an entity by its ID
  - Returns None if entity not found

- `update_entity(entity: MemoryEntity) -> MemoryEntity`
  - Update an existing entity
  - Returns the updated entity

- `delete_entity(entity_id: str) -> bool`
  - Delete an entity by its ID
  - Returns True if successful, False otherwise

#### Search & Retrieval

- `search(query: str, filters: Optional[Dict] = None, limit: int = 10) -> List[Dict]`
  - Perform semantic search across all entities
  - Supports filters by type, tags, metadata, dates
  - Returns list of matching entities with scores

- `search_entities(entity_type: str, filters: Optional[Dict] = None, limit: int = 20) -> List[MemoryEntity]`
  - Search for entities of a specific type
  - Returns list of MemoryEntity objects

- `get_all_entities(entity_type: Optional[str] = None, limit: int = 1000) -> List[Dict]`
  - Get all entities, optionally filtered by type
  - Returns list of entity dictionaries

#### Relationship Management

- `save_relation(relation: MemoryRelation) -> MemoryRelation`
  - Save a relationship between entities
  - Returns the saved relation with generated ID

- `get_related(entity_id: str, relation_types: Optional[List[str]] = None) -> List[Dict]`
  - Get entities related to a specific entity
  - Optionally filter by relation types
  - Returns list of related entities with relation info

- `delete_relation(relation_id: str) -> bool`
  - Delete a relationship by its ID
  - Returns True if successful, False otherwise

#### Context Management

- `save_context(context: MemoryContext) -> MemoryContext`
  - Save a context (conversation, session, etc.)
  - Returns the saved context with generated ID

- `get_context(context_id: str) -> Optional[MemoryContext]`
  - Retrieve a context by its ID
  - Returns None if context not found

- `search_contexts(query: str, filters: Optional[Dict] = None) -> List[MemoryContext]`
  - Search contexts by content
  - Returns list of matching contexts

#### AI Features

- `extract_entities_from_text(text: str) -> List[Dict[str, Any]]`
  - Extract entities (people, projects, files, etc.) from text
  - Returns list of extracted entities with confidence scores

- `extract_topics_from_text(text: str) -> List[str]`
  - Extract topics from text
  - Returns list of identified topics

- `generate_summary(text: str, max_length: int = 200) -> str`
  - Generate a summary of text
  - Returns summarized text

- `extract_action_items(text: str) -> List[str]`
  - Extract action items from text
  - Returns list of identified action items

## MemoryEntity

Data model for entities in the memory store.

### Fields

- `entity_id: str` - Unique identifier (UUID)
- `entity_type: str` - Type of entity (task, person, project, file, etc.)
- `title: str` - Human-readable title
- `content: str` - Main content/description
- `tags: List[str]` - Tags for categorization
- `metadata: Dict[str, Any]` - Additional metadata as JSON
- `created_at: datetime` - Creation timestamp (UTC)
- `updated_at: datetime` - Last update timestamp (UTC)

### Entity Types

Supported entity types:
- `task` - Tasks and todos
- `person` - People and contacts
- `project` - Projects and initiatives
- `file` - Files and documents
- `conversation` - Chat conversations
- `code` - Code snippets and functions
- `meeting` - Meeting records
- `note` - Notes and documentation
- `url` - URLs and links
- `tool` - Tools and utilities

### Example

```python
from models import MemoryEntity
from datetime import datetime, UTC

entity = MemoryEntity(
    entity_id="550e8400-e29b-41d4-a716-446655440000",
    entity_type="task",
    title="Implement authentication",
    content="Add OAuth2 support to the API",
    tags=["auth", "api", "security"],
    metadata={
        "priority": "high",
        "status": "in_progress",
        "assignee": "john@example.com"
    },
    created_at=datetime.now(UTC),
    updated_at=datetime.now(UTC)
)
```

## MemoryRelation

Data model for relationships between entities.

### Fields

- `relation_id: str` - Unique identifier (UUID)
- `source_entity_id: str` - Source entity ID
- `target_entity_id: str` - Target entity ID
- `relation_type: str` - Type of relationship
- `metadata: Dict[str, Any]` - Additional metadata as JSON
- `created_at: datetime` - Creation timestamp (UTC)

### Relation Types

Supported relation types:
- `relates_to` - General relationship
- `contains` - Contains/is contained by
- `assigned_to` - Assignment relationship
- `mentions` - Mentions/references
- `references` - Code or document references
- `depends_on` - Dependency relationship
- `similar_to` - Similarity relationship
- `part_of` - Part/whole relationship
- `created_by` - Creation relationship
- `updated_by` - Update relationship
- `follows` - Sequential relationship

### Example

```python
from models import MemoryRelation
from datetime import datetime, UTC

relation = MemoryRelation(
    relation_id="550e8400-e29b-41d4-a716-446655440001",
    source_entity_id="550e8400-e29b-41d4-a716-446655440000",
    target_entity_id="550e8400-e29b-41d4-a716-446655440002",
    relation_type="assigned_to",
    metadata={
        "assigned_date": "2024-01-15",
        "priority": "high"
    },
    created_at=datetime.now(UTC)
)
```

## MemoryContext

Data model for contextual information.

### Fields

- `context_id: str` - Unique identifier (UUID)
- `context_type: str` - Type of context
- `title: str` - Context title
- `content: str` - Context content
- `metadata: Dict[str, Any]` - Additional metadata as JSON
- `created_at: datetime` - Creation timestamp (UTC)
- `updated_at: datetime` - Last update timestamp (UTC)

### Context Types

Supported context types:
- `handoff` - Session handoff context
- `meeting` - Meeting context
- `debug_session` - Debugging session
- `conversation` - Chat conversation
- `work_session` - Work session
- `research` - Research session
- `planning` - Planning session

### Example

```python
from models import MemoryContext
from datetime import datetime, UTC

context = MemoryContext(
    context_id="550e8400-e29b-41d4-a716-446655440003",
    context_type="handoff",
    title="Authentication Implementation Session",
    content="Working on OAuth2 implementation for the API. Current status: basic structure in place, need to add token validation.",
    metadata={
        "session_duration": "2h 30m",
        "participants": ["john@example.com"],
        "next_steps": ["Add token validation", "Test with real OAuth provider"]
    },
    created_at=datetime.now(UTC),
    updated_at=datetime.now(UTC)
)
```

## Tool Wrappers

### UnifiedHandoffTool

Enhanced handoff tool with AI capabilities.

#### Methods

- `save_context(context: str, metadata: Optional[Dict] = None) -> Dict`
  - Save context with AI enhancement
  - Returns saved context with extracted entities

- `get_latest_context() -> Optional[Dict]`
  - Get the most recent context
  - Returns enhanced context with AI insights

- `list_contexts(limit: int = 10) -> List[Dict]`
  - List recent contexts
  - Returns list of contexts with summaries

### UnifiedTodoTool

Enhanced todo tool with cool features.

#### Methods

- `create_task(title: str, description: Optional[str] = None, **kwargs) -> Dict`
  - Create a new task with AI enhancement
  - Returns created task with extracted entities

- `update_task(task_id: str, **kwargs) -> Dict`
  - Update an existing task
  - Returns updated task

- `search_tasks(query: str, filters: Optional[Dict] = None) -> List[Dict]`
  - Search tasks with semantic search
  - Returns list of matching tasks

- `get_task(task_id: str) -> Optional[Dict]`
  - Get a specific task by ID
  - Returns task details

### UnifiedKnowledgeGraphTool

Enhanced knowledge graph tool.

#### Methods

- `add_entity(name: str, entity_type: str, content: str, **kwargs) -> Dict`
  - Add an entity to the knowledge graph
  - Returns created entity with AI enhancement

- `search(query: str, filters: Optional[Dict] = None) -> List[Dict]`
  - Search knowledge graph
  - Returns list of matching entities

- `get_entity(entity_id: str) -> Optional[Dict]`
  - Get entity by ID
  - Returns entity details

- `add_relation(source_id: str, target_id: str, relation_type: str, **kwargs) -> Dict`
  - Add relationship between entities
  - Returns created relation

## Error Handling

All methods return appropriate error responses:

```python
# Example error response
{
    "error": "Entity not found",
    "error_code": "ENTITY_NOT_FOUND",
    "details": "Entity with ID '123' does not exist"
}
```

## Performance Considerations

- Use batch operations for large datasets
- Enable vector search only when needed
- Use appropriate limits in search queries
- Consider connection pooling for high concurrency
- Monitor memory usage with large embedding models

## Configuration

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

- **memory_entities**: All entities with metadata
- **memory_relations**: Relationships between entities
- **memory_contexts**: Contextual information
- **memory_embeddings**: Vector embeddings for semantic search

## Examples

### Basic Usage

```python
from core import UnifiedMemoryStore
from models import MemoryEntity

# Initialize store
store = UnifiedMemoryStore("data/memory.db")

# Create entity
entity = MemoryEntity(
    entity_type="task",
    title="Implement authentication",
    content="Add OAuth2 support to the API",
    tags=["auth", "api"]
)

# Save entity
saved_entity = store.save_entity(entity)

# Search for related content
results = store.search("authentication OAuth2")
```

### Advanced Search

```python
# Search with filters
results = store.search(
    query="authentication",
    filters={
        "entity_type": "task",
        "tags": ["auth"],
        "metadata": {"priority": "high"}
    },
    limit=20
)
```

### AI Enhancement

```python
# Extract entities from text
entities = store.extract_entities_from_text(
    "John is working on the authentication project with OAuth2"
)

# Generate summary
summary = store.generate_summary(
    "Long text content here...",
    max_length=200
)
``` 