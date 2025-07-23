# graph_create_relation

## Description
Create a new relation between two entities with specified type, strength, and metadata

## Status
- **Enabled**: ✅ Yes
- **Tags**: connection, graph, knowledge, relation, create

## Parameters

### Required Parameters

#### `source_id` (string)
- **Title**: Source Id
- **Description**: No description

#### `target_id` (string)
- **Title**: Target Id
- **Description**: No description

#### `relation_type` (string)
- **Title**: Relation Type
- **Description**: No description

### Optional Parameters

#### `strength` (number)
- **Title**: Strength
- **Description**: No description
- **Default**: `1.0`

#### `metadata` (object | null)
- **Title**: Metadata
- **Description**: No description

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "graph_create_relation",
  "parameters": {
    "source_id": "example_value",
    "target_id": "example_value",
    "relation_type": "example_value"
  }
}
```

## Related Tools

- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_delete_relation`: Delete a specific relation between entities from the knowledge graph
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_shortest_path`: Find the shortest path between two entities using graph algorithms for relationship discovery
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering

