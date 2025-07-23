# automation_get_workflow

## Description
Get detailed information about a specific automation workflow including configuration and status

## Status
- **Enabled**: ✅ Yes
- **Tags**: view, workflow, details, automation, get

## Parameters

### Required Parameters

#### `workflow_id` (string)
- **Title**: Workflow Id
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "automation_get_workflow",
  "parameters": {
    "workflow_id": "example_value"
  }
}
```

## Related Tools

- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_run`: Get detailed information about a specific workflow run including status, logs, and results
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions
- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it

