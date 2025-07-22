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



try:
    from ..core import UnifiedMemoryStore
    from ..core.models import MemoryEntity, MemoryRelation
    from ..tools.todo.unified_todo_tool import UnifiedTodoTool
except ImportError:
    from core import UnifiedMemoryStore
    from core.models import MemoryEntity, MemoryRelation
    from tools.todo.unified_todo_tool import UnifiedTodoTool
logger = logging.getLogger(__name__)


class Event(BaseModel):
    """Event model for workflow triggers."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    payload: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    source: str = "system"  # "system", "mcp", "external"


class WorkflowAction(BaseModel):
    """Individual action within a workflow."""
    type: str  # "create_task", "update_entity", "save_relation", "notify", "run_shell", "http_request"
    params: Dict[str, Any]
    condition: Optional[str] = None  # Optional condition expression


class WorkflowTrigger(BaseModel):
    """Trigger definition for a workflow."""
    # Entity-based trigger fields (replaces the old type + filter structure)
    type: Optional[str] = None  # Entity type (e.g., "handoff", "task", "note")
    content: Optional[str] = None  # Content filter
    name: Optional[str] = None  # Name filter  
    tags: Optional[List[str]] = None  # Tag filters
    metadata: Optional[Dict[str, Any]] = None  # Metadata filters
    
    # Legacy support and special triggers
    event_type: Optional[str] = None  # For backward compatibility: "entity_created", "entity_updated", etc.
    schedule: Optional[str] = None  # Cron-like schedule for scheduled triggers


class Workflow(BaseModel):
    """Workflow definition."""
    id: str
    name: str
    description: str
    trigger: WorkflowTrigger
    actions: List[WorkflowAction]
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class WorkflowRun(BaseModel):
    """Record of a workflow execution."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    event_id: str
    status: str  # "running", "completed", "failed", "rolled_back"
    started_at: datetime = Field(default_factory=lambda: datetime.now())
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
        self.background_tasks = set()


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
        workflow.updated_at = datetime.now()
        
        # Save to memory store first to ensure persistence
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
        
        try:
            # Save to database first
            self.memory.save_entity(workflow_entity)
            
            # Only add to in-memory dictionary after successful database save
            self.workflows[workflow.id] = workflow
            logger.info(f"Registered workflow: {workflow.name} ({workflow.id})")
            
        except Exception as e:
            logger.error(f"Failed to save workflow {workflow.id} to database: {e}")
            # Don't add to in-memory dictionary if database save failed
            raise RuntimeError(f"Failed to register workflow {workflow.id}: {e}")

    def trigger_event(self, event: Event) -> None:
        """Trigger an event and execute matching workflows."""
        import asyncio
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in an async context, create a task
            asyncio.create_task(self._process_event(event))
        except RuntimeError:
            # No event loop running, create a new one for this operation
            try:
                asyncio.run(self._process_event(event))
            except Exception as e:
                logger.error(f"Failed to process event {event.id}: {e}")

    async def _process_event(self, event: Event) -> None:
        """Process an event and execute matching workflows."""
        logger.info(f"Processing event: {event.payload} ({event.id})")
        
        matching_workflows = self._find_matching_workflows(event)
        logger.info(f"Found {len(matching_workflows)} matching workflows")
        
        for workflow in matching_workflows:
            logger.info(f"Checking workflow {workflow.id}: enabled={workflow.enabled}, running={workflow.id in self.running_workflows}")
            if workflow.enabled and workflow.id not in self.running_workflows:
                logger.info(f"Starting workflow: {workflow.name} ({workflow.id})")
                # task = asyncio.create_task(self._run_workflow(workflow, event))
                # self.background_tasks.add(task)
                # task.add_done_callback(background_tasks.discard)

                await self._run_workflow(workflow, event)
            else:
                if not workflow.enabled:
                    logger.info(f"Skipping disabled workflow: {workflow.id}")
                if workflow.id in self.running_workflows:
                    logger.info(f"Skipping already running workflow: {workflow.id}")

    def _find_matching_workflows(self, event: Event) -> List[Workflow]:
        """Find workflows that match the given event."""
        matching = []
        
        logger.info(f"Checking {len(self.workflows)} workflows for event payload: {event.payload}")
        for workflow in self.workflows.values():
            logger.info(f"Checking workflow {workflow.id} against event")
            
            # For entity-based events, check if any entity in the payload matches the trigger
            entities_to_check = event.payload
            
            # Extract entities from event payload
            # if 'entity' in event.payload:
            #     entities_to_check.append(event.payload['entity'])
            # if 'entities' in event.payload:
            #     entities_to_check.extend(event.payload['entities'])
            # if 'context' in event.payload:
            #     entities_to_check.append(event.payload['context'])
            # if 'relation' in event.payload:
            #     entities_to_check.append(event.payload['relation'])
            
            # If no entities in payload and no legacy event_type, skip
            if not entities_to_check and not workflow.trigger.event_type:
                logger.info(f"No entities to check for workflow {workflow.id}")
                continue
            
            # Check if any entity matches the trigger
            entity_matches = False
            for entity_data in entities_to_check:
                if self._entity_matches_trigger(entity_data, workflow.trigger):
                    logger.info(f"Entity matches trigger for workflow {workflow.id}")
                    entity_matches = True
                    break
   
            if entity_matches:
                matching.append(workflow)
            else:
                logger.info(f"No match for workflow {workflow.id}")
        
        logger.info(f"Found {len(matching)} matching workflows")
        return matching

    def _entity_matches_trigger(self, entity_data: Dict[str, Any], trigger: WorkflowTrigger) -> bool:
        """Check if an entity data matches the trigger."""
        logger.info(f"Checking entity data: {entity_data} against trigger: {trigger}")
        if not isinstance(entity_data, dict):
            return False
            
        # If no conditions specified, don't match (avoid matching everything)
        has_conditions = (trigger.type or trigger.content or trigger.name or 
                         trigger.tags or trigger.metadata)
        if not has_conditions:
            return False
        
        # Check entity type
        if trigger.type and entity_data.get("type") != trigger.type:
            logger.info(f"Entity type mismatch: expected {trigger.type}, got {entity_data.get('type')}")
            return False
            
        # Check content (exact match or substring), normalize to lowercase
        if trigger.content:
            entity_content = entity_data.get("content", "").lower()
            if trigger.content not in entity_content:
                logger.info(f"Content mismatch: '{trigger.content}' not in '{entity_content}'")
                return False

        # Check name (exact match or substring), normalize to lowercase
        if trigger.name:
            entity_name = entity_data.get("name", "").lower()
            if trigger.name not in entity_name:
                logger.info(f"Name mismatch: '{trigger.name}' not in '{entity_name}'")
                return False

        # Check tags (any tag in trigger.tags must be in entity.tags), normalize to lowercase
        if trigger.tags:
            entity_tags = entity_data.get("tags", []).lower()
            if not isinstance(entity_tags, list):
                entity_tags = []
            if not any(tag.lower() in entity_tags for tag in trigger.tags):
                logger.info(f"Tag mismatch: none of {trigger.tags} found in {entity_tags}")
                return False
                
        # Check metadata
        if trigger.metadata:
            entity_metadata = entity_data.get("metadata", {})
            if not isinstance(entity_metadata, dict):
                entity_metadata = {}
            for key, expected_value in trigger.metadata.items():
                actual_value = entity_metadata.get(key)
                if actual_value != expected_value:
                    logger.info(f"Metadata mismatch: {key} expected {expected_value}, got {actual_value}")
                    return False
                    
        logger.info(f"Entity matches all trigger conditions")
        return True

    def _matches_filter(self, event: Event, filter_dict: Optional[Dict[str, Any]]) -> bool:
        """Check if an event matches the given filter."""
        if not filter_dict:
            logger.info("No filter specified, matches by default")
            return True
        
        payload = event.payload
        logger.info(f"Checking filter {filter_dict} against payload: {payload}")
        
        for key, expected_value in filter_dict.items():
            logger.info(f"Checking filter key: {key} = {expected_value}")
            
            for key, value in payload.items():
                logger.info( f"Checking payload key: {key} = {value}")
                if key == key:
                    logger.info(f"Found matching key: {key}")
                    if value == expected_value:
                        logger.info(f"Found matching value: {value} for key {key}")
                        return True
                else:
                    logger.info(f"Key {key} not found in payload")
                    return False

            if key not in payload:
                logger.info(f"Key {key} not directly in payload")
                
                # Handle nested keys (e.g., "entity.type")
                if "." in key:
                    logger.info(f"Handling nested key: {key}")
                    keys = key.split(".")
                    logger.info(f"Handling nested keys: {keys}")
                    current = payload
                    try:
                        for k in keys[:-1]:
                            logger.info(f"Navigating to key: {k}")
                            current = current[k]
                            logger.info(f"Current value: {current}")
                        actual_value = current[keys[-1]]
                        logger.info(f"Found nested value: {actual_value} for key {keys[-1]}")
                    except (KeyError, TypeError) as e:
                        logger.info(f"Failed to navigate nested keys: {e}")
                        return False
                else:
                    logger.info(f"Key {key} not found in payload")
                    return False
            else:
                actual_value = payload[key]
                logger.info(f"Found direct value: {actual_value}")
            
            # Handle list values (e.g., topics: ["pull request"])
            if isinstance(expected_value, list):
                logger.info(f"Expected value is list: {expected_value}")
                if not isinstance(actual_value, list):
                    logger.info(f"Actual value is not a list: {actual_value}")
                    return False
                if not any(item in actual_value for item in expected_value):
                    logger.info(f"No matching items found in lists")
                    return False
            else:
                logger.info(f"Comparing actual '{actual_value}' with expected '{expected_value}'")
                if actual_value != expected_value:
                    logger.info(f"Values don't match: {actual_value} != {expected_value}")
                    return False
                else:
                    logger.info(f"Values match!")
        
        logger.info("All filter conditions matched")
        return True

    async def _run_workflow(self, workflow: Workflow, event: Event) -> None:
        """Execute a workflow with the given event context."""
        logger.info(f"Running workflow: {workflow.id}")
        logger.info(f"Event: {event.payload}")
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
                "entities": event.payload,
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
            workflow_run.completed_at = datetime.now()
            workflow_run.logs.append("Workflow execution completed successfully")
            
        except Exception as e:
            workflow_run.status = "failed"
            workflow_run.completed_at = datetime.now()
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
        
        logger.info(f"Executing action: {action.type}")
        logger.info(f"Action params: {action.params}")
        logger.info(f"Context: {context}")
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
        todo_tool = UnifiedTodoTool(self.memory)
        title = self._resolve_template(params.get("title", ""), context)
        content = self._resolve_template(params.get("content", ""), context)
        priority = params.get("priority", "medium")
        
        task = todo_tool.create_task(title=title, description=content, priority=priority)
        logger.info(f"Created task: {task}")

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
            workflow.updated_at = datetime.now()
            # Update in memory store
            return True
        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a workflow."""
        workflow = self.workflows.get(workflow_id)
        if workflow:
            workflow.enabled = True
            workflow.updated_at = datetime.now()
            # Update in memory store
            return True
        return False 