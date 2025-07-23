# todo_update_project

## Description
Update a project's properties.

## Status
- **Enabled**: ✅ Yes
- **Tags**: None

## Parameters

### Required Parameters

#### `project_id` (string)
- **Title**: Project Id
- **Description**: No description

### Optional Parameters

#### `name` (string | null)
- **Title**: Name
- **Description**: No description

#### `description` (string | null)
- **Title**: Description
- **Description**: No description

#### `area_id` (string | null)
- **Title**: Area Id
- **Description**: No description

#### `status` (null)
- **Title**: Status
- **Description**: No description

#### `deadline` (string | null)
- **Title**: Deadline
- **Description**: No description

#### `progress` (number | null)
- **Title**: Progress
- **Description**: No description

#### `color` (string | null)
- **Title**: Color
- **Description**: No description

## Usage Example

```json
{
  "tool": "todo_update_project",
  "parameters": {
    "project_id": "example_value"
  }
}
```

## Related Tools

- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items

