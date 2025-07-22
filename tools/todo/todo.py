"""
TODO List tool for Emily Tools MCP server.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseTool
import json

logger = logging.getLogger(__name__)


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.TODO
    due_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    completed_at: Optional[datetime] = None
    tags: List[str] = []


class TodoTool(BaseTool):
    """TODO list management tool using JSONL."""
    
    @property
    def name(self) -> str:
        return "todo"
    
    @property
    def description(self) -> str:
        return "Manage TODO tasks with priorities, due dates, and status tracking"
    
    def get_capabilities(self) -> List[str]:
        return [
            "create_task",
            "list_tasks", 
            "update_task",
            "delete_task",
            "mark_complete",
            "search_tasks",
            "get_statistics"
        ]

    def _read_tasks(self) -> List[Task]:
        if not self.data_file.exists():
            return []
        tasks = []
        with open(self.data_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tasks.append(Task(**json.loads(line)))
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
        return tasks

    def _write_tasks(self, tasks: List[Task]):
        with open(self.data_file, 'w') as f:
            for task in tasks:
                f.write(task.model_dump_json() + '\n')

    def create_task(self, title: str, description: Optional[str] = None, 
                   priority: Priority = Priority.MEDIUM, due_date: Optional[str] = None,
                   tags: List[str] = []) -> Task:
        """Create a new task and append to JSONL."""
        tasks = self._read_tasks()
        new_id = max([t.id for t in tasks if t.id is not None] + [0]) + 1
        task = Task(
            id=new_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(task.model_dump_json() + '\n')
        return task

    def list_tasks(self, status: Optional[Status] = None, 
                  priority: Optional[Priority] = None) -> List[Task]:
        tasks = self._read_tasks()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        return tasks

    def update_task(self, task_id: int, **kwargs) -> Optional[Task]:
        tasks = self._read_tasks()
        updated = None
        for t in tasks:
            if t.id == task_id:
                for k, v in kwargs.items():
                    setattr(t, k, v)
                updated = t
        self._write_tasks(tasks)
        return updated

    def get_task(self, task_id: int) -> Optional[Task]:
        tasks = self._read_tasks()
        for t in tasks:
            if t.id == task_id:
                return t
        return None

    def mark_complete(self, task_id: int) -> Optional[Task]:
        return self.update_task(task_id, status=Status.DONE, completed_at=datetime.now())

    def delete_task(self, task_id: int) -> bool:
        tasks = self._read_tasks()
        new_tasks = [t for t in tasks if t.id != task_id]
        self._write_tasks(new_tasks)
        return len(new_tasks) < len(tasks)

    def search_tasks(self, query: str) -> List[Task]:
        tasks = self._read_tasks()
        return [t for t in tasks if query.lower() in t.title.lower() or (t.description and query.lower() in t.description.lower())]

    def get_statistics(self) -> Dict[str, Any]:
        tasks = self._read_tasks()
        return {
            'total': len(tasks),
            'by_status': {s.value: len([t for t in tasks if t.status == s]) for s in Status},
            'by_priority': {p.value: len([t for t in tasks if t.priority == p]) for p in Priority},
        } 

    def register(self, mcp):
        @mcp.tool()
        async def todo_create(title: str, description: str = None, priority: str = "medium", 
                             due_date: str = None, tags: list = None) -> dict:
            """Create a new TODO task."""
            if tags is None:
                tags = []
            priority_enum = Priority(priority.lower())
            task = self.create_task(
                title=title,
                description=description,
                priority=priority_enum,
                due_date=due_date,
                tags=tags
            )
            return {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "status": task.status.value,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags
            }

        @mcp.tool()
        async def todo_list(status: str = None, priority: str = None) -> list:
            """List TODO tasks with optional filtering."""
            status_enum = Status(status.lower()) if status else None
            priority_enum = Priority(priority.lower()) if priority else None
            tasks = self.list_tasks(status=status_enum, priority=priority_enum)
            return [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "tags": task.tags,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]

        @mcp.tool()
        async def todo_complete(task_id: int) -> dict:
            """Mark a TODO task as complete."""
            task = self.mark_complete(task_id)
            if task:
                return {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status.value,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
            return {"error": "Task not found"}

        @mcp.resource("resource://todo/all")
        def resource_todo_all() -> list:
            """Return all TODO tasks as a list of dicts."""
            return [task.model_dump(mode='json') for task in self.list_tasks()]

        @mcp.resource("resource://todo/{task_id}")
        def resource_todo_by_id(task_id: int) -> dict:
            """Return a single TODO task by ID as a dict."""
            task = self.get_task(task_id)
            return task.model_dump(mode='json') if task else {}
        
        logger.info("Todo MCP tools registered successfully")