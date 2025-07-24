# get_project_intelligence

## Description
Get comprehensive project intelligence including related tasks, people, technologies, and insights

## Status
- **Enabled**: ✅ Yes
- **Tags**: project, intelligence, comprehensive, analytics, insights

## Parameters

### Required Parameters

#### `project_id` (string)
- **Title**: Project Id
- **Description**: No description

## Tool Annotations

- 🔄 **Idempotent**: Multiple calls with same parameters produce same result
- 👁️ **Read-only**: This tool only retrieves information

## Usage Example

```json
{
  "tool": "get_project_intelligence",
  "parameters": {
    "project_id": "example_value"
  }
}
```

## Related Tools

- `todo_get_project_progress`: Get detailed project progress including completion rates, task breakdown, and milestones
- `get_cross_domain_insights`: Get cross-domain insights for a specific entity by analyzing relationships across different data typ...
- `todo_create_project`: Create a new project within an area to organize related tasks and goals
- `todo_list_projects`: List projects with optional filtering by area and status for project management overview
- `todo_complete_project`: Complete a project and all its associated tasks in bulk operation

