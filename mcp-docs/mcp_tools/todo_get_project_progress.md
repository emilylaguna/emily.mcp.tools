# todo_get_project_progress

## Description
Get detailed project progress including completion rates, task breakdown, and milestones

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, progress, tracking, analytics, todo

## Parameters

### Required Parameters

#### `project_id` (string)
- **Title**: Project Id
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_get_project_progress",
  "parameters": {
    "project_id": "example_value"
  }
}
```

## Related Tools

- `todo_project_timeline`: Get complete project timeline across all data types including tasks, milestones, and deadlines
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_complete_project`: Complete a project and all its associated tasks in bulk operation
- `todo_get_statistics`: Get comprehensive todo statistics including task counts, project status, and productivity metrics

