# automation_delete_workflow

## Description
Permanently delete an automation workflow and stop all its scheduled executions

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, automation, remove, cleanup, delete

## Parameters

### Required Parameters

#### `workflow_id` (string)
- **Title**: Workflow Id
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "automation_delete_workflow",
  "parameters": {
    "workflow_id": "example_value"
  }
}
```

## Related Tools

- `todo_delete_task`: Permanently delete a task from the system
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it

