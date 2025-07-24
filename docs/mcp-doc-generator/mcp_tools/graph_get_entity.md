# graph_get_entity

## Description
Get detailed information about a specific entity by its ID including properties and metadata

## Status
- **Enabled**: ✅ Yes
- **Tags**: details, get, graph, retrieve, entity

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
  "tool": "graph_get_entity",
  "parameters": {
    "entity_id": "example_value"
  }
}
```

## Related Tools

- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_get_relations`: Get all relations for a specific entity with optional filtering by relation types
- `graph_delete_entity`: Delete an entity and all its relations from the knowledge graph permanently
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms

