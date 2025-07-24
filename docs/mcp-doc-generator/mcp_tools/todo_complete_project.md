# todo_complete_project

## Description
Complete a project and all its associated tasks in bulk operation

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, todo, management, complete, bulk

## Parameters

### Required Parameters

#### `project_id` (string)
- **Title**: Project Id
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "todo_complete_project",
  "parameters": {
    "project_id": "example_value"
  }
}
```

## Related Tools

- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_complete_task`: Mark a task as completed and update its status with completion metadata
- `todo_get_project_progress`: Get detailed project progress including completion rates, task breakdown, and milestones
- `todo_project_timeline`: Get complete project timeline across all data types including tasks, milestones, and deadlines

