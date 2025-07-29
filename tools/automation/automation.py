"""
Automation tool for Emily Tools MCP server.
Provides workflow management and automation capabilities.
"""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Literal
from enum import Enum

from pydantic import BaseModel

from emily_core import UnifiedMemoryStore, MemoryEntity, MemoryContext

from emily_common import BaseTool
from ..common_types import Status, TriggerType, ActionType
try:
    from ...workflows.engine import WorkflowEngine, Workflow, WorkflowAction, WorkflowTrigger, Event
    from ...workflows.suggester import WorkflowSuggester
except ImportError:
    from workflows.engine import WorkflowEngine, Workflow, WorkflowAction, WorkflowTrigger, Event
    from workflows.suggester import WorkflowSuggester

logger = logging.getLogger(__name__)


# Use common types where possible
WorkflowStatus = Status
WorkflowTriggerType = TriggerType
WorkflowActionType = ActionType


class WorkflowRunStatus(str, Enum):
    """Workflow run status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowDefinition(BaseModel):
    """Workflow definition for MCP clients."""
    id: str
    name: str
    description: str
    trigger: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowRunInfo(BaseModel):
    """Workflow run information for MCP clients."""
    id: str
    workflow_id: str
    event_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    logs: List[str] = []
    error: Optional[str] = None


class WorkflowSuggestion(BaseModel):
    """Workflow suggestion for MCP clients."""
    id: str
    name: str
    description: str
    confidence: float
    reasoning: str
    category: str
    estimated_impact: str
    workflow_yaml: str


class AutomationTool(BaseTool):
    """Tool for managing workflows and automation in the unified memory system."""

    def __init__(self, memory_store: UnifiedMemoryStore, data_dir: Optional[Path] = None, workflow_engine=None):
        # Initialize BaseTool with data_dir if provided
        if data_dir:
            super().__init__(data_dir)
        else:
            # Create a temporary data directory for testing
            import tempfile
            temp_dir = Path(tempfile.mkdtemp())
            super().__init__(temp_dir)
        
        self.memory_store = memory_store
        
        # Use provided workflow engine or create a new one
        if workflow_engine:
            self.workflow_engine = workflow_engine
        else:
            self.workflow_engine = WorkflowEngine(self.memory_store)
            
        self.workflow_suggester = WorkflowSuggester(self.memory_store)

    @property
    def name(self) -> str:
        return "automation"

    @property
    def description(self) -> str:
        return "Manage workflows and automation rules for the unified memory system."

    def get_capabilities(self) -> List[str]:
        return [
            "register_workflow",
            "list_workflows", 
            "get_workflow",
            "delete_workflow",
            "pause_workflow",
            "resume_workflow",
            "trigger_workflow",
            "list_workflow_runs",
            "get_workflow_run",
            "get_workflow_suggestions",
            "approve_workflow_suggestion",
            "get_suggestion_metrics"
        ]

    def register_workflow(self, workflow_def: Dict[str, Any]) -> WorkflowDefinition:
        """Register a new workflow."""
        try:
            # Create workflow from definition
            workflow = Workflow(
                id=workflow_def.get("id", str(uuid.uuid4())),
                name=workflow_def["name"],
                description=workflow_def["description"],
                trigger=WorkflowTrigger(**workflow_def["trigger"]),
                actions=[WorkflowAction(**action) for action in workflow_def["actions"]],
                enabled=workflow_def.get("enabled", True)
            )
            
            # Register with engine (this handles both in-memory and persistence)
            self.workflow_engine.register_workflow(workflow)
            
            # Verify the workflow was registered successfully
            if workflow.id not in self.workflow_engine.workflows:
                raise RuntimeError(f"Workflow {workflow.id} was not properly registered in memory")
            
            return WorkflowDefinition(
                id=workflow.id,
                name=workflow.name,
                description=workflow.description,
                trigger=workflow.trigger.model_dump(),
                actions=[action.model_dump() for action in workflow.actions],
                enabled=workflow.enabled,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to register workflow: {e}")
            raise ValueError(f"Invalid workflow definition: {e}")

    def list_workflows(self, enabled_only: bool = False) -> List[WorkflowDefinition]:
        """List all registered workflows."""
        workflows = []
        
        # Get from engine
        engine_workflows = self.workflow_engine.list_workflows()
        
        for workflow in engine_workflows:
            if enabled_only and not workflow.enabled:
                continue
                
            workflows.append(WorkflowDefinition(
                id=workflow.id,
                name=workflow.name,
                description=workflow.description,
                trigger=workflow.trigger.model_dump(),
                actions=[action.model_dump() for action in workflow.actions],
                enabled=workflow.enabled,
                created_at=workflow.created_at.isoformat(),
                updated_at=workflow.updated_at.isoformat()
            ))
        
        return workflows

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a specific workflow by ID."""
        workflow = self.workflow_engine.get_workflow(workflow_id)
        if not workflow:
            return None
            
        return WorkflowDefinition(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            trigger=workflow.trigger.model_dump(),
            actions=[action.model_dump() for action in workflow.actions],
            enabled=workflow.enabled,
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat()
        )

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        try:
            # Remove from engine
            success = self.workflow_engine.delete_workflow(workflow_id)
            if not success:
                return False
                
            # Remove from memory store
            workflow_entities = self.memory_store.search_entities(
                entity_type="workflow",
                filters={"workflow_id": workflow_id}
            )
            
            for entity in workflow_entities:
                self.memory_store.delete_entity(entity.id)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow."""
        return self.workflow_engine.pause_workflow(workflow_id)

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow."""
        return self.workflow_engine.resume_workflow(workflow_id)

    def trigger_workflow(self, workflow_id: str, event_data: Dict[str, Any]) -> bool:
        """Manually trigger a workflow with custom event data."""
        try:
            workflow = self.workflow_engine.get_workflow(workflow_id)
            if not workflow:
                return False
                
            # Create manual event
            event = Event(
                payload=[event_data],  # Event expects a list of dicts
                source="mcp"
            )
            
            # Trigger the event
            self.workflow_engine.trigger_event(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
            return False

    def list_workflow_runs(self, workflow_id: Optional[str] = None, limit: int = 50) -> List[WorkflowRunInfo]:
        """List workflow runs."""
        try:
            # Search for workflow run entities
            filters = {}
            
            if workflow_id:
                filters["workflow_id"] = workflow_id
                
            run_entities = self.memory_store.search_entities(
                entity_type="workflow_run",
                filters=filters,
                limit=limit
            )
            
            runs = []
            for entity in run_entities:
                try:
                    run_data = json.loads(entity.content)
                    runs.append(WorkflowRunInfo(
                        id=run_data["id"],
                        workflow_id=run_data["workflow_id"],
                        event_id=run_data["event_id"],
                        status=run_data["status"],
                        started_at=run_data["started_at"],
                        completed_at=run_data.get("completed_at"),
                        logs=run_data.get("logs", []),
                        error=run_data.get("error")
                    ))
                except Exception as e:
                    logger.error(f"Failed to parse workflow run {entity.id}: {e}")
                    continue
                    
            return sorted(runs, key=lambda r: r.started_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list workflow runs: {e}")
            return []

    def get_workflow_run(self, run_id: str) -> Optional[WorkflowRunInfo]:
        """Get a specific workflow run by ID."""
        try:
            run_entities = self.memory_store.search_entities(
                entity_type="workflow_run",
                filters={"run_id": run_id}
            )
            
            if not run_entities:
                return None
                
            run_data = json.loads(run_entities[0].content)
            return WorkflowRunInfo(
                id=run_data["id"],
                workflow_id=run_data["workflow_id"],
                event_id=run_data["event_id"],
                status=run_data["status"],
                started_at=run_data["started_at"],
                completed_at=run_data.get("completed_at"),
                logs=run_data.get("logs", []),
                error=run_data.get("error")
            )
            
        except Exception as e:
            logger.error(f"Failed to get workflow run {run_id}: {e}")
            return None

    def get_workflow_suggestions(self, query: str = "", limit: int = 10) -> List[WorkflowSuggestion]:
        """Get workflow suggestions based on a query."""
        try:
            suggestions = self.workflow_suggester.suggest_workflows(query, limit=limit)
            return [
                WorkflowSuggestion(
                    id=s['id'],
                    name=s['name'],
                    description=s['description'],
                    confidence=s['confidence'],
                    reasoning=s['reasoning'],
                    category=s['category'],
                    estimated_impact=s['estimated_impact'],
                    workflow_yaml=s['workflow_yaml']
                )
                for s in suggestions
            ]
        except Exception as e:
            logger.error(f"Failed to get workflow suggestions: {e}")
            return []

    def approve_workflow_suggestion(self, suggestion_id: str) -> bool:
        """Approve a workflow suggestion."""
        try:
            success = self.workflow_suggester.approve_suggestion(suggestion_id)
            if success:
                # Optionally, you might want to re-register the approved workflow
                # This would require fetching the suggestion and its workflow definition
                # For now, we just approve it.
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to approve workflow suggestion {suggestion_id}: {e}")
            return False

    def get_suggestion_metrics(self) -> Dict[str, Any]:
        """Get metrics for workflow suggestions."""
        try:
            return self.workflow_suggester.get_metrics()
        except Exception as e:
            logger.error(f"Failed to get suggestion metrics: {e}")
            return {}

    def register(self, mcp):
        @mcp.tool(
            name="automation_register_workflow",
            description="Register a new automation workflow with triggers, conditions, and actions",
            tags={"automation", "workflow", "register", "create", "configuration"},
            annotations={
                "destructiveHint": True,
                "idempotentHint": False
            }
        )
        async def automation_register_workflow(workflow_definition: dict) -> dict:
            """Register a new automation workflow."""
            try:
                workflow = self.register_workflow(workflow_definition)
                return {
                    "success": True,
                    "workflow": workflow.model_dump(),
                    "message": f"Workflow '{workflow.name}' registered successfully"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to register workflow"
                }

        @mcp.tool(
            name="automation_list_workflows",
            description="List all registered automation workflows with optional filtering by enabled status",
            tags={"automation", "workflow", "list", "view", "management"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def automation_list_workflows(enabled_only: bool = False) -> dict:
            """List all registered automation workflows."""
            try:
                workflows = self.list_workflows(enabled_only=enabled_only)
                return {
                    "success": True,
                    "workflows": [w.dict() for w in workflows],
                    "count": len(workflows)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to list workflows"
                }

        @mcp.tool(
            name="automation_get_workflow",
            description="Get detailed information about a specific automation workflow including configuration and status",
            tags={"automation", "workflow", "get", "details", "view"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def automation_get_workflow(workflow_id: str) -> dict:
            """Get a specific automation workflow by ID."""
            try:
                workflow = self.get_workflow(workflow_id)
                if workflow:
                    return {
                        "success": True,
                        "workflow": workflow.dict()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow not found",
                        "message": f"No workflow found with ID: {workflow_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get workflow"
                }

        @mcp.tool(
            name="automation_delete_workflow",
            description="Permanently delete an automation workflow and stop all its scheduled executions",
            tags={"automation", "workflow", "delete", "remove", "cleanup"},
            annotations={
                "destructiveHint": True,
                "idempotentHint": True
            }
        )
        async def automation_delete_workflow(workflow_id: str) -> dict:
            """Delete an automation workflow."""
            try:
                success = self.delete_workflow(workflow_id)
                if success:
                    return {
                        "success": True,
                        "message": f"Workflow {workflow_id} deleted successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow not found or deletion failed",
                        "message": f"Failed to delete workflow {workflow_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to delete workflow"
                }

        @mcp.tool(
            name="automation_pause_workflow",
            description="Pause an automation workflow to temporarily stop its execution without deleting it",
            tags={"automation", "workflow", "pause", "control", "management"},
            annotations={
                "destructiveHint": False,
                "idempotentHint": True
            }
        )
        async def automation_pause_workflow(workflow_id: str) -> dict:
            """Pause an automation workflow."""
            try:
                success = self.pause_workflow(workflow_id)
                if success:
                    return {
                        "success": True,
                        "message": f"Workflow {workflow_id} paused successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow not found or pause failed",
                        "message": f"Failed to pause workflow {workflow_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to pause workflow"
                }

        @mcp.tool(
            name="automation_resume_workflow",
            description="Resume a paused automation workflow to continue its scheduled execution",
            tags={"automation", "workflow", "resume", "control", "management"},
            annotations={
                "destructiveHint": False,
                "idempotentHint": True
            }
        )
        async def automation_resume_workflow(workflow_id: str) -> dict:
            """Resume a paused automation workflow."""
            try:
                success = self.resume_workflow(workflow_id)
                if success:
                    return {
                        "success": True,
                        "message": f"Workflow {workflow_id} resumed successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow not found or resume failed",
                        "message": f"Failed to resume workflow {workflow_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to resume workflow"
                }

        @mcp.tool(
            name="automation_trigger_workflow",
            description="Manually trigger an automation workflow with optional event data for immediate execution",
            tags={"automation", "workflow", "trigger", "execute", "manual"},
            annotations={
                "destructiveHint": False,
                "idempotentHint": False
            }
        )
        async def automation_trigger_workflow(workflow_id: str, event_data: Optional[Dict[str, Any]] = None) -> dict:
            """Manually trigger an automation workflow."""
            try:
                if event_data is None:
                    event_data = {}
                    
                success = self.trigger_workflow(workflow_id, event_data)
                if success:
                    return {
                        "success": True,
                        "message": f"Workflow {workflow_id} triggered successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow not found or trigger failed",
                        "message": f"Failed to trigger workflow {workflow_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to trigger workflow"
                }

        @mcp.tool(
            name="automation_list_runs",
            description="List automation workflow runs with optional filtering by workflow and execution history",
            tags={"automation", "workflow", "runs", "history", "monitoring"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def automation_list_runs(workflow_id: Optional[str] = None, limit: int = 50) -> dict:
            """List automation workflow runs."""
            try:
                runs = self.list_workflow_runs(workflow_id=workflow_id, limit=limit)
                return {
                    "success": True,
                    "runs": [r.dict() for r in runs],
                    "count": len(runs)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to list workflow runs"
                }

        @mcp.tool(
            name="automation_get_run",
            description="Get detailed information about a specific workflow run including status, logs, and results",
            tags={"automation", "workflow", "run", "details", "monitoring"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def automation_get_run(run_id: str) -> dict:
            """Get a specific automation workflow run by ID."""
            try:
                run = self.get_workflow_run(run_id)
                if run:
                    return {
                        "success": True,
                        "run": run.dict()
                    }
                else:
                    return {
                        "success": False,
                        "error": "Run not found",
                        "message": f"No workflow run found with ID: {run_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get workflow run"
                }

        @mcp.tool(
            name="automation_get_workflow_suggestions",
            description="Get intelligent workflow suggestions based on query patterns and usage analytics",
            tags={"automation", "workflow", "suggestions", "ai", "recommendations"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def automation_get_workflow_suggestions(query: str = "", limit: int = 10) -> dict:
            """Get workflow suggestions based on a query."""
            try:
                suggestions = self.get_workflow_suggestions(query, limit=limit)
                return {
                    "success": True,
                    "suggestions": [s.model_dump() for s in suggestions],
                    "count": len(suggestions)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get workflow suggestions"
                }

        @mcp.tool(
            name="automation_approve_workflow_suggestion",
            description="Approve and implement a workflow suggestion to create an active automation workflow",
            tags={"automation", "workflow", "suggestions", "approve", "implement"},
            annotations={
                "destructiveHint": True,
                "idempotentHint": True
            }
        )
        async def automation_approve_workflow_suggestion(suggestion_id: str) -> dict:
            """Approve a workflow suggestion."""
            try:
                success = self.approve_workflow_suggestion(suggestion_id)
                if success:
                    return {
                        "success": True,
                        "message": f"Workflow suggestion {suggestion_id} approved successfully"
                    }
                else:
                    return {
                        "success": False,
                        "error": "Workflow suggestion not found or approval failed",
                        "message": f"Failed to approve workflow suggestion {suggestion_id}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to approve workflow suggestion"
                }

        @mcp.tool(
            name="automation_get_suggestion_metrics",
            description="Get analytics and metrics for workflow suggestions including approval rates and effectiveness",
            tags={"automation", "metrics", "analytics", "suggestions", "performance"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def automation_get_suggestion_metrics() -> dict:
            """Get metrics for workflow suggestions."""
            try:
                metrics = self.get_suggestion_metrics()
                return {
                    "success": True,
                    "metrics": metrics
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to get suggestion metrics"
                }


        def automation_workflows_resource() -> str:
            """Get a list of all automation workflows."""
            try:
                workflows = self.list_workflows()
                workflow_list = []
                for w in workflows:
                    workflow_list.append({
                        "id": w.id,
                        "name": w.name,
                        "description": w.description,
                        "enabled": w.enabled,
                        "trigger_type": w.trigger.get("type"),
                        "action_count": len(w.actions)
                    })
                
                return json.dumps({
                    "workflows": workflow_list,
                    "count": len(workflow_list),
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e),
                    "workflows": [],
                    "count": 0
                }, indent=2)

        # @mcp.resource("resource://automation/workflows/{workflow_id}")
        def automation_workflow_detail(workflow_id: str) -> str:
            """Get detailed information about a specific workflow."""
            try:
                workflow = self.get_workflow(workflow_id)
                if workflow:
                    return json.dumps(workflow.dict(), indent=2)
                else:
                    return json.dumps({
                        "error": "Workflow not found",
                        "workflow_id": workflow_id
                    }, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e),
                    "workflow_id": workflow_id
                }, indent=2)

        # @mcp.resource("resource://automation/runs")
        def automation_runs_resource() -> str:
            """Get a list of recent workflow runs."""
            try:
                runs = self.list_workflow_runs(limit=20)
                run_list = []
                for r in runs:
                    run_list.append({
                        "id": r.id,
                        "workflow_id": r.workflow_id,
                        "status": r.status,
                        "started_at": r.started_at,
                        "completed_at": r.completed_at,
                        "has_error": bool(r.error)
                    })
                
                return json.dumps({
                    "runs": run_list,
                    "count": len(run_list),
                    "timestamp": datetime.now().isoformat()
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "error": str(e),
                    "runs": [],
                    "count": 0
                }, indent=2)
        
        logger.info("Automation MCP tools registered successfully")