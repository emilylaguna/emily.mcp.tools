# todo_delete_task

## Description
Permanently delete a task from the system

## Status
- **Enabled**: ✅ Yes
- **Tags**: remove, cleanup, todo, delete, task

## Parameters

### Required Parameters

#### `task_id` (string)
- **Title**: Task Id
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone
- 🔄 **Idempotent**: Multiple calls with same parameters produce same result

## Usage Example

```json
{
  "tool": "todo_delete_task",
  "parameters": {
    "task_id": "example_value"
  }
}
```

## Related Tools

- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_get_evening`: Get tasks suitable for evening work based on energy level and context requirements

