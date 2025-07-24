# graph_find_related

## Description
Find entities related to a given entity within a specified depth using graph traversal algorithms

## Status
- **Enabled**: ✅ Yes
- **Tags**: graph, search, knowledge, relationships, traversal

## Parameters

### Required Parameters

#### `entity_id` (string)
- **Title**: Entity Id
- **Description**: No description

### Optional Parameters

#### `depth` (integer)
- **Title**: Depth
- **Description**: No description
- **Default**: `2`

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "graph_find_related",
  "parameters": {
    "entity_id": "example_value"
  }
}
```

## Related Tools

- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata
- `graph_get_relations`: Get all relations for a specific entity with optional filtering by relation types

