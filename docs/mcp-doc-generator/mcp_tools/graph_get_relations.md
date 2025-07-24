# graph_get_relations

## Description
Get all relations for a specific entity with optional filtering by relation types

## Status
- **Enabled**: ✅ Yes
- **Tags**: filter, graph, connections, relations, entity

## Parameters

### Required Parameters

#### `entity_id` (string)
- **Title**: Entity Id
- **Description**: No description

### Optional Parameters

#### `relation_types` (array | null)
- **Title**: Relation Types
- **Description**: No description

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "graph_get_relations",
  "parameters": {
    "entity_id": "example_value"
  }
}
```

## Related Tools

- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata
- `graph_delete_entity`: Delete an entity and all its relations from the knowledge graph permanently
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms

