# graph_search

## Description
Search for entities in the knowledge graph using semantic search with optional type filtering

## Status
- **Enabled**: ✅ Yes
- **Tags**: semantic, filter, search, graph, entities

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

### Optional Parameters

#### `entity_type` (string | null)
- **Title**: Entity Type
- **Description**: No description

#### `limit` (integer)
- **Title**: Limit
- **Description**: No description
- **Default**: `20`

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "graph_search",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_get_relations`: Get all relations for a specific entity with optional filtering by relation types
- `todo_quick_find`: Quick semantic search across tasks, projects, and areas using AI-powered search capabilities
- `todo_search_tasks`: Search tasks with advanced filtering capabilities including metadata, tags, and content search
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata

