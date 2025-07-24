"""
Unified Todo Tool - advanced implementation with unified memory integration.
Phase 3.2: Advanced Todo Tool
"""

import logging
import re
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

from pydantic import BaseModel, Field

from emily_common import BaseTool
from emily_core import UnifiedMemoryStore, MemoryEntity, MemoryRelation, MemoryContext

logger = logging.getLogger(__name__)

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EnergyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class AreaStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ChecklistItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)


class UnifiedTodoTool(BaseTool):
    """Advanced todo tool with unified memory intelligence."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.tool_name = "todo"
    
    @property
    def name(self) -> str:
        return "unified_todo"
    
    @property
    def description(self) -> str:
        return "Advanced todo management with AI enhancements and unified memory integration"
    
    def get_capabilities(self) -> List[str]:
        return [
            "create_area",
            "create_project", 
            "create_task",
            "create_heading",
            "get_today_tasks",
            "get_evening_tasks",
            "get_upcoming_tasks",
            "get_anytime_tasks",
            "get_someday_tasks",
            "create_task_from_conversation",
            "create_task_with_natural_language",
            "get_project_timeline",
            "suggest_task_priorities",
            "quick_find"
        ]

    # Areas Management
    
    def create_area(self, name: str, description: str, color: Optional[str] = None, **kwargs) -> MemoryEntity:
        """Create a new area (top-level organization)."""
        metadata = {
            "status": kwargs.get("status", "active"),
            "color": color,
            "order": kwargs.get("order", 0)
        }
        
        entity = MemoryEntity(
            id=str(uuid.uuid4()),
            name=name,
            content=description,
            type="area",
            tags=kwargs.get("tags", []),
            metadata=metadata
        )
        
        return self.memory.save_entity(entity)
    
    def get_areas(self, status: str = "active") -> List[MemoryEntity]:
        """Get all areas, optionally filtered by status."""
        areas = self.memory.search_entities("area")
        if status:
            areas = [area for area in areas if area.metadata.get("status") == status]
        return areas
    
    def update_area(self, area_id: str, **updates) -> MemoryEntity:
        """Update an area's properties."""
        area = self.memory.get_entity(area_id)
        if not area:
            raise ValueError(f"Area {area_id} not found")
        
        # Update fields
        for key, value in updates.items():
            if key == "description":
                # Map description to content
                area.content = value
            elif hasattr(area, key):
                setattr(area, key, value)
            elif key in area.metadata:
                area.metadata[key] = value
        
        return self.memory.update_entity(area)
    
    def update_project(self, project_id: str, **updates) -> MemoryEntity:
        """Update a project's properties."""
        project = self.memory.get_entity(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Update fields
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
            elif key in project.metadata:
                project.metadata[key] = value
        
        return self.memory.update_entity(project)
    
    def archive_area(self, area_id: str) -> bool:
        """Archive an area and all its projects."""
        area = self.memory.get_entity(area_id)
        if not area:
            return False
        
        # Archive the area
        area.metadata["status"] = "archived"
        self.memory.update_entity(area)
        
        # Archive all projects in this area
        projects = self.memory.search_entities("project")
        projects = [project for project in projects if project.metadata.get("area_id") == area_id]
        
        for project in projects:
            project.metadata["status"] = "on_hold"
            self.memory.update_entity(project)
        
        return True

    # Projects Management
    def create_project(self, name: str, area_id: Optional[str] = None, description: Optional[str] = None, 
                      deadline: Optional[str] = None, **kwargs) -> MemoryEntity:
        """Create a new project."""
        metadata = {
            "area_id": area_id,
            "status": kwargs.get("status", "active"),
            "deadline": deadline,
            "progress": kwargs.get("progress", 0.0),
            "color": kwargs.get("color")
        }
        
        entity = MemoryEntity(
            id=str(uuid.uuid4()),
            name=name,
            content=description or "",
            type="project",
            tags=kwargs.get("tags", []),
            metadata=metadata
        )
        
        return self.memory.save_entity(entity)
    
    def get_projects(self, area_id: Optional[str] = None, status: str = "active") -> List[MemoryEntity]:
        """Get projects, optionally filtered by area and status."""
        projects = self.memory.search_entities("project")
        
        # Filter by status
        if status:
            projects = [project for project in projects if project.metadata.get("status") == status]
        
        # Filter by area_id
        if area_id:
            projects = [project for project in projects if project.metadata.get("area_id") == area_id]
        
        return projects
    
    def complete_project(self, project_id: str) -> Dict[str, Any]:
        """Complete a project and return summary."""
        project = self.memory.get_entity(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get all tasks in this project
        project_tasks = self.memory.search_entities("task")
        project_tasks = [task for task in project_tasks if task.metadata.get("project_id") == project_id]
        
        # Update project status
        project.metadata["status"] = "completed"
        project.metadata["completed_at"] = datetime.now().isoformat()
        self.memory.update_entity(project)
        
        # Complete all remaining tasks
        completed_tasks = 0
        for task in project_tasks:
            if task.metadata.get("status") == "todo":
                task.metadata["status"] = "completed"
                task.metadata["completed_at"] = datetime.now().isoformat()
                self.memory.update_entity(task)
                completed_tasks += 1
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": len(project_tasks),
            "completed_tasks": completed_tasks,
            "completion_date": datetime.now().isoformat()
        }
    
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get detailed project progress."""
        project = self.memory.get_entity(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project_tasks = self.memory.search_entities("task")
        project_tasks = [task for task in project_tasks if task.metadata.get("project_id") == project_id]
        
        total_tasks = len(project_tasks)
        completed_tasks = len([t for t in project_tasks if t.metadata.get("status") == "completed"])
        in_progress_tasks = len([t for t in project_tasks if t.metadata.get("status") == "in_progress"])
        
        progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": total_tasks - completed_tasks - in_progress_tasks,
            "progress_percentage": progress * 100,
            "deadline": project.metadata.get("deadline")
        }

    # Tasks Management
    def create_task(self, title: str, description: Optional[str] = None, project_id: Optional[str] = None,
                   area_id: Optional[str] = None, heading_id: Optional[str] = None, priority: str = "medium",
                   scheduled_date: Optional[str] = None, due_date: Optional[str] = None, energy_level: str = "medium",
                   time_estimate: Optional[int] = None, checklist: Optional[List[Dict]] = None, **kwargs) -> MemoryEntity:
        """Create a new task with advanced features."""
        metadata = {
            "status": kwargs.get("status", "todo"),
            "priority": priority,
            "project_id": project_id,
            "area_id": area_id,
            "heading_id": heading_id,
            "scheduled_date": scheduled_date,
            "due_date": due_date,
            "checklist": checklist or [],
            "repeat_pattern": kwargs.get("repeat_pattern"),
            "energy_level": energy_level,
            "time_estimate": time_estimate
        }
        # Merge any extra metadata provided in kwargs
        if "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            metadata.update(kwargs["metadata"])
        
        entity = MemoryEntity(
            id=str(uuid.uuid4()),
            name=title,
            content=description or "",
            type="task",
            tags=kwargs.get("tags", []),
            metadata=metadata
        )
        
        return self.memory.save_entity(entity)
    
    def update_task(self, task_id: str, **updates) -> MemoryEntity:
        """Update a task's properties."""
        task = self.memory.get_entity(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
            elif key in task.metadata:
                task.metadata[key] = value
        
        return self.memory.update_entity(task)
    
    def complete_task(self, task_id: str) -> MemoryEntity:
        """Complete a task and handle any repeat patterns."""
        task = self.memory.get_entity(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Mark as completed
        task.metadata["status"] = "completed"
        task.metadata["completed_at"] = datetime.now().isoformat()
        
        # Handle repeat patterns
        repeat_pattern = task.metadata.get("repeat_pattern")
        if repeat_pattern:
            new_task = self._create_repeat_task(task, repeat_pattern)
            if new_task:
                self.memory.save_entity(new_task)
        
        return self.memory.update_entity(task)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return self.memory.delete_entity(task_id)
    
    def _create_repeat_task(self, original_task: MemoryEntity, repeat_pattern: str) -> Optional[MemoryEntity]:
        """Create a new task based on repeat pattern."""
        now = datetime.now()
        
        if repeat_pattern == "daily":
            next_date = now + timedelta(days=1)
        elif repeat_pattern == "weekly":
            next_date = now + timedelta(weeks=1)
        elif repeat_pattern == "monthly":
            next_date = now + timedelta(days=30)
        else:
            return None
        
        # Create new task with next occurrence date
        new_task = MemoryEntity(
            id=str(uuid.uuid4()),
            name=original_task.name,
            content=original_task.content,
            type="task",
            tags=original_task.tags,
            metadata={
                **original_task.metadata,
                "status": "todo",
                "scheduled_date": next_date.strftime("%Y-%m-%d"),
                "completed_at": None
            }
        )
        
        return new_task

    # Smart Lists Implementation
    def get_today_tasks(self) -> Dict[str, List]:
        """AI-enhanced Today list combining scheduled + suggested tasks."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Get explicitly scheduled tasks
        scheduled_tasks = self.memory.search_entities("task")
        scheduled_tasks = [task for task in scheduled_tasks 
                          if task.metadata.get("scheduled_date") == today_str 
                          and task.metadata.get("status") in ["todo", "in_progress"]]
        
        # Get overdue tasks
        overdue_tasks = self._get_overdue_tasks()
        
        # AI-suggested tasks based on context and patterns
        suggested_tasks = self._ai_suggest_today_tasks()
        
        # Get related calendar events (placeholder for future integration)
        calendar_events = self._get_calendar_events(today_str)
        
        return {
            "scheduled": scheduled_tasks,
            "overdue": overdue_tasks,
            "suggested": suggested_tasks,
            "calendar_events": calendar_events,
            "evening": self.get_evening_tasks()
        }
    
    def get_evening_tasks(self) -> List[MemoryEntity]:
        """Get tasks suitable for evening work."""
        evening_tasks = self.memory.search_entities("task")
        evening_tasks = [task for task in evening_tasks 
                        if task.metadata.get("energy_level") == "low" 
                        and task.metadata.get("status") == "todo"]
        
        # Also include tasks tagged with evening-related tags
        evening_tagged = self.memory.search_entities("task")
        evening_tagged = [task for task in evening_tagged 
                         if any(tag in task.tags for tag in ["evening", "low-energy", "reading", "planning"])
                         and task.metadata.get("status") == "todo"]
        
        # Combine and deduplicate
        # Ensure we have lists before adding them
        evening_list = evening_tasks if evening_tasks is not None else []
        evening_tagged_list = evening_tagged if evening_tagged is not None else []
        
        all_evening = evening_list + evening_tagged_list
        unique_evening = {}
        for task in all_evening:
            unique_evening[task.id] = task
        
        return list(unique_evening.values())
    
    def get_upcoming_tasks(self, days: int = 7) -> Dict[str, List]:
        """Upcoming view with AI enhancements."""
        upcoming = {}
    
        for day_offset in range(days):
            logger.info(f"Day offset: {day_offset} {timedelta(days=day_offset)}")
            target_date = datetime.now() + timedelta(days=day_offset)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Tasks scheduled for this date
            scheduled = self.memory.search("", filters={
                "type": "task",
                "metadata.scheduled_date": date_str
            })
            
            # Tasks due on this date
            due_tasks = self.memory.search("", filters={
                "type": "task", 
                "metadata.due_date": date_str
            })
            
            # Project deadlines
            project_deadlines = self.memory.search("", filters={
                "type": "project",
                "metadata.deadline": date_str
            })
            
            # Calendar events (placeholder)
            calendar_events = self._get_calendar_events(date_str)
            
            # AI suggestions for this date
            date_suggestions = self._suggest_for_date(target_date)
            
            # Ensure we have lists before adding them
            scheduled_list = scheduled if scheduled is not None else []
            due_tasks_list = due_tasks if due_tasks is not None else []
            project_deadlines_list = project_deadlines if project_deadlines is not None else []
            calendar_events_list = calendar_events if calendar_events is not None else []
            date_suggestions_list = date_suggestions if date_suggestions is not None else []
            
            upcoming[date_str] = {
                "date": target_date.isoformat(),
                "scheduled_tasks": scheduled_list,
                "due_tasks": due_tasks_list,
                "project_deadlines": project_deadlines_list,
                "calendar_events": calendar_events_list,
                "suggestions": date_suggestions_list,
                "workload_score": self._calculate_workload_score(scheduled_list + due_tasks_list)
            }
        
        return upcoming
    
    def get_anytime_tasks(self) -> List[MemoryEntity]:
        """Get tasks without specific scheduling."""
        tasks = self.memory.search_entities("task")
        return [task for task in tasks 
                if task.metadata.get("status") == "todo"
                and not task.metadata.get("scheduled_date")
                and not task.metadata.get("due_date")]
    
    def get_someday_tasks(self) -> List[MemoryEntity]:
        """Get tasks marked for future consideration."""
        someday_tasks = self.memory.search_entities("task")
        someday_tasks = [task for task in someday_tasks 
                        if any(tag in task.tags for tag in ["someday", "maybe", "later"])
                        and task.metadata.get("status") == "todo"]
        
        # Also include low priority tasks without deadlines
        low_priority = self.memory.search_entities("task")
        low_priority = [task for task in low_priority 
                       if task.metadata.get("priority") == "low"
                       and task.metadata.get("status") == "todo"
                       and not task.metadata.get("due_date")]
        
        # Combine and deduplicate
        # Ensure we have lists before adding them
        someday_list = someday_tasks if someday_tasks is not None else []
        low_priority_list = low_priority if low_priority is not None else []
        
        all_someday = someday_list + low_priority_list
        unique_someday = {}
        for task in all_someday:
            unique_someday[task.id] = task
        
        return list(unique_someday.values())

    # AI-Enhanced Features
    def create_task_from_conversation(self, context_id: str, suggested_title: Optional[str] = None) -> MemoryEntity:
        """Create task from handoff context with AI extraction."""
        
        # Get the conversation context
        context = self.memory.get_entity(context_id)
        if not context:
            raise ValueError(f"Context {context_id} not found")
        
        # Extract action items if no title provided
        if not suggested_title:
            action_items = self.memory.extract_action_items(context.content)
            if action_items:
                suggested_title = action_items[0]
            else:
                suggested_title = f"Follow up on: {context.content[:50]}..."
        
        # Determine priority based on conversation urgency
        priority = self._analyze_conversation_urgency(context.content)
        
        # Find related project/area from conversation entities
        related_entities = self.memory.get_related(context_id)
        project_id = None
        area_id = None
        
        for entity in related_entities:
            if entity.get('type') == 'project':
                project_id = entity['id']
                break
        
        # Create task with conversation linkage
        task = self.create_task(
            title=suggested_title,
            description=f"Created from conversation: {context.content[:200]}...",
            priority=priority,
            project_id=project_id,
            area_id=area_id,
            metadata={
                'source_context': context_id,
                'auto_created': True
            }
        )
        
        # Link task to conversation
        self.memory.save_relation(MemoryRelation(
            source_id=task.id,
            target_id=context_id,
            relation_type='follows_from',
            strength=1.0,
            metadata={'creation_method': 'conversation_extraction'}
        ))
        
        return task
    
    def create_task_with_natural_language(self, input_text: str) -> MemoryEntity:
        """Create task from natural language input."""
        # Parse: "Call Alice about the API design tomorrow #urgent #work"
        
        # Extract title (main action) - remove date/time references first
        title = input_text.strip()
        
        # Remove date/time references from title
        date_patterns = [
            r'\b(today|tomorrow|yesterday|next week|next month)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b'
        ]
        
        for pattern in date_patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remove tags and mentions
        title = re.sub(r'#\w+', '', title)  # Remove hashtags
        title = re.sub(r'@\w+', '', title)  # Remove mentions
        
        # Clean up whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Extract tags
        tags = re.findall(r'#(\w+)', input_text)
        
        # Extract mentions 
        mentions = re.findall(r'@(\w+)', input_text)
        
        # Extract date/time references
        date_patterns = [
            r'\b(today|tomorrow|yesterday|next week|next month)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b'
        ]
        
        parsed_date = None
        for pattern in date_patterns:
            match = re.search(pattern, input_text, re.IGNORECASE)
            if match:
                parsed_date = self.parse_natural_date(match.group(0))
                break
        
        # Determine priority from language and tags
        priority = 'medium'
        if any(tag in ['urgent', 'critical', 'asap'] for tag in tags):
            priority = 'high'
        elif any(tag in ['someday', 'maybe', 'later'] for tag in tags):
            priority = 'low'
        
        # Auto-detect project/area from tags and mentions
        project_id = self._detect_project_from_tags(tags)
        area_id = self._detect_area_from_tags(tags)
        
        # Create task
        task = self.create_task(
            title=title,
            priority=priority,
            project_id=project_id,
            area_id=area_id,
            scheduled_date=parsed_date.strftime("%Y-%m-%d") if parsed_date else None,
            tags=tags
        )
        
        # Link to mentioned people/entities
        for mention in mentions:
            person_entities = self.memory.search(mention, filters={"type": "person"})
            for person in person_entities:
                self.memory.save_relation(MemoryRelation(
                    source_id=task.id,
                    target_id=person['id'],
                    relation_type='involves_person',
                    strength=0.8
                ))
        
        return task
    
    def get_project_timeline(self, project_id: str) -> List[Dict]:
        """Get complete project timeline: tasks + conversations + code + decisions."""
        
        # Get all project-related entities
        project_tasks = self.memory.search_entities("task")
        project_tasks = [task for task in project_tasks if task.metadata.get("project_id") == project_id]
        
        # Get conversations about this project
        project_conversations = self.memory.get_related(project_id, ["discusses", "relates_to"])
        conversations = [c for c in project_conversations if c.get('type') == 'handoff']
        
        # Get code/files related to project
        project_files = self.memory.get_related(project_id, ["implements", "relates_to"])
        files = [f for f in project_files if f.get('type') in ['file', 'function']]
        
        # Get decisions and meetings
        project_decisions = self.memory.search(f"project {project_id}", filters={
            "type": "meeting"
        })
        
        # Combine all timeline events
        timeline_events = []
        
        # Add tasks
        for task in project_tasks:
            timeline_events.append({
                'type': 'task',
                'date': task.created_at.isoformat(),
                'title': task.name,
                'status': task.metadata.get('status'),
                'priority': task.metadata.get('priority'),
                'id': task.id
            })
        
        # Add conversations
        for conv in conversations:
            timeline_events.append({
                'type': 'conversation',
                'date': conv['created_at'],
                'title': f"Discussion: {conv['content'][:50]}...",
                'summary': conv.get('summary'),
                'id': conv['id']
            })
        
        # Add file changes
        for file in files:
            timeline_events.append({
                'type': 'code',
                'date': file['created_at'],
                'title': f"Code: {file['name']}",
                'language': file.get('metadata', {}).get('language'),
                'id': file['id']
            })
        
        # Sort by date
        timeline_events.sort(key=lambda x: x['date'], reverse=True)
        
        return timeline_events
    
    def suggest_task_priorities(self) -> List[Dict]:
        """Get AI-suggested task priorities based on context."""
        suggestions = []
        
        # High priority tasks without scheduling
        high_priority = self.memory.search_entities("task")
        high_priority = [task for task in high_priority 
                        if task.metadata.get("priority") == "high"
                        and task.metadata.get("status") == "todo"
                        and not task.metadata.get("scheduled_date")]
        
        for task in high_priority[:3]:
            suggestions.append({
                "task_id": task.id,
                "title": task.name,
                "reason": "High priority task without scheduling",
                "suggested_action": "Schedule for today or tomorrow"
            })
        
        # Overdue tasks
        overdue = self._get_overdue_tasks()
        for task in overdue[:2]:
            suggestions.append({
                "task_id": task.id,
                "title": task.name,
                "reason": "Task is overdue",
                "suggested_action": "Complete immediately or reschedule"
            })
        
        # Tasks related to recent conversations
        recent_conversations = self.memory.search("", filters={
            "type": "handoff",
            "created_after": (datetime.now() - timedelta(days=3)).isoformat()
        })
        
        if recent_conversations is not None:
            for conv in recent_conversations[:2]:
                suggestions.append({
                    "context_id": conv['id'],
                    "title": f"Follow up on: {conv['content'][:50]}...",
                    "reason": "Recent conversation requires follow-up",
                    "suggested_action": "Create task from conversation"
                })
        
        return suggestions
    
    def quick_find(self, query: str) -> Dict[str, List]:
        """Quick find across tasks, projects, areas with AI search."""
        tasks = self.memory.search(query, {"type": "task"})
        projects = self.memory.search(query, {"type": "project"})
        areas = self.memory.search(query, {"type": "area"})
        
        return {
            "tasks": tasks if tasks is not None else [],
            "projects": projects if projects is not None else [],
            "areas": areas if areas is not None else []
        }

    def register(self, mcp):
        """Register MCP tools for the unified todo system."""
        from .todo_mcp_tools import register_todo_mcp_tools
        register_todo_mcp_tools(mcp, self)
        
        logger.info("Unified Todo MCP tools registered successfully")

    # Helper Methods
    def _get_overdue_tasks(self) -> List[MemoryEntity]:
        """Get tasks that are overdue."""
        today = datetime.now().date()
        overdue_tasks = []
        
        all_tasks = self.memory.search_entities("task")
        all_tasks = [task for task in all_tasks 
                    if task.metadata.get("status") in ["todo", "in_progress"]]
        
        for task in all_tasks:
            due_date = task.metadata.get('due_date')
            if due_date:
                try:
                    task_due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                    if task_due_date < today:
                        overdue_tasks.append(task)
                except ValueError:
                    continue
        
        return overdue_tasks
    
    def _ai_suggest_today_tasks(self) -> List[MemoryEntity]:
        """AI suggests tasks for today based on context and patterns."""
        suggestions = []
        
        # 1. High priority tasks without scheduling
        high_priority = self.memory.search("", filters={
            "type": "task",
            "metadata.priority": "high",
            "metadata.status": "todo",
            "metadata.scheduled_date": None
        })
        if high_priority is not None:
            suggestions.extend(high_priority[:2])
        
        # 2. Tasks related to recent conversations
        recent_conversations = self.memory.search("", filters={
            "type": "handoff",
            "created_after": (datetime.now() - timedelta(days=3)).isoformat()
        })
        
        if recent_conversations is not None:
            for conv in recent_conversations:
                # Find tasks mentioned in or related to recent conversations
                related_tasks = self.memory.get_related(conv['id'], ["relates_to", "spawns_task"])
                if related_tasks is not None:
                    for task in related_tasks:
                        if (task.get('type') == 'task' and 
                            task.get('metadata', {}).get('status') == 'todo'):
                            suggestions.append(task)
        
        # 3. Project deadlines approaching
        urgent_projects = self._get_projects_with_approaching_deadlines()
        for project in urgent_projects:
            project_tasks = self.memory.search("", filters={
                "type": "task",
                "metadata.project_id": project['id'],
                "metadata.status": "todo"
            })
            if project_tasks is not None:
                suggestions.extend(project_tasks[:1])  # One task per urgent project
        
        # 4. Quick wins (low effort, high impact)
        quick_wins = self.memory.search("", filters={
            "type": "task", 
            "metadata.time_estimate": "<30",  # Less than 30 minutes
            "metadata.status": "todo"
        })
        if quick_wins is not None:
            suggestions.extend(quick_wins[:2])
        
        # Deduplicate and limit
        unique_suggestions = {}
        for task in suggestions:
            unique_suggestions[task['id']] = task
        
        return list(unique_suggestions.values())[:8]
    
    def _get_projects_with_approaching_deadlines(self) -> List[Dict]:
        """Get projects with deadlines approaching in the next 3 days."""
        upcoming_deadlines = []
        today = datetime.now().date()
        
        projects = self.memory.search_entities("project")
        projects = [project for project in projects if project.metadata.get("status") == "active"]
        
        for project in projects:
            deadline = project.metadata.get('deadline')
            if deadline:
                try:
                    project_deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
                    days_until_deadline = (project_deadline - today).days
                    if 0 <= days_until_deadline <= 3:
                        upcoming_deadlines.append(project)
                except ValueError:
                    continue
        
        return upcoming_deadlines
    
    def _get_calendar_events(self, date_str: str) -> List[Dict]:
        """Get calendar events for a specific date (placeholder for future integration)."""
        # This would integrate with calendar tool in future phases
        return []
    
    def _suggest_for_date(self, target_date: datetime) -> List[Dict]:
        """Suggest tasks for a specific date based on patterns."""
        # Placeholder for AI date-specific suggestions
        return []
    
    def _calculate_workload_score(self, tasks: List[Dict]) -> float:
        """Calculate workload score for a set of tasks."""
        if not tasks:
            return 0.0
        
        total_estimate = 0
        for task in tasks:
            if isinstance(task, dict):
                time_estimate = task.get('metadata', {}).get('time_estimate', 30)  # Default 30 min
            else:
                # Handle MemoryEntity objects
                time_estimate = task.metadata.get('time_estimate', 30)  # Default 30 min

            total_estimate += time_estimate if time_estimate is not None else 30
        
        # Convert to hours and return score (0-10 scale)
        hours = total_estimate / 60
        return min(hours, 10.0)
    
    def _analyze_conversation_urgency(self, content: str) -> str:
        """Analyze conversation for urgency indicators."""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline']
        high_keywords = ['important', 'priority', 'needed', 'required', 'must']
        
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in urgent_keywords):
            return 'high'
        elif any(keyword in content_lower for keyword in high_keywords):
            return 'medium' 
        else:
            return 'low'
    
    def parse_natural_date(self, input_text: str, context_data: Optional[Dict] = None) -> Optional[datetime]:
        """Enhanced natural language date parsing with context awareness."""
        from dateutil.parser import parse as dateutil_parse
        
        # Standard patterns
        today = datetime.now().date()
        
        # Direct mappings
        direct_mappings = {
            'today': today,
            'tomorrow': today + timedelta(days=1),
            'yesterday': today - timedelta(days=1),
            'next week': today + timedelta(weeks=1),
            'next month': today + timedelta(days=30)
        }
        
        text_lower = input_text.lower().strip()
        
        if text_lower in direct_mappings:
            return datetime.combine(direct_mappings[text_lower], datetime.min.time())
        
        # Weekday patterns
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for i, day in enumerate(weekdays):
            if day in text_lower:
                days_ahead = i - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                return datetime.combine(target_date, datetime.min.time())
        
        # Fallback to dateutil
        try:
            return dateutil_parse(input_text)
        except:
            return None
    
    def _detect_project_from_tags(self, tags: List[str]) -> Optional[str]:
        """Detect project from tags."""
        for tag in tags:
            projects = self.memory.search_entities("project")
            # Filter projects that have the tag in their name, content, or tags
            matching_projects = [p for p in projects 
                               if tag.lower() in p.name.lower() 
                               or (p.content and tag.lower() in p.content.lower())
                               or any(tag.lower() in t.lower() for t in p.tags)]
            if matching_projects:
                return matching_projects[0].id
        return None
    
    def _detect_area_from_tags(self, tags: List[str]) -> Optional[str]:
        """Detect area from tags."""
        for tag in tags:
            areas = self.memory.search_entities("area")
            # Filter areas that have the tag in their name, content, or tags
            matching_areas = [a for a in areas 
                            if tag.lower() in a.name.lower() 
                            or (a.content and tag.lower() in a.content.lower())
                            or any(tag.lower() in t.lower() for t in a.tags)]
            if matching_areas:
                return matching_areas[0].id
        return None 