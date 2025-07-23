"""
MCP Tool Definitions for Unified Todo Tool
Phase 3.2: Advanced Todo Tool MCP Integration
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .unified_todo_tool import UnifiedTodoTool

logger = logging.getLogger(__name__)


def register_todo_mcp_tools(mcp, todo_tool: UnifiedTodoTool):
    """Register all MCP tools for the unified todo system."""
    
    @mcp.tool(
        name="todo_create_area",
        description="Create a new area (top-level organization) for grouping related projects and tasks",
        tags={"todo", "area", "organization", "create"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_create_area(name: str, description: str, color: Optional[str] = None) -> dict:
        """Create a new area (top-level organization)."""
        area = todo_tool.create_area(name=name, description=description, color=color)
        return {
            "id": area.id,
            "name": area.name,
            "description": area.content,
            "status": area.metadata.get("status"),
            "created": True
        }
    
    @mcp.tool(
        name="todo_create_project",
        description="Create a new project within an area to organize related tasks and goals",
        tags={"todo", "project", "create", "organization"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_create_project(name: str, description: str, area_id: Optional[str] = None, deadline: Optional[str] = None) -> dict:
        """Create a new project."""
        project = todo_tool.create_project(
            name=name,
            area_id=area_id,
            description=description,
            deadline=deadline
        )
        return {
            "id": project.id,
            "name": project.name,
            "description": project.content,
            "area_id": project.metadata.get("area_id"),
            "deadline": project.metadata.get("deadline"),
            "status": project.metadata.get("status"),
            "created": True
        }
    
    @mcp.tool(
        name="todo_create_task",
        description="Create a new task with advanced features like scheduling, priority, and energy level tracking",
        tags={"todo", "task", "create", "productivity"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_create_task(title: str, description: Optional[str] = None, project_id: Optional[str] = None,
                              area_id: Optional[str] = None, priority: str = "medium", 
                              scheduled_date: Optional[str] = None, due_date: Optional[str] = None,
                              energy_level: str = "medium", time_estimate: Optional[int] = None,
                              tags: Optional[List[str]] = None) -> dict:
        """Create a new task with advanced features."""
        if tags is None:
            tags = []
            
        task = todo_tool.create_task(
            title=title,
            description=description,
            project_id=project_id,
            area_id=area_id,
            priority=priority,
            scheduled_date=scheduled_date,
            due_date=due_date,
            energy_level=energy_level,
            time_estimate=time_estimate,
            tags=tags
        )
        
        return {
            "id": task.id,
            "title": task.name,
            "description": task.content,
            "priority": task.metadata.get("priority"),
            "status": task.metadata.get("status"),
            "project_id": task.metadata.get("project_id"),
            "area_id": task.metadata.get("area_id"),
            "scheduled_date": task.metadata.get("scheduled_date"),
            "due_date": task.metadata.get("due_date"),
            "energy_level": task.metadata.get("energy_level"),
            "time_estimate": task.metadata.get("time_estimate"),
            "tags": task.tags,
            "created": True
        }
    
    @mcp.tool(
        name="todo_create_task_nl",
        description="Create task from natural language input using AI to parse intent, priority, and scheduling",
        tags={"todo", "task", "ai", "natural-language", "create"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_create_task_nl(input_text: str) -> dict:
        """Create task from natural language input."""
        task = todo_tool.create_task_with_natural_language(input_text)
        return {
            "id": task.id,
            "title": task.name,
            "description": task.content,
            "priority": task.metadata.get("priority"),
            "status": task.metadata.get("status"),
            "scheduled_date": task.metadata.get("scheduled_date"),
            "tags": task.tags,
            "created": True
        }
    
    @mcp.tool(
        name="todo_create_from_conversation",
        description="Create task from conversation context by analyzing chat history and extracting actionable items",
        tags={"todo", "task", "conversation", "ai", "create"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_create_from_conversation(context_id: str, title: Optional[str] = None) -> dict:
        """Create task from conversation context."""
        task = todo_tool.create_task_from_conversation(context_id, title)
        return {
            "task_id": task.id,
            "title": task.name,
            "description": task.content,
            "priority": task.metadata.get("priority"),
            "source_context": task.metadata.get("source_context"),
            "created": True
        }
    
    @mcp.tool(
        name="todo_get_today",
        description="Get today's tasks with AI suggestions for prioritization and scheduling optimization",
        tags={"todo", "task", "today", "schedule", "ai"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_today() -> dict:
        """Get today's tasks with AI suggestions."""
        return todo_tool.get_today_tasks()
    
    @mcp.tool(
        name="todo_get_evening",
        description="Get tasks suitable for evening work based on energy level and context requirements",
        tags={"todo", "task", "evening", "energy", "schedule"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_evening() -> list:
        """Get tasks suitable for evening work."""
        return todo_tool.get_evening_tasks()
    
    @mcp.tool(
        name="todo_get_upcoming",
        description="Get upcoming tasks and events within a specified timeframe for planning and preparation",
        tags={"todo", "task", "upcoming", "schedule", "planning"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_upcoming(days: int = 7) -> dict:
        """Get upcoming tasks and events."""
        return todo_tool.get_upcoming_tasks(days)
    
    @mcp.tool(
        name="todo_get_anytime",
        description="Get tasks without specific scheduling that can be done at any convenient time",
        tags={"todo", "task", "anytime", "flexible", "schedule"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_anytime() -> list:
        """Get tasks without specific scheduling."""
        return todo_tool.get_anytime_tasks()
    
    @mcp.tool(
        name="todo_get_someday",
        description="Get tasks marked for future consideration that are not immediately actionable",
        tags={"todo", "task", "someday", "future", "planning"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_someday() -> list:
        """Get tasks marked for future consideration."""
        return todo_tool.get_someday_tasks()
    
    @mcp.tool(
        name="todo_list_areas",
        description="List all areas (top-level organization containers) with optional status filtering",
        tags={"todo", "area", "list", "organization"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_list_areas(status: str = "active") -> list:
        """List all areas."""
        areas = todo_tool.get_areas(status)
        return [
            {
                "id": area.id,
                "name": area.name,
                "description": area.description,
                "status": area.metadata.get("status"),
                "color": area.metadata.get("color")
            }
            for area in areas
        ]
    
    @mcp.tool(
        name="todo_list_projects",
        description="List projects with optional filtering by area and status for project management overview",
        tags={"todo", "project", "list", "organization", "management"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_list_projects(area_id: Optional[str] = None, status: str = "active") -> list:
        """List projects, optionally filtered by area."""
        projects = todo_tool.get_projects(area_id, status)
        return [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "area_id": project.metadata.get("area_id"),
                "status": project.metadata.get("status"),
                "deadline": project.metadata.get("deadline"),
                "progress": project.metadata.get("progress", 0.0)
            }
            for project in projects
        ]
    
    @mcp.tool(
        name="todo_complete_task",
        description="Mark a task as completed and update its status with completion metadata",
        tags={"todo", "task", "complete", "status", "update"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def todo_complete_task(task_id: str) -> dict:
        """Complete a task."""
        task = todo_tool.complete_task(task_id)
        return {
            "id": task.id,
            "title": task.name,
            "status": task.metadata.get("status"),
            "completed_at": task.metadata.get("completed_at"),
            "completed": True
        }
    
    @mcp.tool(
        name="todo_complete_project",
        description="Complete a project and all its associated tasks in bulk operation",
        tags={"todo", "project", "complete", "bulk", "management"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def todo_complete_project(project_id: str) -> dict:
        """Complete a project and all its tasks."""
        result = todo_tool.complete_project(project_id)
        return result
    
    @mcp.tool(
        name="todo_get_project_progress",
        description="Get detailed project progress including completion rates, task breakdown, and milestones",
        tags={"todo", "project", "progress", "analytics", "tracking"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_project_progress(project_id: str) -> dict:
        """Get detailed project progress."""
        return todo_tool.get_project_progress(project_id)
    
    @mcp.tool(
        name="todo_project_timeline",
        description="Get complete project timeline across all data types including tasks, milestones, and deadlines",
        tags={"todo", "project", "timeline", "tracking", "history"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_project_timeline(project_id: str) -> list:
        """Get complete project timeline across all data types."""
        return todo_tool.get_project_timeline(project_id)
    
    @mcp.tool(
        name="todo_suggest_priorities",
        description="Get AI-suggested task priorities based on context, deadlines, and workload analysis",
        tags={"todo", "task", "ai", "priorities", "suggestions"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": False
        }
    )
    async def todo_suggest_priorities() -> list:
        """Get AI-suggested task priorities based on context."""
        return todo_tool.suggest_task_priorities()
    
    @mcp.tool(
        name="todo_quick_find",
        description="Quick semantic search across tasks, projects, and areas using AI-powered search capabilities",
        tags={"todo", "search", "ai", "find", "semantic"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_quick_find(query: str) -> dict:
        """Quick find across tasks, projects, areas with AI search."""
        return todo_tool.quick_find(query)
    
    @mcp.tool(
        name="todo_update_task",
        description="Update a task's properties including status, priority, scheduling, and project assignment",
        tags={"todo", "task", "update", "modify", "management"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def todo_update_task(task_id: str, title: Optional[str] = None, description: Optional[str] = None,
                              status: Optional[str] = None, priority: Optional[str] = None,
                              project_id: Optional[str] = None, area_id: Optional[str] = None,
                              scheduled_date: Optional[str] = None, due_date: Optional[str] = None,
                              energy_level: Optional[str] = None, time_estimate: Optional[int] = None,
                              tags: Optional[List[str]] = None) -> dict:
        """Update a task's properties."""
        # Build updates dict from non-None parameters
        updates = {}
        if title is not None:
            updates["name"] = title
        if description is not None:
            updates["content"] = description
        if status is not None:
            updates["status"] = status
        if priority is not None:
            updates["priority"] = priority
        if project_id is not None:
            updates["project_id"] = project_id
        if area_id is not None:
            updates["area_id"] = area_id
        if scheduled_date is not None:
            updates["scheduled_date"] = scheduled_date
        if due_date is not None:
            updates["due_date"] = due_date
        if energy_level is not None:
            updates["energy_level"] = energy_level
        if time_estimate is not None:
            updates["time_estimate"] = time_estimate
        if tags is not None:
            updates["tags"] = tags
            
        task = todo_tool.update_task(task_id, **updates)
        return {
            "id": task.id,
            "title": task.name,
            "description": task.content,
            "priority": task.metadata.get("priority"),
            "status": task.metadata.get("status"),
            "project_id": task.metadata.get("project_id"),
            "area_id": task.metadata.get("area_id"),
            "scheduled_date": task.metadata.get("scheduled_date"),
            "due_date": task.metadata.get("due_date"),
            "energy_level": task.metadata.get("energy_level"),
            "time_estimate": task.metadata.get("time_estimate"),
            "tags": task.tags,
            "updated": True
        }
    
    @mcp.tool()
    async def todo_update_project(project_id: str, name: Optional[str] = None, description: Optional[str] = None,
                                 area_id: Optional[str] = None, status: Optional[str] = None,
                                 deadline: Optional[str] = None, progress: Optional[float] = None,
                                 color: Optional[str] = None) -> dict:
        """Update a project's properties."""
        project = todo_tool.memory.get_entity(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Update fields
        if name is not None:
            project.name = name
        if description is not None:
            project.content = description
        if area_id is not None:
            project.metadata["area_id"] = area_id
        if status is not None:
            project.metadata["status"] = status
        if deadline is not None:
            project.metadata["deadline"] = deadline
        if progress is not None:
            project.metadata["progress"] = progress
        if color is not None:
            project.metadata["color"] = color
        
        updated_project = todo_tool.memory.update_entity(project)
        return {
            "id": updated_project.id,
            "name": updated_project.name,
            "description": updated_project.content,
            "area_id": updated_project.metadata.get("area_id"),
            "status": updated_project.metadata.get("status"),
            "deadline": updated_project.metadata.get("deadline"),
            "progress": updated_project.metadata.get("progress"),
            "updated": True
        }
    
    @mcp.tool(
        name="todo_archive_area",
        description="Archive an area and all its projects to remove them from active view while preserving data",
        tags={"todo", "area", "archive", "organization", "cleanup"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def todo_archive_area(area_id: str) -> dict:
        """Archive an area and all its projects."""
        success = todo_tool.archive_area(area_id)
        return {
            "area_id": area_id,
            "archived": success,
            "message": "Area archived successfully" if success else "Area not found"
        }
    
    @mcp.tool(
        name="todo_delete_task",
        description="Permanently delete a task from the system",
        tags={"todo", "task", "delete", "remove", "cleanup"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def todo_delete_task(task_id: str) -> dict:
        """Delete a task."""
        success = todo_tool.delete_task(task_id)
        return {
            "task_id": task_id,
            "deleted": success,
            "message": "Task deleted successfully" if success else "Task not found"
        }
    
    @mcp.tool(
        name="todo_get_statistics",
        description="Get comprehensive todo statistics including task counts, project status, and productivity metrics",
        tags={"todo", "statistics", "analytics", "metrics", "overview"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_statistics() -> dict:
        """Get comprehensive todo statistics."""
        # Get basic counts
        all_tasks = todo_tool.memory.search("", filters={"type": "task"})
        all_projects = todo_tool.memory.search("", filters={"type": "project"})
        all_areas = todo_tool.memory.search("", filters={"type": "area"})
        
        # Task statistics
        task_stats = {
            "total": len(all_tasks),
            "by_status": {},
            "by_priority": {},
            "by_energy_level": {},
            "overdue": len(todo_tool._get_overdue_tasks()),
            "scheduled_today": len(todo_tool.memory.search("", filters={
                "type": "task",
                "metadata.scheduled_date": datetime.now().strftime("%Y-%m-%d")
            }))
        }
        
        # Count by status
        for task in all_tasks:
            status = task.get('metadata', {}).get('status', 'todo')
            task_stats["by_status"][status] = task_stats["by_status"].get(status, 0) + 1
            
            priority = task.get('metadata', {}).get('priority', 'medium')
            task_stats["by_priority"][priority] = task_stats["by_priority"].get(priority, 0) + 1
            
            energy = task.get('metadata', {}).get('energy_level', 'medium')
            task_stats["by_energy_level"][energy] = task_stats["by_energy_level"].get(energy, 0) + 1
        
        # Project statistics
        project_stats = {
            "total": len(all_projects),
            "active": len([p for p in all_projects if p.get('metadata', {}).get('status') == 'active']),
            "completed": len([p for p in all_projects if p.get('metadata', {}).get('status') == 'completed']),
            "on_hold": len([p for p in all_projects if p.get('metadata', {}).get('status') == 'on_hold'])
        }
        
        # Area statistics
        area_stats = {
            "total": len(all_areas),
            "active": len([a for a in all_areas if a.get('metadata', {}).get('status') == 'active']),
            "archived": len([a for a in all_areas if a.get('metadata', {}).get('status') == 'archived'])
        }
        
        return {
            "tasks": task_stats,
            "projects": project_stats,
            "areas": area_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    @mcp.tool(
        name="todo_search_tasks",
        description="Search tasks with advanced filtering capabilities including metadata, tags, and content search",
        tags={"todo", "task", "search", "filter", "advanced"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_search_tasks(query: str, filters: Optional[Dict[str, Any]] = None) -> list:
        """Search tasks with advanced filtering."""
        if filters is None:
            filters = {}
        
        tasks = todo_tool.memory.search(query, filters)
        return [
            {
                "id": task['id'],
                "title": task['name'],
                "description": task.get('description'),
                "priority": task.get('metadata', {}).get('priority'),
                "status": task.get('metadata', {}).get('status'),
                "project_id": task.get('metadata', {}).get('project_id'),
                "area_id": task.get('metadata', {}).get('area_id'),
                "scheduled_date": task.get('metadata', {}).get('scheduled_date'),
                "due_date": task.get('metadata', {}).get('due_date'),
                "energy_level": task.get('metadata', {}).get('energy_level'),
                "time_estimate": task.get('metadata', {}).get('time_estimate'),
                "tags": task.get('tags', [])
            }
            for task in tasks
        ]
    
    @mcp.tool(
        name="todo_get_task_details",
        description="Get detailed task information including relationships, project context, and area assignments",
        tags={"todo", "task", "details", "relationships", "context"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def todo_get_task_details(task_id: str) -> dict:
        """Get detailed task information including relationships."""
        task = todo_tool.memory.get_entity(task_id)
        if not task:
            return {"error": "Task not found"}
        
        # Get related entities
        related = todo_tool.memory.get_related(task_id)
        
        # Get project details if task belongs to a project
        project = None
        if task.metadata.get('project_id'):
            project = todo_tool.memory.get_entity(task.metadata['project_id'])
        
        # Get area details if task belongs to an area
        area = None
        if task.metadata.get('area_id'):
            area = todo_tool.memory.get_entity(task.metadata['area_id'])
        
        return {
            "task": {
                "id": task.id,
                "title": task.name,
                "description": task.description,
                "priority": task.metadata.get('priority'),
                "status": task.metadata.get('status'),
                "project_id": task.metadata.get('project_id'),
                "area_id": task.metadata.get('area_id'),
                "scheduled_date": task.metadata.get('scheduled_date'),
                "due_date": task.metadata.get('due_date'),
                "energy_level": task.metadata.get('energy_level'),
                "time_estimate": task.metadata.get('time_estimate'),
                "tags": task.tags,
                "created_at": task.created_at,
                "updated_at": task.updated_at
            },
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.metadata.get('status'),
                "progress": project.metadata.get('progress')
            } if project else None,
            "area": {
                "id": area.id,
                "name": area.name,
                "description": area.description,
                "status": area.metadata.get('status')
            } if area else None,
            "related_entities": [
                {
                    "id": entity['id'],
                    "type": entity['type'],
                    "name": entity['name'],
                    "relation_type": rel.relation_type
                }
                for entity, rel in related
            ]
        }
    
    logger.info("Todo MCP tools registered successfully")