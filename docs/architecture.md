# Architecture Guide

## Overview

The Emily Tools unified memory architecture provides a single, intelligent backend for all productivity tools, enabling cross-domain intelligence and AI-powered features.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MCP Protocol Handler                                │   │
│  │ - Tool registration                                 │   │
│  │ - Request routing                                   │   │
│  │ - Response formatting                               │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                Tool Wrapper Layer                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Handoff     │ │ Todo        │ │ Knowledge   │          │
│  │ Wrapper     │ │ Wrapper     │ │ Graph       │          │
│  │ - AI        │ │ - Things    │ │ - Multi-    │          │
│  │   enhance   │ │   style     │ │   codebase  │          │
│  │ - Context   │ │ - Smart     │ │ - Entity    │          │
│  │   preserve  │ │   search    │ │   linking   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│              Unified Memory Store                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ SQLite      │ │ Vector      │ │ AI          │          │
│  │ Database    │ │ Search      │ │ Extraction  │          │
│  │ - Entities  │ │ - Semantic  │ │ - Entity    │          │
│  │ - Relations │ │   search    │ │   detection │          │
│  │ - Contexts  │ │ - Embedding │ │ - Topic     │          │
│  │ - Metadata  │ │   storage   │ │   analysis  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. UnifiedMemoryStore

The central component that provides intelligent storage and retrieval capabilities.

**Key Features:**
- **Entity Management**: CRUD operations for all entity types
- **Relationship Management**: Create and manage entity relationships
- **Context Management**: Store and retrieve contextual information
- **Vector Search**: Semantic search using embeddings
- **AI Enhancement**: Automatic entity extraction and content enhancement

**Architecture:**
```python
class UnifiedMemoryStore:
    def __init__(self, db_path, embedding_model=None, enable_vector_search=True, enable_ai_extraction=True):
        self.db_manager = DatabaseManager(db_path)
        self.embedding_model = self._setup_embedding_model(embedding_model)
        self.ai_extractor = self._setup_ai_extraction()
        self._setup_schema()
```

#### 2. Database Layer

**SQLite Database Schema:**

```sql
-- Core entities table
CREATE TABLE memory_entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Relationships table
CREATE TABLE memory_relations (
    relation_id TEXT PRIMARY KEY,
    source_entity_id TEXT NOT NULL,
    target_entity_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    metadata TEXT,  -- JSON object
    created_at TEXT NOT NULL,
    FOREIGN KEY (source_entity_id) REFERENCES memory_entities(entity_id),
    FOREIGN KEY (target_entity_id) REFERENCES memory_entities(entity_id)
);

-- Contexts table
CREATE TABLE memory_contexts (
    context_id TEXT PRIMARY KEY,
    context_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    metadata TEXT,  -- JSON object
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Vector embeddings table
CREATE VIRTUAL TABLE memory_embeddings USING vss0(
    id TEXT PRIMARY KEY,
    embedding BLOB,
    FOREIGN KEY (id) REFERENCES memory_entities(entity_id)
);
```

**Indexes:**
```sql
CREATE INDEX idx_entities_type ON memory_entities(entity_type);
CREATE INDEX idx_entities_tags ON memory_entities(tags);
CREATE INDEX idx_entities_created ON memory_entities(created_at);
CREATE INDEX idx_relations_source ON memory_relations(source_entity_id);
CREATE INDEX idx_relations_target ON memory_relations(target_entity_id);
CREATE INDEX idx_relations_type ON memory_relations(relation_type);
CREATE INDEX idx_contexts_type ON memory_contexts(context_type);
CREATE INDEX idx_contexts_created ON memory_contexts(created_at);
```

#### 3. Vector Search Layer

**Embedding Model:**
- **Default**: `all-MiniLM-L6-v2` (384 dimensions)
- **Alternative**: `all-mpnet-base-v2` (768 dimensions)
- **Storage**: SQLite with sqlite-vec extension

**Search Algorithm:**
```python
def search(self, query: str, filters: Dict = None, limit: int = 10) -> List[Dict]:
    # 1. Generate query embedding
    query_embedding = self._generate_embedding(query)
    
    # 2. Vector search for semantic similarity
    vector_results = self._vector_search(query_embedding, filters, limit)
    
    # 3. Full-text search for keyword matching
    fts_results = self._fts_search(query, filters, limit)
    
    # 4. Combine and rank results
    combined_results = self._combine_search_results(vector_results, fts_results)
    
    return combined_results[:limit]
```

#### 4. AI Extraction Layer

**Entity Extraction:**
- **People**: Names, emails, roles
- **Projects**: Project names, descriptions
- **Files**: File paths, extensions, content types
- **Technologies**: Programming languages, frameworks, tools
- **Actions**: Tasks, deadlines, priorities

**Content Enhancement:**
```python
def extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
    # 1. Use spaCy for NER
    entities = self.ai_extractor.extract_entities(text)
    
    # 2. Use regex patterns for specific entities
    patterns = self.ai_extractor.extract_with_patterns(text)
    
    # 3. Use LLM for complex extraction
    llm_entities = self.ai_extractor.extract_with_llm(text)
    
    # 4. Combine and deduplicate
    return self.entity_matcher.merge_entities(entities + patterns + llm_entities)
```

## Tool Wrapper Architecture

### Design Pattern

Each tool wrapper follows the same pattern:

```python
class UnifiedToolWrapper:
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.store = memory_store
    
    def legacy_method(self, **kwargs):
        # 1. Convert legacy format to unified format
        entity = self._convert_to_entity(kwargs)
        
        # 2. Enhance with AI
        enhanced_entity = self._enhance_with_ai(entity)
        
        # 3. Save to unified store
        saved_entity = self.store.save_entity(enhanced_entity)
        
        # 4. Convert back to legacy format for compatibility
        return self._convert_to_legacy_format(saved_entity)
    
    def enhanced_method(self, **kwargs):
        # New enhanced methods with AI capabilities
        pass
```

### Handoff Tool Wrapper

**Features:**
- **Context Preservation**: Save conversation context
- **AI Enhancement**: Extract entities and topics
- **Semantic Search**: Find related contexts
- **Timeline View**: Chronological context history

**API:**
```python
# Legacy compatibility
handoff_save_context(context: str) -> Dict
handoff_get_latest_context() -> Optional[Dict]
handoff_list_contexts(limit: int) -> List[Dict]

# Enhanced features
handoff_search_contexts(query: str) -> List[Dict]
handoff_get_context_insights(context_id: str) -> Dict
handoff_suggest_related_contexts(context_id: str) -> List[Dict]
```

### Todo Tool Wrapper

**Features:**
- **Things-style Interface**: Familiar task management
- **Smart Search**: Semantic task search
- **Context Awareness**: Link tasks to conversations and code
- **AI Suggestions**: Automatic task categorization

**API:**
```python
# Legacy compatibility
todo_create_task(title: str, description: str) -> Dict
todo_update_task(task_id: str, **kwargs) -> Dict
todo_get_task(task_id: str) -> Optional[Dict]
todo_list_tasks() -> List[Dict]

# Enhanced features
todo_search_tasks(query: str, filters: Dict) -> List[Dict]
todo_suggest_related_tasks(task_id: str) -> List[Dict]
todo_extract_tasks_from_text(text: str) -> List[Dict]
```

### Knowledge Graph Wrapper

**Features:**
- **Multi-codebase Support**: Multiple repository knowledge
- **Entity Linking**: Automatic relationship discovery
- **Code Intelligence**: Function and class understanding
- **Cross-references**: Link code to documentation and tasks

**API:**
```python
# Legacy compatibility
knowledge_add_entity(name: str, entity_type: str, content: str) -> Dict
knowledge_get_entity(entity_id: str) -> Optional[Dict]
knowledge_search(query: str) -> List[Dict]

# Enhanced features
knowledge_add_relation(source_id: str, target_id: str, relation_type: str) -> Dict
knowledge_get_related_entities(entity_id: str) -> List[Dict]
knowledge_suggest_entities(text: str) -> List[Dict]
```

## Data Flow

### 1. Entity Creation Flow

```
User Input → Tool Wrapper → AI Enhancement → Unified Store → Response
     ↓              ↓              ↓              ↓           ↓
  "Create task" → Convert → Extract entities → Save entity → Enhanced task
```

### 2. Search Flow

```
User Query → Tool Wrapper → Unified Store → Vector Search → AI Ranking → Response
     ↓              ↓              ↓              ↓              ↓           ↓
  "Find auth" → Parse query → Generate embedding → Semantic search → Rank results → Enhanced results
```

### 3. Migration Flow

```
JSONL Files → Migration CLI → JSONLMigrator → Unified Store → Verification
     ↓              ↓              ↓              ↓              ↓
  Legacy data → Parse files → Convert format → Save entities → Verify integrity
```

## Performance Considerations

### Database Optimization

1. **Indexing Strategy:**
   - Primary indexes on entity_id, relation_id, context_id
   - Secondary indexes on frequently queried fields
   - Composite indexes for complex queries

2. **Connection Management:**
   - Thread-local connections for concurrency
   - Connection pooling for high-load scenarios
   - Proper connection cleanup

3. **Query Optimization:**
   - Prepared statements for repeated queries
   - Efficient JOIN operations
   - Query result caching

### Vector Search Optimization

1. **Embedding Management:**
   - Batch embedding generation
   - Embedding caching
   - Model size optimization

2. **Search Performance:**
   - Approximate nearest neighbor search
   - Result ranking optimization
   - Query preprocessing

### AI Enhancement Optimization

1. **Extraction Caching:**
   - Cache extracted entities
   - Incremental extraction
   - Background processing

2. **Model Optimization:**
   - Use smaller models for basic extraction
   - Batch processing for efficiency
   - Graceful degradation

## Security Considerations

### Data Protection

1. **Local Storage:**
   - All data stored locally
   - No external data transmission
   - File system permissions

2. **Access Control:**
   - Process-level access control
   - File system security
   - Database file permissions

### AI Model Security

1. **Model Validation:**
   - Use trusted model sources
   - Model integrity verification
   - Secure model loading

2. **Input Validation:**
   - Sanitize user inputs
   - Prevent injection attacks
   - Validate data formats

## Scalability

### Horizontal Scaling

1. **Database Scaling:**
   - SQLite to PostgreSQL migration path
   - Distributed database support
   - Read replicas for search

2. **Application Scaling:**
   - Stateless application design
   - Load balancing support
   - Microservice architecture

### Vertical Scaling

1. **Memory Optimization:**
   - Efficient data structures
   - Memory pooling
   - Garbage collection optimization

2. **CPU Optimization:**
   - Async processing
   - Background tasks
   - Parallel processing

## Monitoring and Observability

### Metrics

1. **Performance Metrics:**
   - Query response times
   - Database operation latency
   - Memory usage

2. **Business Metrics:**
   - Entity creation rates
   - Search query patterns
   - AI enhancement success rates

### Logging

1. **Application Logs:**
   - Structured logging
   - Log levels
   - Log rotation

2. **Database Logs:**
   - Query performance
   - Error tracking
   - Connection monitoring

## Future Enhancements

### Planned Features

1. **Advanced AI:**
   - Custom fine-tuned models
   - Multi-modal understanding
   - Predictive analytics

2. **Enhanced Search:**
   - Graph-based search
   - Temporal search
   - Collaborative filtering

3. **Integration:**
   - External API integration
   - Plugin system
   - Webhook support

### Architecture Evolution

1. **Microservices:**
   - Service decomposition
   - API gateway
   - Service mesh

2. **Cloud Native:**
   - Containerization
   - Kubernetes deployment
   - Cloud storage integration 