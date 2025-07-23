# todo_create_task

## Description
Create a new task with advanced features like scheduling, priority, and energy level tracking

## Status
- **Enabled**: ✅ Yes
- **Tags**: create, task, productivity, todo

## Parameters

### Required Parameters

#### `title` (string)
- **Title**: Title
- **Description**: No description

### Optional Parameters

#### `description` (string | null)
- **Title**: Description
- **Description**: No description

#### `project_id` (string | null)
- **Title**: Project Id
- **Description**: No description

#### `area_id` (string | null)
- **Title**: Area Id
- **Description**: No description

#### `priority` (Priority)
- **Title**: Priority
- **Description**: No description
- **Default**: `medium`
- **Allowed values**: `low`, `medium`, `high`, `urgent`, `critical`

#### `scheduled_date` (string | null)
- **Title**: Scheduled Date
- **Description**: No description

#### `due_date` (string | null)
- **Title**: Due Date
- **Description**: No description

#### `energy_level` (Energy Level)
- **Title**: Energy Level
- **Description**: No description
- **Default**: `medium`
- **Allowed values**: `low`, `medium`, `high`

#### `time_estimate` (integer | null)
- **Title**: Time Estimate
- **Description**: No description

#### `tags` (array | null)
- **Title**: Tags
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "todo_create_task",
  "parameters": {
    "title": "example_value"
  }
}
```

## Related Tools

- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization

