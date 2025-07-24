# todo_update_task

## Description
Update a task's properties including status, priority, scheduling, and project assignment

## Status
- **Enabled**: ✅ Yes
- **Tags**: modify, todo, management, update, task

## Parameters

### Required Parameters

#### `task_id` (string)
- **Title**: Task Id
- **Description**: No description

### Optional Parameters

#### `title` (string | null)
- **Title**: Title
- **Description**: No description

#### `description` (string | null)
- **Title**: Description
- **Description**: No description

#### `status` (null)
- **Title**: Status
- **Description**: No description

#### `priority` (null)
- **Title**: Priority
- **Description**: No description

#### `project_id` (string | null)
- **Title**: Project Id
- **Description**: No description

#### `area_id` (string | null)
- **Title**: Area Id
- **Description**: No description

#### `scheduled_date` (string | null)
- **Title**: Scheduled Date
- **Description**: No description

#### `due_date` (string | null)
- **Title**: Due Date
- **Description**: No description

#### `energy_level` (null)
- **Title**: Energy Level
- **Description**: No description

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
  "tool": "todo_update_task",
  "parameters": {
    "task_id": "example_value"
  }
}
```

## Related Tools

- `todo_complete_task`: Mark a task as completed and update its status with completion metadata
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization

