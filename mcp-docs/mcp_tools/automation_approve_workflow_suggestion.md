# automation_approve_workflow_suggestion

## Description
Approve and implement a workflow suggestion to create an active automation workflow

## Status
- **Enabled**: ✅ Yes
- **Tags**: approve, workflow, automation, implement, suggestions

## Parameters

### Required Parameters

#### `suggestion_id` (string)
- **Title**: Suggestion Id
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "automation_approve_workflow_suggestion",
  "parameters": {
    "suggestion_id": "example_value"
  }
}
```

## Related Tools

- `automation_get_workflow_suggestions`: Get intelligent workflow suggestions based on query patterns and usage analytics
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

