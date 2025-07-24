# todo_project_timeline

## Description
Get complete project timeline across all data types including tasks, milestones, and deadlines

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, tracking, timeline, todo, history

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
  "tool": "todo_project_timeline",
  "parameters": {
    "project_id": "example_value"
  }
}
```

## Related Tools

- `todo_get_project_progress`: Get detailed project progress including completion rates, task breakdown, and milestones
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_complete_project`: Complete a project and all its associated tasks in bulk operation
- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks

