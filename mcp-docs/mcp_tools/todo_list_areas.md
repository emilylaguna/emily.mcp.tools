# todo_list_areas

## Description
List all areas (top-level organization containers) with optional status filtering

## Status
- **Enabled**: ✅ Yes
- **Tags**: list, organization, area, todo

## Parameters

### Optional Parameters

#### `status` (Status)
- **Title**: Status
- **Description**: No description
- **Default**: `active`
- **Allowed values**: `active`, `archived`

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_list_areas"
}
```

## Related Tools

- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_archive_area`: Archive an area and all its projects to remove them from active view while preserving data
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking

