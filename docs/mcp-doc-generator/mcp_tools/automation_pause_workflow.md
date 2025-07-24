# automation_pause_workflow

## Description
Pause an automation workflow to temporarily stop its execution without deleting it

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, pause, automation, control, management

## Parameters

### Required Parameters

#### `workflow_id` (string)
- **Title**: Workflow Id
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "automation_pause_workflow",
  "parameters": {
    "workflow_id": "example_value"
  }
}
```

## Related Tools

- `automation_resume_workflow`: Resume a paused automation workflow to continue its scheduled execution
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

