# handoff_save

## Description
Save chat context for handoff between sessions with AI enhancement.

## Status
- **Enabled**: ✅ Yes
- **Tags**: None

## Parameters

### Required Parameters

#### `context` (string)
- **Title**: Context
- **Description**: No description

## Usage Example

```json
{
  "tool": "handoff_save",
  "parameters": {
    "context": "example_value"
  }
}
```

## Related Tools

- `handoff_get`: Get all handoff contexts from today ordered by created_at in DESC order.
- `handoff_list`: List recent saved chat contexts.
- `handoff_search`: Search handoff contexts by content using AI semantic search.
- `handoff_related`: Get contexts related to the specified context through entities and topics.
- `handoff_insights`: Get AI-generated insights about a handoff context.

