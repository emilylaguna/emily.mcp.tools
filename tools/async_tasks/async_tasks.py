"""
Async Tasks tool for Emily Tools MCP server.
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseTool
import json


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AsyncTask(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    command: str
    arguments: Dict[str, Any] = {}
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = datetime.now()
    tags: List[str] = []


class AsyncTasksTool(BaseTool):
    """Background task management tool using JSONL."""
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self._running_tasks: Dict[int, asyncio.Task] = {}
        self._task_queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
    
    @property
    def name(self) -> str:
        return "async_tasks"
    
    @property
    def description(self) -> str:
        return "Schedule and manage background tasks and future task execution"
    
    def get_capabilities(self) -> List[str]:
        return [
            "create_task",
            "schedule_task",
            "list_tasks",
            "get_task",
            "cancel_task",
            "get_task_status",
            "get_running_tasks",
            "get_task_history"
        ]
    
    def _read_tasks(self) -> List[AsyncTask]:
        if not self.data_file.exists():
            return []
        with open(self.data_file, 'r') as f:
            return [AsyncTask(**json.loads(line)) for line in f if line.strip()]

    def _write_tasks(self, tasks: List[AsyncTask]):
        with open(self.data_file, 'w') as f:
            for task in tasks:
                f.write(task.json() + '\n')

    def create_task(self, name: str, command: str, arguments: Dict[str, Any] = {},
                   description: Optional[str] = None, priority: TaskPriority = TaskPriority.NORMAL,
                   tags: List[str] = []) -> AsyncTask:
        tasks = self._read_tasks()
        new_id = max([t.id for t in tasks if t.id is not None] + [0]) + 1
        task = AsyncTask(
            id=new_id,
            name=name,
            description=description,
            command=command,
            arguments=arguments,
            priority=priority,
            tags=tags,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(task.json() + '\n')
        return task

    def schedule_task(self, name: str, command: str, scheduled_at: datetime,
                     arguments: Dict[str, Any] = {}, description: Optional[str] = None,
                     priority: TaskPriority = TaskPriority.NORMAL, tags: List[str] = []) -> AsyncTask:
        tasks = self._read_tasks()
        new_id = max([t.id for t in tasks if t.id is not None] + [0]) + 1
        task = AsyncTask(
            id=new_id,
            name=name,
            description=description,
            command=command,
            arguments=arguments,
            priority=priority,
            scheduled_at=scheduled_at,
            tags=tags,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(task.json() + '\n')
        return task

    def list_tasks(self, status: Optional[TaskStatus] = None,
                  priority: Optional[TaskPriority] = None, limit: int = 50) -> List[AsyncTask]:
        tasks = self._read_tasks()
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        return tasks[:limit]

    def get_task(self, task_id: int) -> Optional[AsyncTask]:
        tasks = self._read_tasks()
        for t in tasks:
            if t.id == task_id:
                return t
        return None

    def cancel_task(self, task_id: int) -> bool:
        tasks = self._read_tasks()
        updated = False
        for t in tasks:
            if t.id == task_id:
                t.status = TaskStatus.CANCELLED
                updated = True
        self._write_tasks(tasks)
        return updated

    def get_task_status(self, task_id: int) -> Optional[Dict[str, Any]]:
        task = self.get_task(task_id)
        if task:
            return task.dict()
        return None

    def get_running_tasks(self) -> List[Dict[str, Any]]:
        tasks = self._read_tasks()
        return [t.dict() for t in tasks if t.status == TaskStatus.RUNNING]

    def get_task_history(self, days: int = 7) -> List[AsyncTask]:
        tasks = self._read_tasks()
        cutoff = datetime.now() - timedelta(days=days)
        return [t for t in tasks if t.created_at and datetime.fromisoformat(str(t.created_at)) >= cutoff]
    
    async def _worker(self):
        """Background worker that processes the task queue."""
        while True:
            try:
                # Get next task from queue
                task_id = await self._task_queue.get()
                
                # Check if task should be executed now
                task = self.get_task(task_id)
                if not task:
                    continue
                
                if task.scheduled_at and task.scheduled_at > datetime.now():
                    # Task is scheduled for future, put it back in queue
                    await asyncio.sleep(60)  # Check again in 1 minute
                    await self._task_queue.put(task_id)
                    continue
                
                # Execute the task
                asyncio_task = asyncio.create_task(self._execute_task(task_id))
                self._running_tasks[task_id] = asyncio_task
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in async task worker: {e}")
    
    async def _execute_task(self, task_id: int):
        """Execute a specific task."""
        # Update status to running
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE async_tasks SET status = ?, started_at = ? WHERE id = ?
        """, (TaskStatus.RUNNING.value, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        try:
            # Get task details
            task = self.get_task(task_id)
            if not task:
                return
            
            # Execute the command (simplified - in real implementation, you'd have command handlers)
            result = await self._run_command(task.command, task.arguments)
            
            # Update status to completed
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE async_tasks SET status = ?, completed_at = ?, result = ? WHERE id = ?
            """, (TaskStatus.COMPLETED.value, datetime.now().isoformat(), str(result), task_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            # Update status to failed
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE async_tasks SET status = ?, completed_at = ?, error = ? WHERE id = ?
            """, (TaskStatus.FAILED.value, datetime.now().isoformat(), str(e), task_id))
            
            conn.commit()
            conn.close()
        
        finally:
            # Remove from running tasks
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
    
    async def _run_command(self, command: str, arguments: Dict[str, Any]) -> str:
        """Run a command (placeholder implementation)."""
        # This is a simplified implementation
        # In a real system, you'd have proper command handlers
        
        if command == "sleep":
            duration = arguments.get("duration", 1)
            await asyncio.sleep(duration)
            return f"Slept for {duration} seconds"
        
        elif command == "echo":
            message = arguments.get("message", "Hello World")
            return f"Echo: {message}"
        
        elif command == "calculate":
            operation = arguments.get("operation", "add")
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                result = a / b if b != 0 else "Error: Division by zero"
            else:
                result = "Error: Unknown operation"
            
            return f"Result: {result}"
        
        else:
            return f"Unknown command: {command}"
    
    def _row_to_task(self, row) -> AsyncTask:
        """Convert database row to AsyncTask object."""
        return AsyncTask(
            id=row[0],
            name=row[1],
            description=row[2],
            command=row[3],
            arguments=eval(row[4]) if row[4] else {},
            status=TaskStatus(row[5]),
            priority=TaskPriority(row[6]),
            scheduled_at=datetime.fromisoformat(row[7]) if row[7] else None,
            started_at=datetime.fromisoformat(row[8]) if row[8] else None,
            completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
            result=row[10],
            error=row[11],
            created_at=datetime.fromisoformat(row[12]),
            tags=row[13].split(',') if row[13] else []
        ) 

    def register(self, mcp):
        @mcp.tool()
        async def async_tasks_create(name: str, command: str, arguments: dict = None,
                                    description: str = None, priority: str = "normal", 
                                    tags: list = None, ctx: object = None) -> dict:
            """Create a new async task."""
            if arguments is None:
                arguments = {}
            if tags is None:
                tags = []
            priority_enum = TaskPriority(priority.lower())
            task = self.create_task(
                name=name,
                command=command,
                arguments=arguments,
                description=description,
                priority=priority_enum,
                tags=tags
            )
            return {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "command": task.command,
                "arguments": task.arguments,
                "status": task.status.value,
                "priority": task.priority.value,
                "tags": task.tags
            }

        @mcp.tool()
        async def async_tasks_list(status: str = None, priority: str = None, limit: int = 50, ctx: object = None) -> list:
            """List async tasks with optional filtering."""
            status_enum = TaskStatus(status.lower()) if status else None
            priority_enum = TaskPriority(priority.lower()) if priority else None
            tasks = self.list_tasks(status=status_enum, priority=priority_enum, limit=limit)
            return [
                {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "command": task.command,
                    "arguments": task.arguments,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "result": task.result,
                    "error": task.error,
                    "tags": task.tags
                }
                for task in tasks
            ]

        @mcp.tool()
        async def async_tasks_get_status(task_id: int, ctx: object = None) -> dict:
            """Get detailed status of an async task."""
            status_info = self.get_task_status(task_id)
            if status_info:
                return status_info
            return {"error": "Task not found"} 