# todo_quick_find

## Description
Quick semantic search across tasks, projects, and areas using AI-powered search capabilities

## Status
- **Enabled**: ✅ Yes
- **Tags**: semantic, find, todo, search, ai

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_quick_find",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `todo_create_task_nl`: Create task from natural language input using AI to parse intent, priority, and scheduling
- `todo_create_from_conversation`: Create task from conversation context by analyzing chat history and extracting actionable items
- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_suggest_priorities`: Get AI-suggested task priorities based on context, deadlines, and workload analysis
- `todo_search_tasks`: Search tasks with advanced filtering capabilities including metadata, tags, and content search

