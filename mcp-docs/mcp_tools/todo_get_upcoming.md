# todo_get_upcoming

## Description
Get upcoming tasks and events within a specified timeframe for planning and preparation

## Status
- **Enabled**: ✅ Yes
- **Tags**: schedule, todo, upcoming, planning, task

## Parameters

### Optional Parameters

#### `days` (integer)
- **Title**: Days
- **Description**: No description
- **Default**: `7`

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "todo_get_upcoming"
}
```

## Related Tools

- `todo_get_today`: Get today's tasks with AI suggestions for prioritization and scheduling optimization
- `todo_get_evening`: Get tasks suitable for evening work based on energy level and context requirements
- `todo_get_anytime`: Get tasks without specific scheduling that can be done at any convenient time
- `todo_get_someday`: Get tasks marked for future consideration that are not immediately actionable
- `todo_create_task`: Create a new task with advanced features like scheduling, priority, and energy level tracking

