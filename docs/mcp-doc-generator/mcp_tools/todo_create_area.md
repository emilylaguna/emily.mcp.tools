# todo_create_area

## Description
Create a new area (top-level organization) for grouping related projects and tasks

## Status
- **Enabled**: ✅ Yes
- **Tags**: create, organization, area, todo

## Parameters

### Required Parameters

#### `name` (string)
- **Title**: Name
- **Description**: No description

#### `description` (string)
- **Title**: Description
- **Description**: No description

### Optional Parameters

#### `color` (string | null)
- **Title**: Color
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "todo_create_area",
  "parameters": {
    "name": "example_value",
    "description": "example_value"
  }
}
```

## Related Tools

- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_areas`: List all areas (top-level organization containers) with optional status filtering
- `todo_archive_area`: Archive an area and all its projects to remove them from active view while preserving data
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling

