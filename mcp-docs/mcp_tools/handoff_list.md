# handoff_list

## Description
List recent saved chat contexts.

## Status
- **Enabled**: ✅ Yes
- **Tags**: None

## Parameters

### Optional Parameters

#### `limit` (integer)
- **Title**: Limit
- **Description**: No description
- **Default**: `10`

## Usage Example

```json
{
  "tool": "handoff_list"
}
```

## Related Tools

- `handoff_save`: Save chat context for handoff between sessions with AI enhancement.
- `handoff_get`: Get all handoff contexts from today ordered by created_at in DESC order.
- `handoff_search`: Search handoff contexts by content using AI semantic search.
- `handoff_related`: Get contexts related to the specified context through entities and topics.
- `handoff_insights`: Get AI-generated insights about a handoff context.

