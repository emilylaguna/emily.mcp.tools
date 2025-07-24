# graph_delete_relation

## Description
Delete a specific relation between entities from the knowledge graph

## Status
- **Enabled**: ✅ Yes
- **Tags**: remove, connection, graph, relation, delete

## Parameters

### Required Parameters

#### `relation_id` (string)
- **Title**: Relation Id
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
  "tool": "graph_delete_relation",
  "parameters": {
    "relation_id": "example_value"
  }
}
```

## Related Tools

- `graph_create_relation`: Create a new relation between two entities with specified type, strength, and metadata
- `graph_delete_entity`: Delete an entity and all its relations from the knowledge graph permanently
- `graph_shortest_path`: Find the shortest path between two entities using graph algorithms for relationship discovery
- `todo_delete_task`: Permanently delete a task from the system
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

