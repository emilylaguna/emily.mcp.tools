# graph_find_clusters

## Description
Find clusters of related entities using community detection algorithms for pattern discovery

## Status
- **Enabled**: ✅ Yes
- **Tags**: patterns, graph, community, detection, clusters

## Parameters

### Optional Parameters

#### `entity_type` (string | null)
- **Title**: Entity Type
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
  "tool": "graph_find_clusters"
}
```

## Related Tools

- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata

