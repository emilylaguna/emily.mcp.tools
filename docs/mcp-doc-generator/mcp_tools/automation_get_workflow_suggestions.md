# automation_get_workflow_suggestions

## Description
Get intelligent workflow suggestions based on query patterns and usage analytics

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, recommendations, automation, ai, suggestions

## Parameters

### Optional Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description
- **Default**: ``

#### `limit` (integer)
- **Title**: Limit
- **Description**: No description
- **Default**: `10`

## Tool Annotations

- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "automation_get_workflow_suggestions"
}
```

## Related Tools

- `automation_approve_workflow_suggestion`: Approve and implement a workflow suggestion to create an active automation workflow
- `get_workflow_suggestions`: Get intelligent workflow suggestions based on user's current activity and historical patterns
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status

