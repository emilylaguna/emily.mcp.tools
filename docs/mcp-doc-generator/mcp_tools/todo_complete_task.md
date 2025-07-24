# todo_complete_task

## Description
Mark a task as completed and update its status with completion metadata

## Status
- **Enabled**: ✅ Yes
- **Tags**: todo, complete, status, update, task

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
  "tool": "todo_complete_task",
  "parameters": {
    "task_id": "example_value"
  }
}
```

## Related Tools

- `todo_update_task`: Update a task's properties including status, priority, scheduling, and project assignment
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization

