# graph_shortest_path

## Description
Find the shortest path between two entities using graph algorithms for relationship discovery

## Status
- **Enabled**: ✅ Yes
- **Tags**: connection, graph, algorithm, path, shortest

## Parameters

### Required Parameters

#### `source_id` (string)
- **Title**: Source Id
- **Description**: No description

#### `target_id` (string)
- **Title**: Target Id
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
  "tool": "graph_shortest_path",
  "parameters": {
    "source_id": "example_value",
    "target_id": "example_value"
  }
}
```

## Related Tools

- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_delete_relation`: Delete a specific relation between entities from the knowledge graph
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata

