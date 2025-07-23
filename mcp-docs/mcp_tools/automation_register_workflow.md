# automation_register_workflow

## Description
Register a new automation workflow with triggers, conditions, and actions

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, automation, configuration, register, create

## Parameters

### Required Parameters

#### `workflow_definition` (object)
- **Title**: Workflow Definition
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "automation_register_workflow",
  "parameters": {
    "workflow_definition": "value"
  }
}
```

## Related Tools

- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions
- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it
- `automation_resume_workflow`: Resume a paused automation workflow to continue its scheduled execution

