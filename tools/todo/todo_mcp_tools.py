"""
MCP Tool Definitions for Unified Todo Tool
Phase 3.2: Advanced Todo Tool MCP Integration
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from .unified_todo_tool import UnifiedTodoTool


def register_todo_mcp_tools(mcp, todo_tool: UnifiedTodoTool):
    """Register all MCP tools for the unified todo system."""
    
    @mcp.tool()
    async def todo_create_area(name: str, description: str = None, color: str = None) -> dict:
        """Create a new area (top-level organization)."""
        area = todo_tool.create_area(name=name, description=description, color=color)
        return {
            "id": area.id,
            "name": area.name,
            "description": area.description,
            "status": area.metadata.get("status"),
            "created": True
        }
    
    @mcp.tool()
    async def todo_create_project(name: str, area_id: str = None, description: str = None, 
                                deadline: str = None) -> dict:
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
            "description": project.description,
            "area_id": project.metadata.get("area_id"),
            "deadline": project.metadata.get("deadline"),
            "status": project.metadata.get("status"),
            "created": True
        }
    
    @mcp.tool()
    async def todo_create_task(title: str, description: str = None, project_id: str = None,
                              area_id: str = None, priority: str = "medium", 
                              scheduled_date: str = None, due_date: str = None,
                              energy_level: str = "medium", time_estimate: int = None,
                              tags: list = None) -> dict:
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
            "description": task.description,
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
    
    @mcp.tool()
    async def todo_create_task_nl(input_text: str) -> dict:
        """Create task from natural language input."""
        task = todo_tool.create_task_with_natural_language(input_text)
        return {
            "id": task.id,
            "title": task.name,
            "description": task.description,
            "priority": task.metadata.get("priority"),
            "status": task.metadata.get("status"),
            "scheduled_date": task.metadata.get("scheduled_date"),
            "tags": task.tags,
            "created": True
        }
    
    @mcp.tool()
    async def todo_create_from_conversation(context_id: str, title: str = None) -> dict:
        """Create task from conversation context."""
        task = todo_tool.create_task_from_conversation(context_id, title)
        return {
            "task_id": task.id,
            "title": task.name,
            "description": task.description,
            "priority": task.metadata.get("priority"),
            "source_context": task.metadata.get("source_context"),
            "created": True
        }
    
    @mcp.tool()
    async def todo_get_today() -> dict:
        """Get today's tasks with AI suggestions."""
        return todo_tool.get_today_tasks()
    
    @mcp.tool()
    async def todo_get_evening() -> list:
        """Get tasks suitable for evening work."""
        return todo_tool.get_evening_tasks()
    
    @mcp.tool()
    async def todo_get_upcoming(days: int = 7) -> dict:
        """Get upcoming tasks and events."""
        return todo_tool.get_upcoming_tasks(days)
    
    @mcp.tool()
    async def todo_get_anytime() -> list:
        """Get tasks without specific scheduling."""
        return todo_tool.get_anytime_tasks()
    
    @mcp.tool()
    async def todo_get_someday() -> list:
        """Get tasks marked for future consideration."""
        return todo_tool.get_someday_tasks()
    
    @mcp.tool()
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
    
    @mcp.tool()
    async def todo_list_projects(area_id: str = None, status: str = "active") -> list:
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
    
    @mcp.tool()
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
    
    @mcp.tool()
    async def todo_complete_project(project_id: str) -> dict:
        """Complete a project and all its tasks."""
        result = todo_tool.complete_project(project_id)
        return result
    
    @mcp.tool()
    async def todo_get_project_progress(project_id: str) -> dict:
        """Get detailed project progress."""
        return todo_tool.get_project_progress(project_id)
    
    @mcp.tool()
    async def todo_project_timeline(project_id: str) -> list:
        """Get complete project timeline across all data types."""
        return todo_tool.get_project_timeline(project_id)
    
    @mcp.tool()
    async def todo_suggest_priorities() -> list:
        """Get AI-suggested task priorities based on context."""
        return todo_tool.suggest_task_priorities()
    
    @mcp.tool()
    async def todo_quick_find(query: str) -> dict:
        """Quick find across tasks, projects, areas with AI search."""
        return todo_tool.quick_find(query)
    
    @mcp.tool()
    async def todo_update_task(task_id: str, **updates) -> dict:
        """Update a task's properties."""
        task = todo_tool.update_task(task_id, **updates)
        return {
            "id": task.id,
            "title": task.name,
            "description": task.description,
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
    async def todo_update_project(project_id: str, **updates) -> dict:
        """Update a project's properties."""
        project = todo_tool.memory.get_entity(project_id)
        if not project:
            return {"error": "Project not found"}
        
        # Update fields
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
            elif key in project.metadata:
                project.metadata[key] = value
        
        updated_project = todo_tool.memory.update_entity(project)
        return {
            "id": updated_project.id,
            "name": updated_project.name,
            "description": updated_project.description,
            "area_id": updated_project.metadata.get("area_id"),
            "status": updated_project.metadata.get("status"),
            "deadline": updated_project.metadata.get("deadline"),
            "progress": updated_project.metadata.get("progress"),
            "updated": True
        }
    
    @mcp.tool()
    async def todo_archive_area(area_id: str) -> dict:
        """Archive an area and all its projects."""
        success = todo_tool.archive_area(area_id)
        return {
            "area_id": area_id,
            "archived": success,
            "message": "Area archived successfully" if success else "Area not found"
        }
    
    @mcp.tool()
    async def todo_delete_task(task_id: str) -> dict:
        """Delete a task."""
        success = todo_tool.delete_task(task_id)
        return {
            "task_id": task_id,
            "deleted": success,
            "message": "Task deleted successfully" if success else "Task not found"
        }
    
    @mcp.tool()
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
    
    @mcp.tool()
    async def todo_search_tasks(query: str, filters: dict = None) -> list:
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
    
    @mcp.tool()
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