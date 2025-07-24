# graph_delete_entity

## Description
Delete an entity and all its relations from the knowledge graph permanently

## Status
- **Enabled**: ✅ Yes
- **Tags**: remove, cleanup, graph, delete, entity

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

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "graph_delete_entity",
  "parameters": {
    "entity_id": "example_value"
  }
}
```

## Related Tools

- `graph_delete_relation`: Delete a specific relation between entities from the knowledge graph
- `todo_delete_task`: Permanently delete a task from the system
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions
- `graph_create_entity`: Create a new entity in the knowledge graph with specified properties and metadata
- `graph_get_entity`: Get detailed information about a specific entity by its ID including properties and metadata

