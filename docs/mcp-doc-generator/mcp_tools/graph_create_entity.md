# graph_create_entity

## Description
Create a new entity in the knowledge graph with specified properties and metadata

## Status
- **Enabled**: ✅ Yes
- **Tags**: data, graph, knowledge, create, entity

## Parameters

### Required Parameters

#### `payload` (object)
- **Title**: Payload
- **Description**: No description

### Optional Parameters

#### `ctx` (null)
- **Title**: Ctx
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "graph_create_entity",
  "parameters": {
    "payload": "value"
  }
}
```

## Related Tools

- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata
- `graph_get_relations`: Get all relations for a specific entity with optional filtering by relation types
- `graph_delete_entity`: Delete an entity and all its relations from the knowledge graph permanently

