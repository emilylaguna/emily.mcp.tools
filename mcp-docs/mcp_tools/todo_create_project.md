# todo_create_project

## Description
Create a new project within an area to organize related tasks and goals

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, create, organization, todo

## Parameters

### Required Parameters

#### `name` (string)
- **Title**: Name
- **Description**: No description

#### `description` (string)
- **Title**: Description
- **Description**: No description

### Optional Parameters

#### `area_id` (string | null)
- **Title**: Area Id
- **Description**: No description

#### `deadline` (string | null)
- **Title**: Deadline
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "todo_create_project",
  "parameters": {
    "name": "example_value",
    "description": "example_value"
  }
}
```

## Related Tools

- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items

