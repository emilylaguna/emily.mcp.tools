# AI Agent Integration Guide for Emily Tools MCP Server

This guide provides comprehensive examples and prompts for integrating your AI agent with the Emily Tools MCP server. The server provides intelligent productivity tools with unified memory architecture, AI-powered search, and cross-domain intelligence.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Todo Management](#todo-management)
4. [Intelligent Handoff](#intelligent-handoff)
5. [Knowledge Graph](#knowledge-graph)
6. [Intelligent Search](#intelligent-search)
7. [Workflow Automation](#workflow-automation)
8. [Advanced Integration Patterns](#advanced-integration-patterns)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

## Overview

The Emily Tools MCP server provides the following core capabilities:

- **Unified Todo Management**: Things-style todos with AI enhancements
- **Intelligent Handoff**: Context preservation between sessions
- **Knowledge Graph**: Multi-codebase knowledge with relationships
- **Intelligent Search**: Semantic search across all data types
- **Workflow Automation**: AI-powered workflow suggestions

## Data Models and Entity Types

### Parameter Mapping

**Important**: The MCP tools use different parameter names than the underlying data model:

- **MCP Tool Parameters**: Use `description` for content
- **Data Model Fields**: Store content in the `content` field
- **Return Values**: MCP tools return `description` field (mapped from `content`)

### Supported Entity Types

When creating entities in the knowledge graph, you must use one of these valid entity types:

- **`task`** - Todo items, action items
- **`person`** - People mentioned in conversations  
- **`project`** - Software projects, initiatives
- **`file`** - Code files, documents
- **`handoff`** - Conversation contexts
- **`area`** - Areas for organization
- **`meeting`** - Meeting notes and outcomes
- **`technology`** - Programming languages, frameworks, tools
- **`conversation`** - General conversation contexts
- **`note`** - General notes and documentation
- **`workflow`** - Automation workflows
- **`workflow_run`** - Workflow execution instances

### Supported Relation Types

When creating relationships between entities, use one of these valid relation types:

- **`relates_to`** - General relationship
- **`contains`** - Hierarchical containment
- **`follows_from`** - Temporal or logical sequence
- **`depends_on`** - Dependency relationship
- **`mentions`** - Entity mentioned in content
- **`implements`** - Implementation relationship
- **`references`** - Reference relationship
- **`assigned_to`** - Assignment relationship
- **`created_by`** - Creation relationship
- **`part_of`** - Part-whole relationship
- **`similar_to`** - Similarity relationship

### Supported Context Types

For handoff and conversation contexts, use one of these valid context types:

- **`handoff`** - Session handoff contexts
- **`meeting`** - Meeting notes and outcomes
- **`debug_session`** - Debugging sessions
- **`conversation`** - General conversations
- **`code_review`** - Code review sessions
- **`planning_session`** - Planning meetings
- **`retrospective`** - Retrospective sessions

### Entity Structure

All entities follow this structure:
```python
{
    "type": "task|person|project|file|handoff|area|meeting|technology|conversation|note|workflow|workflow_run",
    "name": "Display name for the entity",
    "content": "Full content/description (optional)",
    "metadata": {},  # Flexible metadata dictionary
    "tags": []       # Searchable tags list
}
```

### Common Entity Examples

**Task Entity:**
```python
{
    "type": "task",
    "name": "Implement User Authentication",
    "content": "Add OAuth2 authentication with JWT tokens",
    "metadata": {
        "priority": "high",
        "status": "todo",
        "project_id": "project-uuid",
        "due_date": "2024-03-15"
    },
    "tags": ["authentication", "oauth2", "security"]
}
```

**Technology Entity:**
```python
{
    "type": "technology", 
    "name": "React",
    "content": "JavaScript library for building user interfaces",
    "metadata": {
        "version": "18.2.0",
        "category": "frontend"
    },
    "tags": ["javascript", "frontend", "ui"]
}
```

**Project Entity:**
```python
{
    "type": "project",
    "name": "Web Application Development", 
    "content": "Full-stack web application with React and Node.js",
    "metadata": {
        "status": "active",
        "deadline": "2024-03-15",
        "area_id": "area-uuid"
    },
    "tags": ["web-app", "full-stack", "react", "nodejs"]
}
```

**Person Entity:**
```python
{
    "type": "person",
    "name": "John Doe",
    "content": "Senior developer working on authentication system",
    "metadata": {
        "role": "developer",
        "expertise": ["react", "nodejs", "authentication"]
    },
    "tags": ["developer", "senior", "authentication"]
}
```

### Relation Examples

**Component Relationship:**
```python
{
    "source_id": "frontend-entity-id",
    "target_id": "project-entity-id", 
    "relation_type": "part_of",
    "strength": 0.9
}
```

**Dependency Relationship:**
```python
{
    "source_id": "auth-task-id",
    "target_id": "database-setup-task-id",
    "relation_type": "depends_on", 
    "strength": 0.8
}
```

**Assignment Relationship:**
```python
{
    "source_id": "auth-task-id",
    "target_id": "john-doe-person-id",
    "relation_type": "assigned_to",
    "strength": 1.0
}
```

## Getting Started

### Initial Setup Prompts

```markdown
# System Prompt for AI Agent Integration

You are an AI assistant with access to the Emily Tools MCP server. This server provides intelligent productivity tools with unified memory architecture. You can:

1. Manage todos with AI enhancements
2. Save and retrieve conversation context
3. Build and query knowledge graphs
4. Perform intelligent searches across all data
5. Automate workflows

Always use the appropriate MCP tools for these operations. When users ask for task management, use the todo tools. When they want to save context, use handoff tools. For knowledge management, use the knowledge graph tools.

## Available Tools

### Todo Management Tools
- `todo_create_area` - Create organizational areas
- `todo_create_project` - Create projects within areas
- `todo_create_task` - Create individual tasks
- `todo_create_task_nl` - Create tasks from natural language
- `todo_get_today` - Get today's tasks with AI suggestions
- `todo_list_areas` - List all areas
- `todo_list_projects` - List projects
- `todo_complete_task` - Mark tasks as complete

**Todo Tool Parameters:**
- `todo_create_area(name, description=None, color=None)` - Creates an area with optional description and color
- `todo_create_project(name, area_id=None, description=None, deadline=None)` - Creates a project with optional area assignment, description, and deadline
- `todo_create_task(title, description=None, project_id=None, area_id=None, priority="medium", scheduled_date=None, due_date=None, energy_level="medium", time_estimate=None, tags=None)` - Creates a task with full metadata support

### Handoff Tools
- `handoff_save` - Save conversation context
- `handoff_get` - Get latest saved context
- `handoff_list` - List recent contexts
- `handoff_search` - Search saved contexts
- `handoff_related` - Find related contexts
- `handoff_insights` - Get context insights

### Knowledge Graph Tools
- `graph_create_entity` - Create entities in the knowledge graph
- `graph_create_relation` - Create relationships between entities
- `graph_find_related` - Find related entities
- `graph_search` - Search for entities
- `graph_get_entity` - Get specific entity details

### Intelligent Search Tools
- `intelligent_search` - Advanced semantic search
- `natural_query` - Process natural language queries
- `get_project_intelligence` - Get project insights
- `find_expertise` - Find people with specific expertise
- `get_smart_suggestions` - Get contextual suggestions

Always provide helpful, actionable responses and use the appropriate tools for each request.

**Important for Workflow Automation**: To ensure workflows trigger consistently across sessions, implement automatic context saving:
- Save conversation context every few exchanges using `handoff_save`
- Include workflow-triggering keywords in context summaries
- This ensures automation workflows can detect and respond to conversation patterns

```

### Connection Setup

```markdown
# Connection Configuration

To connect your AI agent to the Emily Tools MCP server:

1. **Start the server**:
   ```bash
   cd /path/to/emily.mcp.tools
   uv run python main.py
   ```

2. **Configure your AI agent** to use the MCP server:
   - Protocol: MCP (Model Context Protocol)
   - Transport: stdio (default)
   - Server path: Path to your main.py file

3. **Test the connection** by calling a simple tool:
   ```python
   # Test with a simple todo creation
   result = mcp.call("todo_create_task", 
                    title="Test connection",
                    description="Verifying MCP server connection")
   ```

## Todo Management

### Basic Todo Operations

```markdown
# Todo Management Prompts

## Creating Organizational Structure

**Prompt**: "I want to organize my work into areas. Create areas for 'Work', 'Personal', and 'Learning'."

**AI Agent Response**:
I'll help you create an organizational structure for your todos. Let me create these areas for you.

```python
# Create work area
work_area = mcp.call("todo_create_area", 
                     name="Work",
                     description="Professional tasks and projects",
                     color="#007AFF")

# Create personal area  
personal_area = mcp.call("todo_create_area",
                        name="Personal", 
                        description="Personal tasks and life management",
                        color="#34C759")

# Create learning area
learning_area = mcp.call("todo_create_area",
                        name="Learning",
                        description="Educational goals and skill development", 
                        color="#FF9500")

# Example return value:
# {
#   "id": "uuid-string",
#   "name": "Work", 
#   "description": "Professional tasks and projects",
#   "status": "active",
#   "created": True
# }
```

## Creating Projects

**Prompt**: "I have a project to build a web application. Create a project for this."

**AI Agent Response**:
I'll create a project for your web application development. Let me set that up for you.

```python
# Create web app project
web_project = mcp.call("todo_create_project",
                       name="Web Application Development",
                       area_id=work_area["id"],
                       description="Build a modern web application with React and Node.js",
                       deadline="2024-03-15")

# Example return value:
# {
#   "id": "uuid-string",
#   "name": "Web Application Development",
#   "description": "Build a modern web application with React and Node.js", 
#   "area_id": "work-area-uuid",
#   "deadline": "2024-03-15",
#   "status": "active",
#   "created": True
# }
```

## Creating Tasks

**Prompt**: "I need to implement user authentication for my web app."

**AI Agent Response**:
I'll create a task for implementing user authentication. Let me add that to your project.

```python
# Create authentication task
auth_task = mcp.call("todo_create_task",
                     title="Implement User Authentication",
                     description="Add OAuth2 authentication with JWT tokens",
                     project_id=web_project["id"],
                     priority="high",
                     energy_level="high",
                     time_estimate=480)  # 8 hours

# Example return value:
# {
#   "id": "uuid-string",
#   "title": "Implement User Authentication",
#   "description": "Add OAuth2 authentication with JWT tokens",
#   "priority": "high",
#   "status": "todo",
#   "project_id": "web-project-uuid",
#   "area_id": null,
#   "scheduled_date": null,
#   "due_date": null,
#   "energy_level": "high",
#   "time_estimate": 480,
#   "tags": [],
#   "created": True
# }
```

## Natural Language Task Creation

**Prompt**: "I need to review the API documentation tomorrow morning."

**AI Agent Response**:
I'll create a task for reviewing the API documentation using natural language processing.

```python
# Create task from natural language
review_task = mcp.call("todo_create_task_nl",
                       input_text="Review the API documentation tomorrow morning")
```

## Getting Today's Tasks

**Prompt**: "What do I need to do today?"

**AI Agent Response**:
Let me check your tasks for today, including AI-suggested priorities.

```python
# Get today's tasks with AI suggestions
today_tasks = mcp.call("todo_get_today")
```

This will return:
- Overdue tasks
- Today's scheduled tasks  
- AI-suggested tasks based on your workload and priorities
- Evening tasks suitable for later work

## Task Completion

**Prompt**: "I finished implementing the authentication system."

**AI Agent Response**:
Great! Let me mark that task as complete for you.

```python
# Complete the authentication task
completed_task = mcp.call("todo_complete_task", 
                         task_id=auth_task["id"])
```
```

### Advanced Todo Features

```markdown
# Advanced Todo Management

## Project Progress Tracking

**Prompt**: "How is my web application project progressing?"

**AI Agent Response**:
Let me check the progress of your web application project.

```python
# Get project progress
project_progress = mcp.call("todo_get_project_progress",
                           project_id=web_project["id"])
```

This will show:
- Overall completion percentage
- Tasks completed vs. remaining
- Timeline analysis
- Potential blockers

## Evening Work Planning

**Prompt**: "What tasks are good for evening work?"

**AI Agent Response**:
Let me find tasks that are suitable for evening work (lower energy, less complex tasks).

```python
# Get evening tasks
evening_tasks = mcp.call("todo_get_evening")
```

## Upcoming Planning

**Prompt**: "What's coming up in the next week?"

**AI Agent Response**:
Let me check your upcoming tasks and deadlines for the next week.

```python
# Get upcoming tasks
upcoming = mcp.call("todo_get_upcoming", days=7)
```

## Quick Search

**Prompt**: "Find all tasks related to authentication."

**AI Agent Response**:
Let me search for all tasks related to authentication across your projects.

```python
# Search for authentication tasks
auth_tasks = mcp.call("todo_quick_find", query="authentication")
```
```

## Intelligent Handoff

### Context Preservation

```markdown
# Intelligent Handoff Prompts

## Saving Conversation Context

**Prompt**: "I need to save this conversation so I can continue later."

**AI Agent Response**:
I'll save this conversation context so you can pick up where you left off later.

```python
# Save current conversation context
saved_context = mcp.call("handoff_save",
                        context="Working on web application development. Discussed authentication implementation, API documentation review, and project structure. User is planning to continue with frontend development next.")
```

## Retrieving Context

**Prompt**: "What were we working on last time?"

**AI Agent Response**:
Let me retrieve the context from your last session to remind you where we left off.

```python
# Get latest saved context
latest_context = mcp.call("handoff_get")
```

## Context Search

**Prompt**: "Find conversations about authentication."

**AI Agent Response**:
Let me search through your saved contexts for discussions about authentication.

```python
# Search for authentication-related contexts
auth_contexts = mcp.call("handoff_search",
                         query="authentication",
                         limit=10)
```

## Related Context Discovery

**Prompt**: "What other conversations are related to my current work?"

**AI Agent Response**:
Let me find conversations that are related to your current context.

```python
# Find related contexts
related_contexts = mcp.call("handoff_related",
                           context_id=latest_context["id"])
```

## Context Insights

**Prompt**: "What insights can you provide about my recent conversations?"

**AI Agent Response**:
Let me analyze your recent conversations to provide insights and patterns.

```python
# Get context insights
insights = mcp.call("handoff_insights",
                   context_id=latest_context["id"])
```

This will provide:
- Key topics discussed
- Action items identified
- Project progress patterns
- Time allocation insights

## Action Suggestions

**Prompt**: "What should I focus on next based on our conversations?"

**AI Agent Response**:
Let me suggest next actions based on your conversation history and current context.

```python
# Get suggested actions
suggestions = mcp.call("handoff_suggest_actions",
                      context_id=latest_context["id"])
```
```

## Knowledge Graph

### Entity and Relationship Management

```markdown
# Knowledge Graph Prompts

## Creating Knowledge Entities

**Prompt**: "I want to document my web application architecture."

**AI Agent Response**:
I'll help you create knowledge entities to document your web application architecture.

```python
# Create architecture entity
architecture = mcp.call("graph_create_entity",
                       payload={
                           "type": "project",
                           "name": "Web Application Architecture",
                           "content": "Modern web application using React frontend, Node.js backend, and PostgreSQL database",
                           "tags": ["web-app", "architecture", "full-stack"]
                       })

# Create frontend entity
frontend = mcp.call("graph_create_entity",
                   payload={
                       "type": "technology",
                       "name": "React Frontend",
                       "content": "User interface built with React, TypeScript, and Tailwind CSS",
                       "tags": ["react", "frontend", "typescript"]
                   })

# Create backend entity
backend = mcp.call("graph_create_entity",
                  payload={
                      "type": "technology", 
                      "name": "Node.js Backend",
                      "content": "API server built with Express.js and JWT authentication",
                      "tags": ["nodejs", "backend", "api"]
                  })
```

## Creating Relationships

**Prompt**: "Connect the frontend and backend components to the architecture."

**AI Agent Response**:
I'll create relationships to show how the components connect to your overall architecture.

```python
# Create relationships
mcp.call("graph_create_relation",
        source_id=frontend["id"],
        target_id=architecture["id"],
        relation_type="part_of",
        strength=0.9)

mcp.call("graph_create_relation",
        source_id=backend["id"], 
        target_id=architecture["id"],
        relation_type="part_of",
        strength=0.9)

mcp.call("graph_create_relation",
        source_id=frontend["id"],
        target_id=backend["id"],
        relation_type="relates_to",
        strength=0.8)
```

## Finding Related Knowledge

**Prompt**: "What's related to my React frontend?"

**AI Agent Response**:
Let me find all entities and relationships related to your React frontend.

```python
# Find related entities
related = mcp.call("graph_find_related",
                  entity_id=frontend["id"],
                  depth=2)
```

## Knowledge Search

**Prompt**: "Search for all knowledge about authentication."

**AI Agent Response**:
Let me search through your knowledge graph for everything related to authentication.

```python
# Search for authentication knowledge
auth_knowledge = mcp.call("graph_search",
                         query="authentication",
                         entity_type="component")
```

## Codebase Integration

**Prompt**: "I want to document my codebase structure."

**AI Agent Response**:
I'll help you document your codebase structure in the knowledge graph.

```python
# Register codebase
codebase = mcp.call("codebase_register",
                   codebase_id="web-app",
                   name="Web Application",
                   root_path="/path/to/your/project",
                   description="Full-stack web application with React and Node.js")

# Add knowledge nodes
mcp.call("codebase_add_knowledge",
        codebase_id="web-app",
        node_type="file",
        name="auth.js",
        content="Authentication middleware and JWT token handling",
        path="src/middleware/auth.js",
        metadata={"language": "javascript", "purpose": "authentication"})

mcp.call("codebase_add_knowledge",
        codebase_id="web-app", 
        node_type="component",
        name="LoginForm",
        content="React component for user login with form validation",
        path="src/components/LoginForm.jsx",
        metadata={"language": "jsx", "purpose": "user-interface"})
```
```

## Intelligent Search

### Advanced Search Capabilities

```markdown
# Intelligent Search Prompts

## Universal Search

**Prompt**: "Find everything related to user authentication across all my data."

**AI Agent Response**:
I'll perform a comprehensive search across all your data types for authentication-related information.

```python
# Universal search across all domains
auth_results = mcp.call("intelligent_search",
                       query="user authentication",
                       context={
                           "include_tasks": True,
                           "include_conversations": True,
                           "include_knowledge": True,
                           "include_code": True
                       })
```

## Natural Language Queries

**Prompt**: "What tasks do I have that are related to the authentication project and are due soon?"

**AI Agent Response**:
I'll process your natural language query to find relevant tasks.

```python
# Process natural language query
query_results = mcp.call("natural_query",
                        query="tasks related to authentication project due soon")
```

## Project Intelligence

**Prompt**: "Give me a comprehensive overview of my web application project."

**AI Agent Response**:
I'll gather comprehensive intelligence about your web application project across all domains.

```python
# Get project intelligence
project_intel = mcp.call("get_project_intelligence",
                        project_id=web_project["id"])
```

This will provide:
- Task completion status
- Related conversations
- Knowledge documentation
- Code structure
- Timeline analysis
- Risk assessment

## Expertise Discovery

**Prompt**: "Who knows about React development in my team?"

**AI Agent Response**:
Let me search for people with React development expertise based on conversations and code contributions.

```python
# Find React experts
react_experts = mcp.call("find_expertise",
                        technology="React")
```

## Smart Suggestions

**Prompt**: "I'm working on authentication. What should I focus on next?"

**AI Agent Response**:
Let me provide contextual suggestions based on your current work on authentication.

```python
# Get smart suggestions
suggestions = mcp.call("get_smart_suggestions",
                      context={
                          "current_work": "authentication",
                          "project_id": web_project["id"],
                          "recent_tasks": ["implement_oauth", "setup_jwt"]
                      })
```

## Intent-Based Search

**Prompt**: "I want to understand how authentication works in my system."

**AI Agent Response**:
I'll understand your intent and provide relevant information about authentication in your system.

```python
# Intent-based search
auth_understanding = mcp.call("intent_based_search",
                             natural_query="I want to understand how authentication works in my system")
```

## Complex Queries

**Prompt**: "Show me all tasks that are high priority, related to authentication, and have dependencies on other tasks."

**AI Agent Response**:
I'll process this complex query to find tasks matching all your criteria.

```python
# Complex query processing
complex_results = mcp.call("complex_query",
                          query="high priority authentication tasks with dependencies")
```

## Cross-Domain Insights

**Prompt**: "What insights can you provide about my authentication work across all domains?"

**AI Agent Response**:
I'll analyze your authentication work across conversations, tasks, code, and knowledge to provide comprehensive insights.

```python
# Get cross-domain insights
auth_insights = mcp.call("get_cross_domain_insights",
                        entity_id=auth_task["id"])
```

## Contextual Search

**Prompt**: "Search for API documentation while considering I'm working on authentication."

**AI Agent Response**:
I'll search for API documentation with the context that you're working on authentication.

```python
# Contextual search
api_docs = mcp.call("search_with_context",
                   query="API documentation",
                   entity_context="authentication implementation")
```
```

## Workflow Automation

### Automation and Workflow Management

```markdown
# Workflow Automation Prompts

## Registering Workflows

**Prompt**: "I want to automate the process of creating tasks from conversations."

**AI Agent Response**:
I'll help you create an automation workflow that creates tasks from conversations.

```python
# Register automation workflow
workflow = mcp.call("automation_register_workflow",
                   workflow_definition={
                       "id": "conversation-to-task",
                       "name": "Conversation to Task Automation",
                       "description": "Automatically create tasks from conversation context",
                       "trigger": {
                           "type": "conversation_saved",
                           "conditions": {
                               "contains_action_items": True
                           }
                       },
                       "actions": [
                           {
                               "type": "create_task",
                               "params": {
                                   "source": "conversation",
                                   "priority": "medium"
                               }
                           }
                       ],
                       "enabled": True
                   })
```

## Listing Workflows

**Prompt**: "What automation workflows do I have set up?"

**AI Agent Response**:
Let me show you all your registered automation workflows.

```python
# List all workflows
workflows = mcp.call("automation_list_workflows",
                    enabled_only=False)
```

## Workflow Suggestions

**Prompt**: "What workflows would be helpful for my current work?"

**AI Agent Response**:
Let me suggest workflows that would be beneficial for your current work context.

```python
# Get workflow suggestions
workflow_suggestions = mcp.call("get_workflow_suggestions",
                               user_context={
                                   "current_project": web_project["id"],
                                   "recent_activities": ["task_creation", "conversation_saving"],
                                   "workload": "medium"
                               })
```

## Triggering Workflows

**Prompt**: "Run the conversation-to-task workflow manually."

**AI Agent Response**:
I'll manually trigger the conversation-to-task workflow for you.

```python
# Trigger workflow manually
trigger_result = mcp.call("automation_trigger_workflow",
                         workflow_id="conversation-to-task",
                         context={
                             "conversation_id": latest_context["id"],
                             "manual_trigger": True
                         })
```
```

### Example: Personal Automation Workflows

**Meow Counter Example**:
```python
# Emily's meow tracking workflow
meow_workflow = {
    "id": "meow-tracker",
    "name": "Meow Tracker",
    "description": "When a new conversation mentions 'meow', create a fun meow task.",
    "trigger": {
        "type": "conversation_saved",
        "filter": {"contains_keywords": ["meow"]}
    },
    "actions": [
        {
            "type": "create_task",
            "params": {
                "title": "Meow detected!",
                "description": "Emily said meow! Time for cat content 🐱",
                "priority": "low",
                "tags": ["meow", "fun", "cat"]
            }
        }
    ],
    "enabled": true
}

# Register the workflow
result = mcp.call("automation_register_workflow", workflow_definition=meow_workflow)

# To make this work across sessions, the AI agent should regularly save context:
def save_conversation_with_keywords(conversation_summary):
    """Save conversation context to trigger automation workflows"""
    mcp.call("handoff_save", context=conversation_summary)
    # This will trigger any workflows that match keywords in the summary
```

## 🤖 Automatic Workflow Triggering

### Overview

Workflows now **automatically trigger** when entities, relations, or contexts are created/updated in the unified memory system. This enables powerful automation scenarios like:

- Auto-creating tasks from conversations
- Notifying teams when important entities are created
- Updating project status when tasks are completed
- Creating follow-up actions from meeting notes

### Trigger Types

| Trigger | Description | When it fires |
|---------|-------------|---------------|
| `entity_created` | New entity saved | Any `memory_store.save_entity()` call for new entities |
| `entity_updated` | Existing entity updated | Any `memory_store.save_entity()` call for existing entities |
| `relation_created` | New relation saved | Any `memory_store.save_relation()` call |
| `manual` | Manually triggered | Via `automation_trigger_workflow` MCP tool |

### Filter Syntax

```python
# Simple entity type filter
workflow_def = {
    "trigger": {
        "type": "entity_created",
        "filter": {"entity.type": "note"}
    }
}

# Complex nested filters
workflow_def = {
    "trigger": {
        "type": "entity_created", 
        "filter": {
            "entity.type": "handoff",
            "entity.metadata.priority": "high",
            "entity.tags": ["urgent", "escalation"]
        }
    }
}
```

### Working Examples

#### 1. Auto-Task Creation from Notes
```python
# This workflow automatically creates tasks when notes are created
note_to_task_workflow = {
    "id": "note-to-task-auto",
    "name": "Auto-create tasks from notes",
    "description": "Automatically create follow-up tasks when notes are saved",
    "trigger": {
        "type": "entity_created",
        "filter": {"entity.type": "note"}
    },
    "actions": [
        {
            "type": "create_task",
            "params": {
                "title": "Follow up on: {{ entity.name }}",
                "content": "Action items from note: {{ entity.content }}",
                "priority": "medium"
            }
        }
    ]
}

# Register the workflow
result = mcp.call("automation_register_workflow", workflow_definition=note_to_task_workflow)

# Now when you create a note, a task is automatically created!
note = mcp.call("handoff_save", context="Discussed new project timeline - need to update milestones")
# 🤖 Auto-creates task: "Follow up on: Project Discussion"
```

#### 2. High-Priority Issue Escalation
```python
# Auto-escalate high priority issues
escalation_workflow = {
    "id": "high-priority-escalation",
    "name": "High Priority Issue Escalation",
    "description": "Automatically escalate high-priority issues",
    "trigger": {
        "type": "entity_created",
        "filter": {
            "entity.type": "handoff",
            "entity.metadata.priority": "high"
        }
    },
    "actions": [
        {
            "type": "create_task",
            "params": {
                "title": "URGENT: {{ entity.name }}",
                "priority": "high",
                "content": "High-priority issue requires immediate attention: {{ entity.content }}"
            }
        },
        {
            "type": "notify",
            "params": {
                "channel": "slack",
                "message": "🚨 High priority issue created: {{ entity.name }}"
            }
        }
    ]
}
```

#### 3. Project Status Updates
```python
# Auto-update project status when tasks are completed
project_update_workflow = {
    "id": "project-status-update",
    "name": "Project Status Auto-Update",
    "description": "Update project metadata when tasks are completed",
    "trigger": {
        "type": "entity_updated",
        "filter": {
            "entity.type": "task",
            "entity.metadata.status": "completed"
        }
    },
    "actions": [
        {
            "type": "update_entity",
            "params": {
                "entity_id": "{{ entity.metadata.project_id }}",
                "updates": {
                    "metadata.last_task_completed": "{{ entity.updated_at }}",
                    "metadata.completed_tasks_count": "{{ entity.metadata.completed_tasks_count | default(0) | int + 1 }}"
                }
            }
        }
    ]
}
```

### Testing Auto-Triggering

```python
# 1. Register a workflow
workflow = {
    "id": "test-auto-trigger",
    "name": "Test Auto-Trigger",
    "trigger": {
        "type": "entity_created",
        "filter": {"entity.type": "note"}
    },
    "actions": [{
        "type": "create_task",
        "params": {"title": "Auto-created: {{ entity.name }}"}
    }]
}
mcp.call("automation_register_workflow", workflow_definition=workflow)

# 2. Create an entity that matches the filter
mcp.call("handoff_save", context="This is a test note")

# 3. Check that a task was auto-created
tasks = mcp.call("todo_get_today")
# You should see: "Auto-created: Meeting Discussion" or similar
```

### Benefits of Auto-Triggering

✅ **Zero Manual Intervention**: Workflows run automatically when conditions are met  
✅ **Real-time Response**: Actions happen immediately when data changes  
✅ **Consistent Execution**: Never forget to run important follow-up actions  
✅ **Scalable Automation**: Handle increasing workload without manual overhead  
✅ **Cross-Domain Intelligence**: Connect handoffs, tasks, notes, and projects automatically

### Troubleshooting

**Workflow not triggering?**
1. Check filter syntax: Use `entity.type` not just `type`
2. Verify workflow is enabled: `automation_list_workflows`
3. Check event types match exactly
4. Test with simple filters first, then add complexity

**Performance considerations:**
- Workflow execution happens asynchronously  
- Failed workflows don't break data operations
- Use specific filters to avoid unnecessary triggering

## Advanced Integration Patterns

### Multi-Tool Workflows

```markdown
# Advanced Integration Patterns

## Complete Project Setup

**Prompt**: "I'm starting a new project. Help me set it up completely."

**AI Agent Response**:
I'll help you set up a complete project structure using all available tools.

```python
# 1. Create project area and project
project_area = mcp.call("todo_create_area",
                       name="New Project",
                       description="Area for new project organization")

project = mcp.call("todo_create_project",
                  name="New Project",
                  area_id=project_area["id"],
                  description="Complete project setup with documentation")

# 2. Create initial tasks
mcp.call("todo_create_task",
        title="Project Planning",
        description="Define project scope, requirements, and timeline",
        project_id=project["id"],
        priority="high")

mcp.call("todo_create_task",
        title="Setup Development Environment",
        description="Install tools, setup repository, configure IDE",
        project_id=project["id"],
        priority="high")

# 3. Document in knowledge graph
project_entity = mcp.call("graph_create_entity",
                         entity_data={
                             "type": "project",
                             "name": "New Project",
                             "content": "Complete project documentation and planning",
                             "tags": ["new-project", "planning"]
                         })

# 4. Save context for handoff
mcp.call("handoff_save",
        context=f"Started new project setup. Created project '{project['name']}' with initial tasks and documentation.")

# 5. Get smart suggestions
suggestions = mcp.call("get_smart_suggestions",
                      context={
                          "new_project": True,
                          "project_id": project["id"],
                          "setup_phase": True
                      })
```

## Meeting Follow-up Automation

**Prompt**: "I just had a meeting about the authentication system. Help me process the outcomes."

**AI Agent Response**:
I'll help you process the meeting outcomes using multiple tools.

```python
# 1. Save meeting context
meeting_context = mcp.call("handoff_save",
                          context="Meeting about authentication system implementation. Discussed OAuth2 integration, security requirements, and timeline. Action items: research OAuth providers, create security documentation, setup development environment.")

# 2. Extract and create tasks from context
mcp.call("todo_create_from_conversation",
        context_id=meeting_context["id"],
        title="Research OAuth Providers")

mcp.call("todo_create_from_conversation",
        context_id=meeting_context["id"],
        title="Create Security Documentation")

mcp.call("todo_create_from_conversation",
        context_id=meeting_context["id"],
        title="Setup Development Environment")

# 3. Update knowledge graph with meeting insights
mcp.call("graph_create_entity",
        payload={
            "type": "meeting",
            "name": "Authentication System Meeting",
            "content": "Discussed OAuth2 integration, security requirements, and implementation timeline",
            "tags": ["meeting", "authentication", "oauth2"]
        })

# 4. Get related insights
insights = mcp.call("handoff_insights",
                   context_id=meeting_context["id"])

# 5. Get next action suggestions
next_actions = mcp.call("handoff_suggest_actions",
                       context_id=meeting_context["id"])
```

## Daily Review Process

**Prompt**: "Help me do my daily review and planning."

**AI Agent Response**:
I'll help you with a comprehensive daily review using all available tools.

```python
# 1. Get today's tasks and progress
today_summary = mcp.call("todo_get_today")

# 2. Get upcoming tasks
upcoming_tasks = mcp.call("todo_get_upcoming", days=7)

# 3. Get recent context
recent_context = mcp.call("handoff_get")

# 4. Get project intelligence
project_intel = mcp.call("get_project_intelligence",
                        project_id=web_project["id"])

# 5. Get smart suggestions for tomorrow
tomorrow_suggestions = mcp.call("get_smart_suggestions",
                               context={
                                   "daily_review": True,
                                   "completed_today": today_summary["completed"],
                                   "upcoming": upcoming_tasks
                               })

# 6. Save review context
mcp.call("handoff_save",
        context=f"Daily review completed. Completed {len(today_summary['completed'])} tasks. Upcoming: {len(upcoming_tasks['tasks'])} tasks in next 7 days. Focus areas: {tomorrow_suggestions['focus_areas']}")

# 7. Create planning task for tomorrow
mcp.call("todo_create_task",
        title="Daily Planning",
        description="Review yesterday's progress and plan today's priorities",
        priority="high",
        scheduled_date="tomorrow")
```

## Knowledge Discovery Workflow

**Prompt**: "I want to understand everything about authentication in my system."

**AI Agent Response**:
I'll help you discover all knowledge about authentication across your entire system.

```python
# 1. Search across all domains
auth_search = mcp.call("intelligent_search",
                      query="authentication",
                      context={
                          "include_tasks": True,
                          "include_conversations": True,
                          "include_knowledge": True,
                          "include_code": True
                      })

# 2. Get knowledge graph entities
auth_entities = mcp.call("graph_search",
                        query="authentication")

# 3. Find related entities
related_entities = []
for entity in auth_entities:
    related = mcp.call("graph_find_related",
                      entity_id=entity["id"],
                      depth=2)
    related_entities.extend(related["entities"])

# 4. Get project intelligence
auth_projects = mcp.call("get_project_intelligence",
                        project_id=web_project["id"])

# 5. Get cross-domain insights
cross_domain = mcp.call("get_cross_domain_insights",
                       entity_id=auth_task["id"])

# 6. Create comprehensive knowledge summary
mcp.call("graph_create_entity",
        payload={
            "type": "note",
            "name": "Authentication System Knowledge",
            "content": f"Comprehensive knowledge about authentication system including {len(auth_entities)} entities, {len(related_entities)} related items, and cross-domain insights",
            "tags": ["authentication", "knowledge-summary", "system-overview"]
        })
```
```

## Error Handling

### Robust Error Management

```markdown
# Error Handling Prompts

## Graceful Error Handling

**Prompt**: "What happens if a tool fails?"

**AI Agent Response**:
I'll implement robust error handling for all tool calls.

```python
# Example error handling pattern
def safe_tool_call(tool_name, **kwargs):
    try:
        result = mcp.call(tool_name, **kwargs)
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "tool": tool_name,
            "suggestion": "Please try again or check your input parameters"
        }

# Usage example
task_result = safe_tool_call("todo_create_task",
                            title="Test task",
                            description="Testing error handling")

if not task_result["success"]:
    print(f"Failed to create task: {task_result['error']}")
    print(f"Suggestion: {task_result['suggestion']}")
```

## Fallback Strategies

**Prompt**: "What if the knowledge graph is unavailable?"

**AI Agent Response**:
I'll implement fallback strategies when tools are unavailable.

```python
# Fallback strategy for knowledge graph
def get_knowledge_with_fallback(query):
    try:
        # Try knowledge graph first
        return mcp.call("graph_search", query=query)
    except Exception as e:
        try:
            # Fallback to intelligent search
            return mcp.call("intelligent_search", query=query)
        except Exception as e2:
            # Final fallback to simple search
            return {"error": "Knowledge tools unavailable", "fallback_data": []}
```

## Validation and Verification

**Prompt**: "How do I verify that my data was saved correctly?"

**AI Agent Response**:
I'll help you implement validation and verification for your data operations.

```python
# Validation pattern
def create_and_verify_task(title, description):
    # Create task
    task = mcp.call("todo_create_task",
                   title=title,
                   description=description)
    
    # Verify creation
    verification = mcp.call("todo_get_task_details", task_id=task["id"])
    
    if verification["title"] == title:
        return {"success": True, "task": task, "verified": True}
    else:
        return {"success": False, "error": "Task creation verification failed"}
```
```

## Best Practices

### Integration Guidelines

```markdown
# Best Practices for AI Agent Integration

## 1. Context Awareness

**Always maintain context across tool calls:**
```python
# Good: Maintain context
context = {"current_project": project_id, "user_focus": "authentication"}
task = mcp.call("todo_create_task", title="Auth task", **context)

# Bad: No context
task = mcp.call("todo_create_task", title="Auth task")
```

## 2. Batch Operations

**Group related operations together:**
```python
# Good: Batch related operations
def setup_project(project_name, tasks):
    project = mcp.call("todo_create_project", name=project_name)
    
    for task in tasks:
        mcp.call("todo_create_task", 
                title=task["title"],
                project_id=project["id"])
    
    return project

# Bad: Scattered operations
project = mcp.call("todo_create_project", name=project_name)
# ... other code ...
mcp.call("todo_create_task", title="Task 1", project_id=project["id"])
# ... more code ...
mcp.call("todo_create_task", title="Task 2", project_id=project["id"])
```

## 3. Error Recovery

**Implement graceful error recovery:**
```python
def robust_operation(operation_func, *args, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)  # Brief delay before retry
```

## 4. Data Consistency

**Ensure data consistency across tools:**
```python
def create_project_with_documentation(project_name, description):
    # Create project
    project = mcp.call("todo_create_project", 
                      name=project_name,
                      description=description)
    
    # Create corresponding knowledge entity
    mcp.call("graph_create_entity",
            payload={
                "type": "project",
                "name": project_name,
                "content": description,
                "metadata": {"todo_project_id": project["id"]}
            })
    
    # Save context
    mcp.call("handoff_save",
            context=f"Created project '{project_name}' with documentation")
    
    return project
```

## 5. User Experience

**Provide helpful feedback and suggestions:**
```python
def create_task_with_suggestions(title, description):
    # Create task
    task = mcp.call("todo_create_task",
                   title=title,
                   description=description)
    
    # Get related suggestions
    suggestions = mcp.call("get_smart_suggestions",
                          context={"new_task": task["id"]})
    
    # Return with helpful information
    return {
        "task": task,
        "suggestions": suggestions,
        "next_steps": [
            "Consider adding a due date",
            "Check for related tasks",
            "Review project timeline"
        ]
    }
```

## 6. Performance Optimization

**Optimize for performance:**
```python
# Good: Batch search operations
def comprehensive_search(query):
    # Parallel search across domains
    results = {
        "tasks": mcp.call("todo_quick_find", query=query),
        "knowledge": mcp.call("graph_search", query=query),
        "conversations": mcp.call("handoff_search", query=query)
    }
    return results

# Bad: Sequential searches
def slow_search(query):
    tasks = mcp.call("todo_quick_find", query=query)
    knowledge = mcp.call("graph_search", query=query)
    conversations = mcp.call("handoff_search", query=query)
    return {"tasks": tasks, "knowledge": knowledge, "conversations": conversations}
```

## 7. Security and Privacy

**Handle sensitive data appropriately:**
```python
def safe_context_saving(context):
    # Sanitize sensitive information
    sanitized_context = sanitize_context(context)
    
    # Save with appropriate privacy settings
    return mcp.call("handoff_save",
                   context=sanitized_context)

def sanitize_context(context):
    # Remove sensitive patterns (passwords, API keys, etc.)
    import re
    patterns = [
        r'password["\s]*[:=]["\s]*[^\s,}]+',
        r'api_key["\s]*[:=]["\s]*[^\s,}]+',
        r'token["\s]*[:=]["\s]*[^\s,}]+'
    ]
    
    sanitized = context
    for pattern in patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized)
    
    return sanitized
```

## 8. Monitoring and Logging

**Implement proper monitoring:**
```python
import logging
logger = logging.getLogger(__name__)

def monitored_tool_call(tool_name, **kwargs):
    start_time = time.time()
    try:
        result = mcp.call(tool_name, **kwargs)
        duration = time.time() - start_time
        logger.info(f"Tool {tool_name} completed in {duration:.2f}s")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Tool {tool_name} failed after {duration:.2f}s: {e}")
        raise
```

## 9. Documentation

**Document your integration patterns:**
```python
"""
AI Agent Integration Patterns for Emily Tools MCP Server

This module provides reusable patterns for integrating AI agents with the
Emily Tools MCP server.

Usage:
    from integration_patterns import create_project_workflow
    
    result = create_project_workflow("My Project", ["Task 1", "Task 2"])
"""

def create_project_workflow(project_name, task_list):
    """
    Complete project setup workflow.
    
    Args:
        project_name (str): Name of the project
        task_list (list): List of task titles to create
        
    Returns:
        dict: Project information with created tasks
    """
    # Implementation here
    pass
```

## 10. Testing

**Test your integration thoroughly:**
```python
def test_integration():
    """Test basic integration functionality."""
    
    # Test todo creation
    task = mcp.call("todo_create_task", title="Test task")
    assert task["title"] == "Test task"
    
    # Test context saving
    context = mcp.call("handoff_save", context="Test context")
    assert context["context"] == "Test context"
    
    # Test knowledge creation
    entity = mcp.call("graph_create_entity",
                     entity_data={"type": "test", "name": "Test Entity"})
    assert entity["name"] == "Test Entity"
    
    print("All integration tests passed!")
```
```

This comprehensive guide provides AI agents with everything they need to effectively integrate with the Emily Tools MCP server, from basic operations to advanced patterns and best practices. 

### Workflow Definition Schema and Limitations

`automation_register_workflow(workflow_definition)` expects **exactly** this structure (extra top-level keys will be ignored and _can_ cause validation errors):
```jsonc
{
  "id": "string (unique)",        // Optional – autogenerated if omitted
  "name": "string",               // Required
  "description": "string",        // Required
  "trigger": {
    "type": "entity_created" | "entity_updated" | "relation_created" | "scheduled" | "manual",
    "filter": {                    // Optional – filter conditions for automatic triggers
      // For entity triggers, use nested syntax:
      "entity.type": "note",       // Entity type filter
      "entity.metadata.priority": "high",  // Nested metadata filter
      "entity.tags": ["urgent"]    // List matching for tags
      // For relation triggers:
      // "relation.relation_type": "depends_on"
    },
    "schedule": "cron string"      // Only for scheduled triggers (eg. "0 9 * * MON")
  },
  "actions": [                     // At least one action
    {
      "type": "create_task" | "update_entity" | "save_relation" | "notify" | "run_shell" | "http_request",
      "params": { /* action-specific */ },
      "condition": "optional Jinja expression"  // eg. "{{ entity.priority == 'high' }}"
    }
  ],
  "enabled": true                 // Optional (default true)
}
```

**Automatic Trigger Types** ✨

The system now supports **automatic workflow triggering** when data changes:

| Trigger Type      | When it fires | Filter context |
|-------------------|---------------|----------------|
| `entity_created`  | New entity saved to memory store | `entity.*` properties available |
| `entity_updated`  | Existing entity updated | `entity.*` properties available |
| `relation_created` | New relation created | `relation.*` properties available |
| `manual`          | Manually triggered via MCP tool | Custom payload |
| `scheduled`       | Cron-based scheduling | Time-based context |

**Filter Syntax for Automatic Triggers** 🎯

Use **nested property syntax** for entity and relation filters:

```jsonc
// Entity filters - use "entity." prefix
{
  "entity.type": "handoff",           // Entity type
  "entity.name": "Meeting Notes",     // Entity name (exact match)
  "entity.metadata.priority": "high", // Nested metadata
  "entity.tags": ["urgent", "bug"]    // List matching (any item matches)
}

// Relation filters - use "relation." prefix  
{
  "relation.relation_type": "depends_on",
  "relation.source_id": "specific-entity-id",
  "relation.strength": 0.8
}

// Complex filters with multiple conditions (ALL must match)
{
  "entity.type": "task",
  "entity.metadata.status": "completed",
  "entity.metadata.project_id": "project-123"
}
```

**Template Variables** 📝

Actions can use template variables from the triggering event:

```jsonc
{
  "type": "create_task",
  "params": {
    "title": "Follow up on: {{ entity.name }}",
    "content": "Action items: {{ entity.content }}",
    "priority": "{{ entity.metadata.priority | default('medium') }}",
    "tags": ["auto-created", "{{ entity.type }}"]
  }
}
```

**Currently supported action types**

| Action type      | Required params                                      |
|------------------|------------------------------------------------------|
| `create_task`    | `title` (str), `content` (str) **plus** any valid `todo_create_task` params (`priority`, `tags`, …) |
| `update_entity`  | `entity_id` (str), `updates` (dict)                 |
| `save_relation`  | `source_id`, `target_id`, `relation_type`, `strength`|
| `notify`         | `message` (str), `channel` (str)                    |
| `run_shell`      | `command` (str)                                      |
| `http_request`   | `method` ("GET"/"POST"), `url` (str), `headers`/`body` |

⚠️  **Not yet supported** – `increment_counter`, `create_knowledge_entity`, or any other custom action types. Including them will raise an "Invalid workflow definition" error.

### Working Examples ✅

#### 1. Auto-create tasks from notes
```python
note_to_task_workflow = {
    "id": "note-to-task-auto",
    "name": "Auto-create tasks from notes",
    "description": "Automatically create follow-up tasks when notes are saved",
    "trigger": {
        "type": "entity_created",
        "filter": {"entity.type": "note"}
    },
    "actions": [
        {
            "type": "create_task",
            "params": {
                "title": "Follow up on: {{ entity.name }}",
                "content": "Action items from note: {{ entity.content }}",
                "priority": "medium"
            }
        }
    ]
}

result = mcp.call("automation_register_workflow", workflow_definition=note_to_task_workflow)
```

#### 2. High-priority issue escalation
```python
escalation_workflow = {
    "id": "high-priority-escalation",
    "name": "High Priority Issue Escalation", 
    "description": "Automatically escalate high-priority handoffs",
    "trigger": {
        "type": "entity_created",
        "filter": {
            "entity.type": "handoff",
            "entity.metadata.priority": "high"
        }
    },
    "actions": [
        {
            "type": "create_task",
            "params": {
                "title": "URGENT: {{ entity.name }}",
                "priority": "high",
                "content": "High-priority issue: {{ entity.content }}"
            }
        },
        {
            "type": "notify",
            "params": {
                "channel": "slack", 
                "message": "🚨 High priority issue: {{ entity.name }}"
            }
        }
    ],
    "enabled": true
}
```

#### 3. Project status updates on task completion
```python
project_update_workflow = {
    "id": "project-status-update",
    "name": "Project Status Auto-Update",
    "description": "Update project when tasks are completed",
    "trigger": {
        "type": "entity_updated",
        "filter": {
            "entity.type": "task",
            "entity.metadata.status": "completed"
        }
    },
    "actions": [
        {
            "type": "update_entity",
            "params": {
                "entity_id": "{{ entity.metadata.project_id }}",
                "updates": {
                    "metadata.last_task_completed": "{{ entity.updated_at }}",
                    "metadata.total_completed": "{{ entity.metadata.total_completed | default(0) | int + 1 }}"
                }
            },
            "condition": "{{ entity.metadata.project_id is defined }}"
        }
    ],
    "enabled": true
}
```

### Testing Your Workflows 🧪

```python
# 1. Register a simple test workflow
test_workflow = {
    "id": "test-auto-trigger",
    "name": "Test Auto-Trigger",
    "trigger": {
        "type": "entity_created",
        "filter": {"entity.type": "note"}
    },
    "actions": [{
        "type": "create_task", 
        "params": {"title": "Auto-created: {{ entity.name }}"}
    }]
}
mcp.call("automation_register_workflow", workflow_definition=test_workflow)

# 2. Trigger by creating an entity that matches
mcp.call("handoff_save", context="This is a test note")

# 3. Verify the task was auto-created
tasks = mcp.call("todo_get_today")
# Should include: "Auto-created: [context title]"
```

**Troubleshooting**

❌ **Common Issues:**

```python
# WRONG: Old filter syntax
"filter": {"type": "note"}  # Won't work!

# CORRECT: New nested syntax  
"filter": {"entity.type": "note"}  # Works! ✅
```

```python
# WRONG: Missing required template context
"title": "Task for {{ name }}"  # 'name' not available

# CORRECT: Use entity context
"title": "Task for {{ entity.name }}"  # ✅
```

**Performance considerations:**
- Workflow execution happens asynchronously and doesn't block data operations
- Failed workflows don't break memory store operations
- Use specific filters to avoid triggering on every entity creation
- Template variables are resolved at execution time

**Debugging workflows:**
1. Check `automation_list_workflows` to verify registration
2. Ensure filters use correct nested syntax (`entity.type`, not `type`)
3. Test with simple examples before adding complexity
4. Use `automation_get_workflow` to inspect workflow definitions 