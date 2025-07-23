# todo_create_task_nl

## Description
Create task from natural language input using AI to parse intent, priority, and scheduling

## Status
- **Enabled**: ✅ Yes
- **Tags**: todo, task, ai, create, natural-language

## Parameters

### Required Parameters

#### `input_text` (string)
- **Title**: Input Text
- **Description**: No description

## Tool Annotations

- ⚠️ **Destructive**: This tool makes changes that cannot be easily undone

## Usage Example

```json
{
  "tool": "todo_create_task_nl",
  "parameters": {
    "input_text": "example_value"
  }
}
```

## Related Tools

- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_suggest_priorities`: Get AI-suggested task priorities based on context, deadlines, and workload analysis
- `todo_create_area`: Create a new area (top-level organization) for grouping related projects and tasks

