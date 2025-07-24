# todo_create_from_conversation

## Description
Create task from conversation context by analyzing chat history and extracting actionable items

## Status
- **Enabled**: ✅ Yes
- **Tags**: conversation, todo, ai, create, task

## Parameters

### Required Parameters

#### `context_id` (string)
- **Title**: Context Id
- **Description**: No description

### Optional Parameters

#### `title` (string | null)
- **Title**: Title
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "todo_create_from_conversation",
  "parameters": {
    "context_id": "example_value"
  }
}
```

## Related Tools

- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_suggest_priorities`: Get AI-suggested task priorities based on context, deadlines, and workload analysis
- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks

