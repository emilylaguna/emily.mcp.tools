# intelligent_search

## Description
Advanced semantic search with cross-domain intelligence for finding related information across all data types

## Status
- **Enabled**: ✅ Yes
- **Tags**: semantic, intelligence, search, ai, cross-domain

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

### Optional Parameters

#### `context` (object)
- **Title**: Context
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "intelligent_search",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `todo_quick_find`: Quick semantic search across tasks, projects, and areas using AI-powered search capabilities
- `graph_search`: Search for entities in the knowledge graph using semantic search with optional type filtering
- `natural_query`: Process natural language queries with intelligent interpretation and context understanding
- `intent_based_search`: Understand search intent from natural language and provide contextual results with AI interpretation
- `complex_query`: Process complex queries with multiple clauses and relationships using advanced AI parsing

