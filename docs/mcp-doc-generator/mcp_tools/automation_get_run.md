# automation_get_run

## Description
Get detailed information about a specific workflow run including status, logs, and results

## Status
- **Enabled**: ✅ Yes
- **Tags**: workflow, details, automation, run, monitoring

## Parameters

### Required Parameters

#### `run_id` (string)
- **Title**: Run Id
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "automation_get_run",
  "parameters": {
    "run_id": "example_value"
  }
}
```

## Related Tools

- `automation_get_workflow`: Get detailed information about a specific automation workflow including configuration and status
- `automation_list_runs`: List automation workflow runs with optional filtering by workflow and execution history
- `automation_register_workflow`: Register a new automation workflow with triggers, conditions, and actions
- `automation_list_workflows`: List all registered automation workflows with optional filtering by enabled status
- `automation_delete_workflow`: Permanently delete an automation workflow and stop all its scheduled executions

