# automation_resume_workflow

## Description
Resume a paused automation workflow to continue its scheduled execution

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, automation, control, resume, management

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
  "tool": "automation_resume_workflow",
  "parameters": {
    "workflow_id": "example_value"
  }
}
```

## Related Tools

- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

