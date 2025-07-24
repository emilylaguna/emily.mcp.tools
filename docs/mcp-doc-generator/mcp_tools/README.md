# MCP Tools Index

This directory contains individual documentation files for each MCP tool.

**Total Tools**: 65

## Categories

### Analysis

- [`get_cross_domain_insights`](./get_cross_domain_insights.md) - Get cross-domain insights for a specific entity by analyzing relationships across different data typ...

### Anytime

- [`todo_get_anytime`](./todo_get_anytime.md) - Get tasks without specific scheduling that can be done at any convenient time

### Approve

- [`automation_approve_workflow_suggestion`](./automation_approve_workflow_suggestion.md) - Approve and implement a workflow suggestion to create an active automation workflow

### Automation

- [`automation_get_suggestion_metrics`](./automation_get_suggestion_metrics.md) - Get analytics and metrics for workflow suggestions including approval rates and effectiveness

### Centrality

- [`graph_get_centrality`](./graph_get_centrality.md) - Get centrality score for an entity to measure its importance and influence in the knowledge graph

### Complex

- [`complex_query`](./complex_query.md) - Process complex queries with multiple clauses and relationships using advanced AI parsing

### Connection

- [`graph_create_relation`](./graph_create_relation.md) - Create a new relation between two entities with specified type, strength, and metadata
- [`graph_shortest_path`](./graph_shortest_path.md) - Find the shortest path between two entities using graph algorithms for relationship discovery

### Conversation

- [`todo_create_from_conversation`](./todo_create_from_conversation.md) - Create task from conversation context by analyzing chat history and extracting actionable items

### Create

- [`todo_create_area`](./todo_create_area.md) - Create a new area (top-level organization) for grouping related projects and tasks
- [`todo_create_task`](./todo_create_task.md) - Create a new task with advanced features like scheduling, priority, and energy level tracking

### Data

- [`graph_create_entity`](./graph_create_entity.md) - Create a new entity in the knowledge graph with specified properties and metadata

### Details

- [`graph_get_entity`](./graph_get_entity.md) - Get detailed information about a specific entity by its ID including properties and metadata
- [`todo_get_task_details`](./todo_get_task_details.md) - Get detailed task information including relationships, project context, and area assignments

### Evening

- [`todo_get_evening`](./todo_get_evening.md) - Get tasks suitable for evening work based on energy level and context requirements

### Filter

- [`graph_get_relations`](./graph_get_relations.md) - Get all relations for a specific entity with optional filtering by relation types
- [`todo_search_tasks`](./todo_search_tasks.md) - Search tasks with advanced filtering capabilities including metadata, tags, and content search

### Graph

- [`graph_find_related`](./graph_find_related.md) - Find entities related to a given entity within a specified depth using graph traversal algorithms

### Interpretation

- [`natural_query`](./natural_query.md) - Process natural language queries with intelligent interpretation and context understanding

### List

- [`todo_list_areas`](./todo_list_areas.md) - List all areas (top-level organization containers) with optional status filtering

### Mapping

- [`get_expertise_map`](./get_expertise_map.md) - Create expertise map from conversation and code patterns to identify knowledge distribution

### Modify

- [`todo_update_task`](./todo_update_task.md) - Update a task's properties including status, priority, scheduling, and project assignment

### Organization

- [`todo_archive_area`](./todo_archive_area.md) - Archive an area and all its projects to remove them from active view while preserving data

### Overview

- [`todo_get_statistics`](./todo_get_statistics.md) - Get comprehensive todo statistics including task counts, project status, and productivity metrics

### Patterns

- [`graph_find_clusters`](./graph_find_clusters.md) - Find clusters of related entities using community detection algorithms for pattern discovery

### Priorities

- [`todo_suggest_priorities`](./todo_suggest_priorities.md) - Get AI-suggested task priorities based on context, deadlines, and workload analysis

### Project

- [`get_project_intelligence`](./get_project_intelligence.md) - Get comprehensive project intelligence including related tasks, people, technologies, and insights
- [`todo_complete_project`](./todo_complete_project.md) - Complete a project and all its associated tasks in bulk operation
- [`todo_create_project`](./todo_create_project.md) - Create a new project within an area to organize related tasks and goals
- [`todo_get_project_progress`](./todo_get_project_progress.md) - Get detailed project progress including completion rates, task breakdown, and milestones
- [`todo_list_projects`](./todo_list_projects.md) - List projects with optional filtering by area and status for project management overview
- [`todo_project_timeline`](./todo_project_timeline.md) - Get complete project timeline across all data types including tasks, milestones, and deadlines

### Recommendations

- [`get_smart_suggestions`](./get_smart_suggestions.md) - Get contextual suggestions based on current entity and activity patterns using AI analysis

### Relevance

- [`search_with_context`](./search_with_context.md) - Search with additional context about the current entity for more accurate and relevant results

### Remove

- [`graph_delete_entity`](./graph_delete_entity.md) - Delete an entity and all its relations from the knowledge graph permanently
- [`graph_delete_relation`](./graph_delete_relation.md) - Delete a specific relation between entities from the knowledge graph
- [`todo_delete_task`](./todo_delete_task.md) - Permanently delete a task from the system

### Schedule

- [`todo_get_today`](./todo_get_today.md) - Get today's tasks with AI suggestions for prioritization and scheduling optimization
- [`todo_get_upcoming`](./todo_get_upcoming.md) - Get upcoming tasks and events within a specified timeframe for planning and preparation

### Search

- [`intent_based_search`](./intent_based_search.md) - Understand search intent from natural language and provide contextual results with AI interpretation

### Semantic

- [`graph_search`](./graph_search.md) - Search for entities in the knowledge graph using semantic search with optional type filtering
- [`intelligent_search`](./intelligent_search.md) - Advanced semantic search with cross-domain intelligence for finding related information across all d...
- [`todo_quick_find`](./todo_quick_find.md) - Quick semantic search across tasks, projects, and areas using AI-powered search capabilities

### Someday

- [`todo_get_someday`](./todo_get_someday.md) - Get tasks marked for future consideration that are not immediately actionable

### Todo

- [`todo_complete_task`](./todo_complete_task.md) - Mark a task as completed and update its status with completion metadata
- [`todo_create_task_nl`](./todo_create_task_nl.md) - Create task from natural language input using AI to parse intent, priority, and scheduling

### Uncategorized

- [`handoff_get`](./handoff_get.md) - Get all handoff contexts from today ordered by created_at in DESC order.
- [`handoff_insights`](./handoff_insights.md) - Get AI-generated insights about a handoff context.
- [`handoff_list`](./handoff_list.md) - List recent saved chat contexts.
- [`handoff_related`](./handoff_related.md) - Get contexts related to the specified context through entities and topics.
- [`handoff_save`](./handoff_save.md) - Save chat context for handoff between sessions with AI enhancement.
- [`handoff_search`](./handoff_search.md) - Search handoff contexts by content using AI semantic search.
- [`handoff_suggest_actions`](./handoff_suggest_actions.md) - Get suggested follow-up actions for a context.
- [`todo_update_project`](./todo_update_project.md) - Update a project's properties.

### View

- [`automation_get_workflow`](./automation_get_workflow.md) - Get detailed information about a specific automation workflow including configuration and status
- [`automation_list_workflows`](./automation_list_workflows.md) - List all registered automation workflows with optional filtering by enabled status

### Workflow

- [`automation_delete_workflow`](./automation_delete_workflow.md) - Permanently delete an automation workflow and stop all its scheduled executions
- [`automation_get_run`](./automation_get_run.md) - Get detailed information about a specific workflow run including status, logs, and results
- [`automation_get_workflow_suggestions`](./automation_get_workflow_suggestions.md) - Get intelligent workflow suggestions based on query patterns and usage analytics
- [`automation_list_runs`](./automation_list_runs.md) - List automation workflow runs with optional filtering by workflow and execution history
- [`automation_pause_workflow`](./automation_pause_workflow.md) - Pause an automation workflow to temporarily stop its execution without deleting it
- [`automation_register_workflow`](./automation_register_workflow.md) - Register a new automation workflow with triggers, conditions, and actions
- [`automation_resume_workflow`](./automation_resume_workflow.md) - Resume a paused automation workflow to continue its scheduled execution
- [`automation_trigger_workflow`](./automation_trigger_workflow.md) - Manually trigger an automation workflow with optional event data for immediate execution
- [`get_workflow_suggestions`](./get_workflow_suggestions.md) - Get intelligent workflow suggestions based on user's current activity and historical patterns

## Quick Reference

### Common Patterns

- **todo_*** - Task and project management
- **graph_*** - Knowledge graph operations
- **automation_*** - Workflow automation
- **get_*** - Data retrieval and insights
- **intelligent_search** - Cross-domain semantic search
- **natural_query** - Natural language processing

### Usage Tips

1. Start with the index to find relevant tools
2. Check required vs optional parameters
3. Note tool annotations (destructive, read-only, etc.)
4. Use related tools section for workflow discovery
