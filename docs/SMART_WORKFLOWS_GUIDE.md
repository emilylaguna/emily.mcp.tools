# Smart Workflows & Automation Guide

## Overview

The Smart Workflows & Automation system provides AI-powered workflow suggestions and automated task execution based on user behavior patterns. This system analyzes your activity in the unified memory store and suggests workflows that can automate repetitive tasks and improve productivity.

## Key Features

### 🤖 AI-Powered Workflow Suggestions
- **Pattern Analysis**: Analyzes your activity patterns over time
- **Smart Recommendations**: Suggests workflows based on your behavior
- **Confidence Scoring**: Each suggestion includes a confidence score
- **Impact Assessment**: Estimates the potential impact of each workflow

### 🔄 Automated Workflow Execution
- **Event-Driven Triggers**: Workflows trigger based on data changes
- **Scheduled Execution**: Support for cron-like scheduling
- **Template Resolution**: Dynamic content using template variables
- **Error Handling**: Robust error handling with rollback support

### 🛠️ Built-in Action Types
- **create_task**: Create new tasks automatically
- **update_entity**: Update existing entities
- **save_relation**: Create relationships between entities
- **notify**: Send notifications via Slack, email, or console
- **run_shell**: Execute shell commands
- **http_request**: Make HTTP requests to external services

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Layer                        │
├─────────────────────────────────────────────────────────────┤
│                Automation Tool                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Workflow    │ │ Workflow    │ │ Workflow    │          │
│  │ Engine      │ │ Suggester   │ │ Actions     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│              Unified Memory Store                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ SQLite      │ │ Vector      │ │ AI          │          │
│  │ Database    │ │ Search      │ │ Extraction  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Getting Workflow Suggestions

```python
# Get all workflow suggestions
result = await mcp.call("automation_get_workflow_suggestions")

# Get suggestions for a specific query
result = await mcp.call("automation_get_workflow_suggestions", 
                       query="task completion", limit=5)
```

### Approving Workflow Suggestions

```python
# Approve a workflow suggestion
result = await mcp.call("automation_approve_workflow_suggestion", 
                       suggestion_id="auto_task_completion")
```

### Getting Suggestion Metrics

```python
# Get metrics about workflow suggestions
result = await mcp.call("automation_get_suggestion_metrics")
```

### Managing Workflows

```python
# List all workflows
result = await mcp.call("automation_list_workflows")

# Register a new workflow
workflow_def = {
    "id": "my_workflow",
    "name": "My Custom Workflow",
    "description": "A custom workflow for my needs",
    "trigger": {
        "type": "entity_created",
        "filter": {"type": "task"}
    },
    "actions": [
        {
            "type": "notify",
            "params": {
                "channel": "slack",
                "message": "New task created: {{ entity.name }}"
            }
        }
    ]
}
result = await mcp.call("automation_register_workflow", 
                       workflow_definition=workflow_def)
```

## Workflow DSL (YAML)

Workflows are defined using a YAML-based DSL that supports:

### Triggers

```yaml
trigger:
  type: entity_created  # entity_created, entity_updated, relation_created, scheduled, manual
  filter:
    type: handoff       # Filter by entity type
    metadata.topics: ["meeting", "discussion"]  # Filter by metadata
  schedule: "0 9 * * 1-5"  # Cron-like schedule for scheduled triggers
```

### Actions

```yaml
actions:
  - type: create_task
    params:
      title: "Follow up on {{ entity.name }}"
      priority: high
      content: "Action items: {{ entity.content }}"
  
  - type: notify
    params:
      channel: slack
      message: "New meeting follow-up task created"
  
  - type: update_entity
    params:
      entity_id: "{{ entity.metadata.project_id }}"
      metadata:
        last_updated: "{{ entity.updated_at }}"
```

### Template Variables

The DSL supports template variables using `{{ variable }}` syntax:

- `{{ entity.name }}` - Name of the triggering entity
- `{{ entity.content }}` - Content of the triggering entity
- `{{ entity.metadata.field }}` - Metadata field of the entity
- `{{ datetime.now() }}` - Current datetime

## Example Workflows

### Meeting Follow-up Automation

```yaml
id: meeting_followup
name: Meeting Follow-up Automation
description: Create action items from meeting notes
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["meeting", "discussion"]
actions:
  - type: create_task
    params:
      title: "Follow up on meeting: {{ entity.name }}"
      priority: medium
      content: "Action items from meeting: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "Meeting follow-up task created: {{ entity.name }}"
```

### Bug Report Automation

```yaml
id: bug_report
name: Bug Report Automation
description: Automatically create tasks for bug reports
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["bug", "issue", "error"]
actions:
  - type: create_task
    params:
      title: "Investigate bug: {{ entity.name }}"
      priority: high
      content: "Bug report: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "New bug report requires investigation: {{ entity.name }}"
```

### Daily Standup Reminder

```yaml
id: daily_standup
name: Daily Standup Reminder
description: Send daily standup reminders
trigger:
  type: scheduled
  schedule: "0 9 * * 1-5"  # 9 AM on weekdays
actions:
  - type: notify
    params:
      channel: slack
      message: "Time for daily standup! Please update your task status."
  - type: create_task
    params:
      title: "Daily Standup - {{ datetime.now().strftime('%Y-%m-%d') }}"
      priority: medium
      content: "Daily team synchronization meeting"
```

## Pattern Analysis

The WorkflowSuggester analyzes several types of patterns:

### Entity Creation Patterns
- Frequency of creating different entity types
- Common metadata patterns
- Creation timing patterns

### Task Completion Patterns
- Task completion rates
- Time to completion
- Task priority patterns

### Conversation Patterns
- Frequent conversation topics
- Follow-up needs
- Communication patterns

### Temporal Patterns
- Peak activity hours
- Regular activity days
- Seasonal patterns

### Content Patterns
- Common keywords
- Content length patterns
- Repetitive content elements

## Configuration

### Notification Channels

Configure notification channels in the automation tool:

```python
automation_tool.configure_notification_channel("slack", {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#general"
})

automation_tool.configure_notification_channel("email", {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@gmail.com",
    "password": "your-app-password"
})
```

### Workflow Engine Settings

```python
# Configure workflow engine
workflow_engine = WorkflowEngine(memory_store)
workflow_engine.max_concurrent_workflows = 10
workflow_engine.enable_logging = True
```

## Best Practices

### 1. Start with Suggestions
- Use the AI suggestions as a starting point
- Review and customize suggested workflows
- Test workflows before enabling them

### 2. Monitor Performance
- Check workflow run logs regularly
- Monitor for failed executions
- Review suggestion metrics periodically

### 3. Security Considerations
- Be careful with shell command actions
- Validate HTTP request endpoints
- Use secure notification channels

### 4. Template Best Practices
- Use descriptive variable names
- Handle missing variables gracefully
- Test templates with sample data

## Troubleshooting

### Common Issues

1. **Workflow not triggering**
   - Check trigger conditions
   - Verify entity types and metadata
   - Review event logs

2. **Template resolution errors**
   - Check variable names
   - Verify entity structure
   - Test with sample data

3. **Action execution failures**
   - Check action parameters
   - Verify external service connectivity
   - Review error logs

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('workflows').setLevel(logging.DEBUG)
```

Check workflow run logs:

```python
runs = await mcp.call("automation_list_runs", workflow_id="my_workflow")
for run in runs['runs']:
    print(f"Status: {run['status']}, Error: {run.get('error')}")
```

## API Reference

### MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `automation_get_workflow_suggestions` | Get AI-powered workflow suggestions | `query`, `limit` |
| `automation_approve_workflow_suggestion` | Approve a workflow suggestion | `suggestion_id` |
| `automation_get_suggestion_metrics` | Get suggestion metrics | None |
| `automation_register_workflow` | Register a new workflow | `workflow_definition` |
| `automation_list_workflows` | List all workflows | `enabled_only` |
| `automation_get_workflow` | Get workflow details | `workflow_id` |
| `automation_delete_workflow` | Delete a workflow | `workflow_id` |
| `automation_pause_workflow` | Pause a workflow | `workflow_id` |
| `automation_resume_workflow` | Resume a workflow | `workflow_id` |
| `automation_trigger_workflow` | Manually trigger a workflow | `workflow_id`, `event_data` |
| `automation_list_runs` | List workflow runs | `workflow_id`, `limit` |
| `automation_get_run` | Get run details | `run_id` |

### MCP Resources

| Resource | Description |
|----------|-------------|
| `resource://automation/workflows` | List of all workflows |
| `resource://automation/workflows/{workflow_id}` | Workflow details |
| `resource://automation/runs` | List of workflow runs |

## Future Enhancements

- **Machine Learning**: Improved pattern recognition
- **Natural Language**: Create workflows using natural language
- **Visual Editor**: Drag-and-drop workflow builder
- **Integration Hub**: Connect to external services
- **Advanced Analytics**: Detailed workflow performance metrics
- **Collaborative Workflows**: Team-based workflow sharing

---

For more information, see the [API Reference](api_reference.md) and [Architecture Guide](architecture.md). 