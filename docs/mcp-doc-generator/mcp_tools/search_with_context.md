# search_with_context

## Description
Search with additional context about the current entity for more accurate and relevant results

## Status
- **Enabled**: ✅ Yes
- **Tags**: relevance, search, enhanced, contextual, entity

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

### Optional Parameters

#### `entity_context` (string)
- **Title**: Entity Context
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "search_with_context",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `intent_based_search`: Understand search intent from natural language and provide contextual results with AI interpretation
- `todo_quick_find`: Quick semantic search across tasks, projects, and areas using AI-powered search capabilities
- `todo_search_tasks`: Search tasks with advanced filtering capabilities including metadata, tags, and content search
- `graph_find_related`: Find entities related to a given entity within a specified depth using graph traversal algorithms
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering

