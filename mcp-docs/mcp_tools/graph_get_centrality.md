# graph_get_centrality

## Description
Get centrality score for an entity to measure its importance and influence in the knowledge graph

## Status
- **Enabled**: ✅ Yes
- **Tags**: centrality, importance, graph, influence, metrics

## Parameters

### Required Parameters

#### `entity_id` (string)
- **Title**: Entity Id
- **Description**: No description

### Optional Parameters

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "graph_get_centrality",
  "parameters": {
    "entity_id": "example_value"
  }
}
```

## Related Tools

- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata

