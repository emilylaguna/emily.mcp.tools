"""
Smart Workflows & Automation Engine

Provides rule- and AI-driven automation for the unified memory system.
Handles event processing, workflow execution, and async task management.
"""

import asyncio
import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from pydantic import BaseModel, Field

from core import UnifiedMemoryStore
from models import MemoryEntity, MemoryRelation

logger = logging.getLogger(__name__)


class Event(BaseModel):
    """Event model for workflow triggers."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str  # "entity_created", "task_completed", "calendar_event", etc.
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))
    source: str = "system"  # "system", "mcp", "external"


class WorkflowAction(BaseModel):
    """Individual action within a workflow."""
    type: str  # "create_task", "update_entity", "save_relation", "notify", "run_shell", "http_request"
    params: Dict[str, Any]
    condition: Optional[str] = None  # Optional condition expression


class WorkflowTrigger(BaseModel):
    """Trigger definition for a workflow."""
    type: str  # "entity_created", "entity_updated", "relation_created", "scheduled", "manual"
    filter: Optional[Dict[str, Any]] = None  # Filter conditions
    schedule: Optional[str] = None  # Cron-like schedule for scheduled triggers


class Workflow(BaseModel):
    """Workflow definition."""
    id: str
    name: str
    description: str
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))


class WorkflowRun(BaseModel):
    """Record of a workflow execution."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    event_id: str
    status: str  # "running", "completed", "failed", "rolled_back"
    started_at: datetime = Field(default_factory=lambda: datetime.now(datetime.UTC))
    completed_at: Optional[datetime] = None
    logs: List[str] = []
    error: Optional[str] = None
    context: Dict[str, Any] = {}


class WorkflowEngine:
    """Rule- & AI-driven automation engine for unified memory."""

    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.workflows: Dict[str, Workflow] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running_workflows: Set[str] = set()
        self._load_workflows()

    def _load_workflows(self) -> None:
        """Load workflows from the memory store."""
        try:
            workflow_entities = self.memory.search_entities(
                entity_type="workflow",
                limit=100
            )
            
            for entity in workflow_entities:
                try:
                    workflow_data = json.loads(entity.content)
                    workflow = Workflow(**workflow_data)
                    self.workflows[workflow.id] = workflow
                    logger.info(f"Loaded workflow: {workflow.name} ({workflow.id})")
                except Exception as e:
                    logger.error(f"Failed to load workflow {entity.id}: {e}")
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")

    def register_workflow(self, workflow: Workflow) -> None:
        """Register a new workflow."""
        workflow.updated_at = datetime.now(datetime.UTC)
        self.workflows[workflow.id] = workflow
        
        # Save to memory store
        workflow_entity = MemoryEntity(
            type="workflow",
            name=workflow.name,
            content=workflow.model_dump_json(),
            metadata={
                "workflow_id": workflow.id,
                "enabled": workflow.enabled,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat()
            }
        )
        self.memory.save_entity(workflow_entity)
        logger.info(f"Registered workflow: {workflow.name} ({workflow.id})")

    def trigger_event(self, event: Event) -> None:
        """Trigger an event and execute matching workflows."""
        asyncio.create_task(self._process_event(event))

    async def _process_event(self, event: Event) -> None:
        """Process an event and execute matching workflows."""
        logger.info(f"Processing event: {event.type} ({event.id})")
        
        matching_workflows = self._find_matching_workflows(event)
        
        for workflow in matching_workflows:
            if workflow.enabled and workflow.id not in self.running_workflows:
                asyncio.create_task(self._run_workflow(workflow, event))

    def _find_matching_workflows(self, event: Event) -> List[Workflow]:
        """Find workflows that match the given event."""
        matching = []
        
        for workflow in self.workflows.values():
            if workflow.trigger.type == event.type:
                if self._matches_filter(event, workflow.trigger.filter):
                    matching.append(workflow)
        
        return matching

    def _matches_filter(self, event: Event, filter_dict: Optional[Dict[str, Any]]) -> bool:
        """Check if an event matches the given filter."""
        if not filter_dict:
            return True
        
        payload = event.payload
        
        for key, expected_value in filter_dict.items():
            if key not in payload:
                return False
            
            actual_value = payload[key]
            
            # Handle nested keys (e.g., "metadata.topics")
            if "." in key:
                keys = key.split(".")
                current = payload
                try:
                    for k in keys[:-1]:
                        current = current[k]
                    actual_value = current[keys[-1]]
                except (KeyError, TypeError):
                    return False
            
            # Handle list values (e.g., topics: ["pull request"])
            if isinstance(expected_value, list):
                if not isinstance(actual_value, list):
                    return False
                if not any(item in actual_value for item in expected_value):
                    return False
            else:
                if actual_value != expected_value:
                    return False
        
        return True

    async def _run_workflow(self, workflow: Workflow, event: Event) -> None:
        """Execute a workflow with the given event context."""
        workflow_run = WorkflowRun(
            workflow_id=workflow.id,
            event_id=event.id,
            status="running"
        )
        
        self.running_workflows.add(workflow.id)
        
        try:
            # Create context with event and workflow data
            context = {
                "event": event.model_dump(),
                "workflow": workflow.model_dump(),
                "entity": event.payload.get("entity"),
                "relation": event.payload.get("relation"),
                "timestamp": event.timestamp.isoformat()
            }
            
            workflow_run.logs.append(f"Starting workflow execution for event {event.id}")
            
            # Execute actions in sequence
            for i, action in enumerate(workflow.actions):
                try:
                    workflow_run.logs.append(f"Executing action {i+1}: {action.type}")
                    await self._execute_action(action, context)
                    workflow_run.logs.append(f"Action {i+1} completed successfully")
                except Exception as e:
                    workflow_run.logs.append(f"Action {i+1} failed: {str(e)}")
                    raise
            
            workflow_run.status = "completed"
            workflow_run.completed_at = datetime.now(datetime.UTC)
            workflow_run.logs.append("Workflow execution completed successfully")
            
        except Exception as e:
            workflow_run.status = "failed"
            workflow_run.completed_at = datetime.now(datetime.UTC)
            workflow_run.error = str(e)
            workflow_run.logs.append(f"Workflow execution failed: {str(e)}")
            logger.error(f"Workflow {workflow.id} failed: {e}")
        
        finally:
            self.running_workflows.discard(workflow.id)
            self._save_workflow_run(workflow_run)

    async def _execute_action(self, action: WorkflowAction, context: Dict[str, Any]) -> None:
        """Execute a single workflow action."""
        # Check condition if present
        if action.condition:
            if not self._evaluate_condition(action.condition, context):
                logger.info(f"Skipping action {action.type} due to condition")
                return
        
        # Execute based on action type
        if action.type == "create_task":
            await self._action_create_task(action.params, context)
        elif action.type == "update_entity":
            await self._action_update_entity(action.params, context)
        elif action.type == "save_relation":
            await self._action_save_relation(action.params, context)
        elif action.type == "notify":
            await self._action_notify(action.params, context)
        elif action.type == "run_shell":
            await self._action_run_shell(action.params, context)
        elif action.type == "http_request":
            await self._action_http_request(action.params, context)
        else:
            raise ValueError(f"Unknown action type: {action.type}")

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        # Simple condition evaluation - can be extended with a proper expression parser
        try:
            # Replace template variables
            for key, value in context.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        condition = condition.replace(f"{{{{ {key}.{subkey} }}}}", str(subvalue))
                else:
                    condition = condition.replace(f"{{{{ {key} }}}}", str(value))
            
            # Simple boolean evaluation (be careful with this in production)
            return eval(condition, {"__builtins__": {}}, {})
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return False

    async def _action_create_task(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Create a new task entity."""
        title = self._resolve_template(params.get("title", ""), context)
        content = self._resolve_template(params.get("content", ""), context)
        priority = params.get("priority", "medium")
        
        task = MemoryEntity(
            type="task",
            name=title,
            content=content,
            metadata={
                "priority": priority,
                "status": "pending",
                "created_by_workflow": context["workflow"]["id"],
                "triggered_by_event": context["event"]["id"]
            }
        )
        
        self.memory.save_entity(task)
        logger.info(f"Created task: {title}")

    async def _action_update_entity(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Update an existing entity."""
        entity_id = self._resolve_template(params.get("entity_id", ""), context)
        updates = params.get("updates", {})
        
        # Resolve template variables in updates
        resolved_updates = {}
        for key, value in updates.items():
            if isinstance(value, str):
                resolved_updates[key] = self._resolve_template(value, context)
            else:
                resolved_updates[key] = value
        
        # Get entity and update
        entity = self.memory.get_entity(entity_id)
        if entity:
            for key, value in resolved_updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
                elif key in entity.metadata:
                    entity.metadata[key] = value
            
            self.memory.save_entity(entity)
            logger.info(f"Updated entity: {entity_id}")

    async def _action_save_relation(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Save a new relation between entities."""
        source_id = self._resolve_template(params.get("source_id", ""), context)
        target_id = self._resolve_template(params.get("target_id", ""), context)
        relation_type = params.get("relation_type", "related")
        
        relation = MemoryRelation(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type
        )
        
        self.memory.save_relation(relation)
        logger.info(f"Created relation: {source_id} -> {target_id} ({relation_type})")

    async def _action_notify(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Send a notification."""
        channel = params.get("channel", "console")
        message = self._resolve_template(params.get("message", ""), context)
        
        if channel == "console":
            logger.info(f"NOTIFICATION: {message}")
        elif channel == "slack":
            # Placeholder for Slack integration
            logger.info(f"SLACK NOTIFICATION: {message}")
        elif channel == "email":
            # Placeholder for email integration
            logger.info(f"EMAIL NOTIFICATION: {message}")
        else:
            logger.warning(f"Unknown notification channel: {channel}")

    async def _action_run_shell(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Run a shell command."""
        command = self._resolve_template(params.get("command", ""), context)
        
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor,
                lambda: asyncio.run(self._run_shell_command(command))
            )
            logger.info(f"Shell command executed: {command}")
        except Exception as e:
            logger.error(f"Shell command failed: {command} - {e}")
            raise

    async def _action_http_request(self, params: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Make an HTTP request."""
        # Placeholder for HTTP request implementation
        url = self._resolve_template(params.get("url", ""), context)
        method = params.get("method", "GET")
        
        logger.info(f"HTTP {method} request to: {url}")
        # TODO: Implement actual HTTP request logic

    def _resolve_template(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template variables in a string."""
        result = template
        
        # Replace simple {{ variable }} patterns
        for key, value in context.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    result = result.replace(f"{{{{ {key}.{subkey} }}}}", str(subvalue))
            else:
                result = result.replace(f"{{{{ {key} }}}}", str(value))
        
        return result

    async def _run_shell_command(self, command: str) -> None:
        """Run a shell command (placeholder implementation)."""
        # This would be implemented with actual subprocess calls
        logger.info(f"Would execute shell command: {command}")

    def _save_workflow_run(self, workflow_run: WorkflowRun) -> None:
        """Save workflow run record to memory store."""
        try:
            run_entity = MemoryEntity(
                type="workflow_run",
                name=f"Workflow Run {workflow_run.id}",
                content=workflow_run.model_dump_json(),
                metadata={
                    "workflow_id": workflow_run.workflow_id,
                    "event_id": workflow_run.event_id,
                    "status": workflow_run.status,
                    "started_at": workflow_run.started_at.isoformat(),
                    "completed_at": workflow_run.completed_at.isoformat() if workflow_run.completed_at else None
                }
            )
            self.memory.save_entity(run_entity)
        except Exception as e:
            logger.error(f"Failed to save workflow run: {e}")

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        return list(self.workflows.values())

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            # TODO: Remove from memory store
            return True
        return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow."""
        workflow = self.workflows.get(workflow_id)
        if workflow:
            workflow.enabled = False
            workflow.updated_at = datetime.now(datetime.UTC)
            # Update in memory store
            return True
        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a workflow."""
        workflow = self.workflows.get(workflow_id)
        if workflow:
            workflow.enabled = True
            workflow.updated_at = datetime.now(datetime.UTC)
            # Update in memory store
            return True
        return False 