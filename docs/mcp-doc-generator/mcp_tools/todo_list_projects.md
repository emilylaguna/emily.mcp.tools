# todo_list_projects

## Description
List projects with optional filtering by area and status for project management overview

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, organization, todo, list, management

## Parameters

### Optional Parameters

#### `area_id` (string | null)
- **Title**: Area Id
- **Description**: No description

#### `status` (Status)
- **Title**: Status
- **Description**: No description
- **Default**: `active`
- **Allowed values**: `active`, `completed`, `on_hold`, `cancelled`

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_list_projects"
}
```

## Related Tools

- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_areas`: List all areas (top-level organization containers) with optional status filtering
- `todo_complete_project`: Complete a project and all its associated tasks in bulk operation
- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_get_project_progress`: Get detailed project progress including completion rates, task breakdown, and milestones

