# automation_list_workflows

## Description
List all registered automation workflows with optional filtering by enabled status

## Status
- **Enabled**: ✅ Yes
- **Tags**: view, workflow, automation, list, management

## Parameters

### Optional Parameters

#### `enabled_only` (boolean)
- **Title**: Enabled Only
- **Description**: No description
- **Default**: `False`

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "automation_list_workflows"
}
```

## Related Tools

- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_pause_workflow`: Pause an automation workflow to temporarily stop its execution without deleting it
- `automation_resume_workflow`: Resume a paused automation workflow to continue its scheduled execution
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

