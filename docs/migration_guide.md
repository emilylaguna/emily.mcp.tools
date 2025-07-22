# Migration Guide: JSONL to Unified Memory System

This guide helps you migrate your existing JSONL-based tool data (handoff, todo, memory_graph, knowledgebase) to the new unified SQLite + vector search memory system.

## Overview

The migration system converts your existing data while preserving all information, relationships, and timestamps. It also enhances your data with AI-powered entity extraction and cross-domain intelligence.

## Prerequisites

1. **Backup your data**: Always create backups before migration
2. **Install dependencies**: Ensure you have the required packages
3. **Check data format**: Verify your JSONL files are valid

## Quick Start

### 1. Backup Your Data

```bash
# Create a backup of your data directory
cp -r data/ data_backup_$(date +%Y%m%d_%H%M%S)/
```

### 2. Run Migration

```bash
# Full migration with backup
python migration_cli.py --data-dir data/ --db-path memory.db --backup

# Verbose output for detailed information
python migration_cli.py --data-dir data/ --db-path memory.db --backup --verbose

# Save migration report
python migration_cli.py --data-dir data/ --db-path memory.db --backup --output migration_report.json
```

### 3. Validate Migration

```bash
# Check migration results
python migration_cli.py --data-dir data/ --db-path memory.db --validate-only
```

## Migration Options

### Full Migration (Recommended)

Migrates all JSONL files in one operation:

```bash
python migration_cli.py --data-dir data/ --db-path memory.db --backup
```

**What happens:**
- Creates backup of all JSONL files
- Migrates handoff → contexts table
- Migrates todo → task entities with AI extraction
- Migrates memory_graph → entities and relations
- Migrates knowledgebase → file and function entities
- Validates data integrity
- Generates comprehensive report

### Incremental Migration

Migrate specific tools for testing or partial migration:

```bash
# Migrate only handoff data
python migration_cli.py --data-dir data/ --db-path memory.db --tool handoff

# Migrate only todo data
python migration_cli.py --data-dir data/ --db-path memory.db --tool todo

# Migrate only memory graph
python migration_cli.py --data-dir data/ --db-path memory.db --tool memory_graph

# Migrate only knowledgebase
python migration_cli.py --data-dir data/ --db-path memory.db --tool knowledgebase
```

### Validation Only

Check if migration was successful without running migration:

```bash
python migration_cli.py --data-dir data/ --db-path memory.db --validate-only
```

## Data Format Requirements

### Handoff Tool (handoff.jsonl)

```json
{
  "id": 1,
  "context": "Working on API authentication. Need to implement OAuth2 flow...",
  "created_at": "2024-01-15T10:30:00"
}
```

**Required fields:**
- `id`: Unique identifier
- `context`: Handoff content

**Optional fields:**
- `created_at`: ISO timestamp

### Todo Tool (todo.jsonl)

```json
{
  "id": 1,
  "title": "Fix database connection timeout",
  "description": "PostgreSQL connections timing out after 30 seconds",
  "priority": "high",
  "status": "todo",
  "tags": ["database", "urgent"],
  "created_at": "2024-01-15T09:00:00"
}
```

**Required fields:**
- `id`: Unique identifier
- `title`: Task title

**Optional fields:**
- `description`: Task description
- `priority`: Priority level (low, medium, high)
- `status`: Task status (todo, in_progress, done)
- `tags`: Array of tags
- `created_at`: ISO timestamp

### Memory Graph (memory_graph.jsonl)

```json
{
  "type": "entity",
  "id": "person_alice",
  "name": "Alice Johnson",
  "entity_type": "person",
  "metadata": {"role": "Frontend Developer"},
  "created_at": "2024-01-10T14:00:00"
}
{
  "type": "relation",
  "source": "person_alice",
  "target": "project_website",
  "relation": "works_on",
  "strength": 0.8,
  "created_at": "2024-01-10T14:05:00"
}
```

**Entity format:**
- `type`: Must be "entity"
- `id`: Unique identifier
- `name`: Entity name
- `entity_type`: Type of entity (person, project, etc.)
- `metadata`: Optional metadata object
- `created_at`: ISO timestamp

**Relation format:**
- `type`: Must be "relation"
- `source`: Source entity ID
- `target`: Target entity ID
- `relation`: Relation type
- `strength`: Relation strength (0.0-1.0)
- `created_at`: ISO timestamp

### Knowledgebase (knowledgebase.jsonl)

```json
{
  "id": "file_api_auth_py",
  "type": "file",
  "path": "src/auth/authentication.py",
  "content": "Contains OAuth2 implementation...",
  "functions": ["authenticate_user", "validate_token"],
  "created_at": "2024-01-12T16:00:00"
}
```

**Required fields:**
- `id`: Unique identifier
- `type`: Must be "file"
- `path`: File path

**Optional fields:**
- `content`: File content or description
- `functions`: Array of function names
- `created_at`: ISO timestamp

## Migration Process Details

### 1. Handoff Migration

**Converts to:** MemoryContext objects
**Enhancement:** AI-powered content analysis and entity extraction

```python
# Before migration
{
  "id": 1,
  "context": "Working on API authentication..."
}

# After migration
MemoryContext(
  id="handoff_1",
  type="handoff",
  content="Working on API authentication...",
  metadata={
    'migrated_from': 'handoff.jsonl',
    'original_id': 1,
    'migration_date': '2024-01-20T10:30:00'
  }
)
```

### 2. Todo Migration

**Converts to:** MemoryEntity (task type)
**Enhancement:** AI entity extraction from task content

```python
# Before migration
{
  "id": 1,
  "title": "Fix database connection timeout",
  "description": "PostgreSQL connections timing out..."
}

# After migration
MemoryEntity(
  id="task_1",
  type="task",
  name="Fix database connection timeout",
  content="PostgreSQL connections timing out...",
  metadata={
    'priority': 'high',
    'status': 'todo',
    'migrated_from': 'todo.jsonl',
    'original_id': 1
  },
  tags=["database", "urgent"]
)
```

**AI Enhancement:** Automatically extracts entities like "PostgreSQL" and creates relationships.

### 3. Memory Graph Migration

**Converts to:** MemoryEntity and MemoryRelation objects
**Preserves:** All relationships and entity metadata

```python
# Before migration
{
  "type": "entity",
  "id": "person_alice",
  "name": "Alice Johnson",
  "entity_type": "person"
}

# After migration
MemoryEntity(
  id="mg_person_alice",
  type="person",
  name="Alice Johnson",
  metadata={
    'role': 'Frontend Developer',
    'migrated_from': 'memory_graph.jsonl',
    'original_id': 'person_alice'
  }
)
```

### 4. Knowledgebase Migration

**Converts to:** MemoryEntity (file and function types)
**Enhancement:** Language detection and file-function relationships

```python
# Before migration
{
  "id": "file_api_auth_py",
  "path": "src/auth/authentication.py",
  "functions": ["authenticate_user", "validate_token"]
}

# After migration
MemoryEntity(
  id="kb_file_api_auth_py",
  type="file",
  name="src/auth/authentication.py",
  metadata={
    'language': 'python',
    'migrated_from': 'knowledgebase.jsonl',
    'original_id': 'file_api_auth_py'
  }
)
```

**Plus function entities and relationships:**
- Creates separate entities for each function
- Links functions to parent files with "contains" relationships

## Migration Report

The migration system generates a comprehensive report:

```json
{
  "migration_timestamp": "2024-01-20T10:30:00",
  "summary": {
    "tools_processed": 4,
    "tools_successful": 4,
    "tools_failed": 0,
    "total_records_migrated": 15,
    "total_errors": 0
  },
  "validation": {
    "validation_passed": true,
    "database_counts": {
      "entities": 12,
      "relations": 8,
      "contexts": 3
    }
  },
  "results": {
    "handoff": {
      "status": "completed",
      "migrated_count": 3,
      "error_count": 0
    },
    "todo": {
      "status": "completed", 
      "migrated_count": 5,
      "error_count": 0
    }
  }
}
```

## Troubleshooting

### Common Issues

**1. File not found errors**
```
Error: Data directory does not exist: /path/to/data
```
**Solution:** Verify the data directory path and ensure JSONL files exist.

**2. JSON parsing errors**
```
Line 5: Expecting property name enclosed in double quotes
```
**Solution:** Check JSONL file format. Each line must be valid JSON.

**3. Database errors**
```
Database validation failed: no such table: entity_data
```
**Solution:** Ensure the database path is writable and the migration creates the schema.

**4. Permission errors**
```
Permission denied: /path/to/database.db
```
**Solution:** Check file permissions and ensure write access to the database directory.

### Error Recovery

**1. Partial migration errors**
- Migration continues on individual record errors
- Check the error log in the migration report
- Fix data issues and re-run migration

**2. Rollback procedure**
```bash
# Restore from backup
cp -r data_backup_YYYYMMDD_HHMMSS/* data/

# Remove migrated database
rm memory.db
```

**3. Re-migration**
```bash
# Re-run migration after fixing issues
python migration_cli.py --data-dir data/ --db-path memory.db --backup
```

## Post-Migration

### 1. Verify Data Integrity

```bash
# Check migration results
python migration_cli.py --data-dir data/ --db-path memory.db --validate-only
```

### 2. Test New Functionality

```python
from core import UnifiedMemoryStore

# Load migrated data
store = UnifiedMemoryStore("memory.db")

# Search across all data types
results = store.search("PostgreSQL")
print(f"Found {len(results)} related items")

# Get cross-domain relationships
relations = store.get_relations_by_type("relates_to")
print(f"Found {len(relations)} relationships")
```

### 3. Explore AI Enhancements

```python
# Check AI-extracted entities
tech_entities = store.search_entities("tech")
print(f"AI extracted {len(tech_entities)} technology entities")

# View enhanced contexts
contexts = store.search_contexts("handoff")
for context in contexts:
    print(f"Context: {context.content}")
    print(f"AI summary: {context.metadata.get('ai_summary', 'N/A')}")
```

## Benefits After Migration

1. **Unified Search**: Search across all data types with one query
2. **AI Intelligence**: Automatic entity extraction and relationship discovery
3. **Cross-Domain Insights**: Find connections between tasks, people, and code
4. **Better Performance**: SQLite + vector search for faster queries
5. **Enhanced Metadata**: Rich tagging and relationship information

## Support

If you encounter issues during migration:

1. Check the migration report for detailed error information
2. Verify your JSONL file formats match the requirements
3. Ensure sufficient disk space for the database
4. Check file permissions and database access rights

For additional help, refer to the test files for examples of valid data formats. 