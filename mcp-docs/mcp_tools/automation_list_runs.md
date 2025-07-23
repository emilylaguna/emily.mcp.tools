# automation_list_runs

## Description
List automation workflow runs with optional filtering by workflow and execution history

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, automation, runs, history, monitoring

## Parameters

### Optional Parameters

#### `workflow_id` (string | null)
- **Title**: Workflow Id
- **Description**: No description

#### `limit` (integer)
- **Title**: Limit
- **Description**: No description
- **Default**: `50`

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "automation_list_runs"
}
```

## Related Tools

- `automation_get_run`: Get detailed information about a specific workflow run including status, logs, and results
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

