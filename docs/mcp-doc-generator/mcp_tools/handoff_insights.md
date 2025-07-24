# handoff_insights

## Description
Get AI-generated insights about a handoff context.

## Status
- **Enabled**: ✅ Yes
- **Tags**: None

## Parameters

### Required Parameters

#### `context_id` (integer)
- **Title**: Context Id
- **Description**: No description

## Usage Example

```json
{
  "tool": "handoff_insights",
  "parameters": {
    "context_id": 1
  }
}
```

## Related Tools

- `handoff_save`: Save chat context for handoff between sessions with AI enhancement.
- `handoff_get`: Get all handoff contexts from today ordered by created_at in DESC order.
- `handoff_list`: List recent saved chat contexts.
- `handoff_search`: Search handoff contexts by content using AI semantic search.
- `handoff_related`: Get contexts related to the specified context through entities and topics.

