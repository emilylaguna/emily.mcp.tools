# todo_search_tasks

## Description
Search tasks with advanced filtering capabilities including metadata, tags, and content search

## Status
- **Enabled**: ✅ Yes
- **Tags**: filter, search, todo, advanced, task

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

### Optional Parameters

#### `filters` (object | null)
- **Title**: Filters
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_search_tasks",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_get_evening`: Get tasks suitable for evening work based on energy level and context requirements

