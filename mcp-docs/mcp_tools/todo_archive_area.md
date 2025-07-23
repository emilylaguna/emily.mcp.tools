# todo_archive_area

## Description
Archive an area and all its projects to remove them from active view while preserving data

## Status
- **Enabled**: ✅ Yes
- **Tags**: organization, archive, area, cleanup, todo

## Parameters

### Required Parameters

#### `area_id` (string)
- **Title**: Area Id
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "todo_archive_area",
  "parameters": {
    "area_id": "example_value"
  }
}
```

## Related Tools

- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_list_areas`: List all areas (top-level organization containers) with optional status filtering
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_delete_task`: Permanently delete a task from the system

