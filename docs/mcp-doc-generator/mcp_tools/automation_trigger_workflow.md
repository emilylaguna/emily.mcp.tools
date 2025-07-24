# automation_trigger_workflow

## Description
Manually trigger an automation workflow with optional event data for immediate execution

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, manual, automation, trigger, execute

## Parameters

### Required Parameters

#### `workflow_id` (string)
- **Title**: Workflow Id
- **Description**: No description

### Optional Parameters

#### `event_data` (object | null)
- **Title**: Event Data
- **Description**: No description

## Tool Annotations


## Usage Example

```json
{
  "tool": "automation_trigger_workflow",
  "parameters": {
    "workflow_id": "example_value"
  }
}
```

## Related Tools

- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions
- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it

