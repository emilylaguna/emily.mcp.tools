# handoff_search

## Description
Search handoff contexts by content using AI semantic search.

## Status
- **Enabled**: ✅ Yes
- **Tags**: None

## Parameters

### Required Parameters

#### `query` (string)
- **Title**: Query
- **Description**: No description

### Optional Parameters

#### `limit` (integer)
- **Title**: Limit
- **Description**: No description
- **Default**: `10`

## Usage Example

```json
{
  "tool": "handoff_search",
  "parameters": {
    "query": "example_value"
  }
}
```

## Related Tools

- `handoff_save`: Save chat context for handoff between sessions with AI enhancement.
- `handoff_get`: Get all handoff contexts from today ordered by created_at in DESC order.
- `handoff_list`: List recent saved chat contexts.
- `handoff_related`: Get contexts related to the specified context through entities and topics.
- `handoff_insights`: Get AI-generated insights about a handoff context.

