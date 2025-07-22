"""
Unit tests for automation tool and workflow engine.
Phase 4.2: Smart Workflows & Automation
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from workflows.engine import Workflow, WorkflowAction, WorkflowTrigger, Event
from core import UnifiedMemoryStore
from tools.automation.automation import AutomationTool, WorkflowDefinition


class TestAutomationTool:
    """Test cases for the AutomationTool class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def memory_store(self, temp_dir):
        """Create a test memory store."""
        from core import UnifiedMemoryStore
        db_path = temp_dir / "test_memory.db"
        return UnifiedMemoryStore(db_path, enable_vector_search=False, enable_ai_extraction=False)
    
    @pytest.fixture
    def automation_tool(self, memory_store, temp_dir):
        """Create an AutomationTool instance for testing."""
        return AutomationTool(memory_store, temp_dir)

    @pytest.fixture
    def sample_workflow_definition(self):
        """Sample workflow definition for testing."""
        return {
            "id": "test-workflow-1",
            "name": "Test Workflow",
            "description": "A test workflow for automation",
            "trigger": {
                "type": "entity_created",
                "filter": {"entity_type": "task"}
            },
            "actions": [
                {
                    "type": "create_task",
                    "params": {
                        "title": "Follow up on {{ entity.metadata.title }}",
                        "description": "Auto-generated follow-up task"
                    }
                }
            ],
            "enabled": True
        }

    def test_automation_tool_initialization(self, automation_tool):
        """Test that the automation tool initializes correctly."""
        assert automation_tool.name == "automation"
        assert "Manage workflows and automation" in automation_tool.description
        assert "register_workflow" in automation_tool.get_capabilities()
        assert "list_workflows" in automation_tool.get_capabilities()
        assert "trigger_workflow" in automation_tool.get_capabilities()

    def test_register_workflow_success(self, automation_tool, sample_workflow_definition):
        """Test successful workflow registration."""
        with patch.object(automation_tool.memory_store, 'save_entity') as mock_save:
            mock_save.return_value = Mock(id="test-entity-id")
            
            result = automation_tool.register_workflow(sample_workflow_definition)
            
            assert isinstance(result, WorkflowDefinition)
            assert result.id == "test-workflow-1"
            assert result.name == "Test Workflow"
            assert result.enabled is True
            assert len(result.actions) == 1
            assert result.actions[0]["type"] == "create_task"

    def test_register_workflow_invalid_definition(self, automation_tool):
        """Test workflow registration with invalid definition."""
        invalid_definition = {
            "name": "Invalid Workflow",
            # Missing required fields
        }
        
        with pytest.raises(ValueError, match="Invalid workflow definition"):
            automation_tool.register_workflow(invalid_definition)

    def test_list_workflows_empty(self, automation_tool):
        """Test listing workflows when none exist."""
        with patch.object(automation_tool.workflow_engine, 'list_workflows') as mock_list:
            mock_list.return_value = []
            
            workflows = automation_tool.list_workflows()
            assert workflows == []

    def test_list_workflows_with_workflows(self, automation_tool):
        """Test listing workflows when workflows exist."""
        mock_workflow = Mock()
        mock_workflow.id = "test-1"
        mock_workflow.name = "Test Workflow"
        mock_workflow.description = "Test description"
        mock_workflow.trigger = Mock()
        mock_workflow.trigger.model_dump = lambda: {"type": "entity_created"}
        mock_workflow.actions = [Mock()]
        mock_workflow.actions[0].model_dump = lambda: {"type": "create_task"}
        mock_workflow.enabled = True
        mock_workflow.created_at = Mock()
        mock_workflow.created_at.isoformat = lambda: "2024-01-01T00:00:00"
        mock_workflow.updated_at = Mock()
        mock_workflow.updated_at.isoformat = lambda: "2024-01-01T00:00:00"
        
        with patch.object(automation_tool.workflow_engine, 'list_workflows') as mock_list:
            mock_list.return_value = [mock_workflow]
            
            workflows = automation_tool.list_workflows()
            assert len(workflows) == 1
            assert workflows[0].id == "test-1"
            assert workflows[0].name == "Test Workflow"

    def test_list_workflows_enabled_only(self, automation_tool):
        """Test listing only enabled workflows."""
        mock_workflow_enabled = Mock()
        mock_workflow_enabled.id = "test-1"
        mock_workflow_enabled.name = "Enabled Workflow"
        mock_workflow_enabled.description = "Test description"
        mock_workflow_enabled.trigger = Mock()
        mock_workflow_enabled.trigger.model_dump = lambda: {"type": "entity_created"}
        mock_workflow_enabled.actions = [Mock()]
        mock_workflow_enabled.actions[0].model_dump = lambda: {"type": "create_task"}
        mock_workflow_enabled.enabled = True
        mock_workflow_enabled.created_at = Mock()
        mock_workflow_enabled.created_at.isoformat = lambda: "2024-01-01T00:00:00"
        mock_workflow_enabled.updated_at = Mock()
        mock_workflow_enabled.updated_at.isoformat = lambda: "2024-01-01T00:00:00"
        
        mock_workflow_disabled = Mock()
        mock_workflow_disabled.id = "test-2"
        mock_workflow_disabled.name = "Disabled Workflow"
        mock_workflow_disabled.description = "Test description"
        mock_workflow_disabled.trigger = Mock()
        mock_workflow_disabled.trigger.model_dump = lambda: {"type": "entity_created"}
        mock_workflow_disabled.actions = [Mock()]
        mock_workflow_disabled.actions[0].model_dump = lambda: {"type": "create_task"}
        mock_workflow_disabled.enabled = False
        mock_workflow_disabled.created_at = Mock()
        mock_workflow_disabled.created_at.isoformat = lambda: "2024-01-01T00:00:00"
        mock_workflow_disabled.updated_at = Mock()
        mock_workflow_disabled.updated_at.isoformat = lambda: "2024-01-01T00:00:00"
        
        with patch.object(automation_tool.workflow_engine, 'list_workflows') as mock_list:
            mock_list.return_value = [mock_workflow_enabled, mock_workflow_disabled]
            
            workflows = automation_tool.list_workflows(enabled_only=True)
            assert len(workflows) == 1
            assert workflows[0].id == "test-1"
            assert workflows[0].name == "Enabled Workflow"

    def test_get_workflow_success(self, automation_tool):
        """Test getting a specific workflow."""
        mock_workflow = Mock()
        mock_workflow.id = "test-1"
        mock_workflow.name = "Test Workflow"
        mock_workflow.description = "Test description"
        mock_workflow.trigger = Mock()
        mock_workflow.trigger.model_dump = lambda: {"type": "entity_created"}
        mock_workflow.actions = [Mock()]
        mock_workflow.actions[0].model_dump = lambda: {"type": "create_task"}
        mock_workflow.enabled = True
        mock_workflow.created_at = Mock()
        mock_workflow.created_at.isoformat = lambda: "2024-01-01T00:00:00"
        mock_workflow.updated_at = Mock()
        mock_workflow.updated_at.isoformat = lambda: "2024-01-01T00:00:00"
        
        with patch.object(automation_tool.workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = mock_workflow
            
            workflow = automation_tool.get_workflow("test-1")
            assert workflow is not None
            assert workflow.id == "test-1"
            assert workflow.name == "Test Workflow"

    def test_get_workflow_not_found(self, automation_tool):
        """Test getting a workflow that doesn't exist."""
        with patch.object(automation_tool.workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = None
            
            workflow = automation_tool.get_workflow("nonexistent")
            assert workflow is None

    def test_delete_workflow_success(self, automation_tool):
        """Test successful workflow deletion."""
        with patch.object(automation_tool.workflow_engine, 'delete_workflow') as mock_delete:
            with patch.object(automation_tool.memory_store, 'search_entities') as mock_search:
                with patch.object(automation_tool.memory_store, 'delete_entity') as mock_delete_entity:
                    mock_delete.return_value = True
                    mock_search.return_value = [Mock(id="test-entity")]
                    
                    success = automation_tool.delete_workflow("test-1")
                    assert success is True
                    mock_delete.assert_called_once_with("test-1")

    def test_delete_workflow_not_found(self, automation_tool):
        """Test deleting a workflow that doesn't exist."""
        with patch.object(automation_tool.workflow_engine, 'delete_workflow') as mock_delete:
            mock_delete.return_value = False
            
            success = automation_tool.delete_workflow("nonexistent")
            assert success is False

    def test_pause_workflow(self, automation_tool):
        """Test pausing a workflow."""
        with patch.object(automation_tool.workflow_engine, 'pause_workflow') as mock_pause:
            mock_pause.return_value = True
            
            success = automation_tool.pause_workflow("test-1")
            assert success is True
            mock_pause.assert_called_once_with("test-1")

    def test_resume_workflow(self, automation_tool):
        """Test resuming a workflow."""
        with patch.object(automation_tool.workflow_engine, 'resume_workflow') as mock_resume:
            mock_resume.return_value = True
            
            success = automation_tool.resume_workflow("test-1")
            assert success is True
            mock_resume.assert_called_once_with("test-1")

    def test_trigger_workflow_success(self, automation_tool):
        """Test successful workflow triggering."""
        mock_workflow = Mock(id="test-1")
        
        with patch.object(automation_tool.workflow_engine, 'get_workflow') as mock_get:
            with patch.object(automation_tool.workflow_engine, 'trigger_event') as mock_trigger:
                mock_get.return_value = mock_workflow
                
                success = automation_tool.trigger_workflow("test-1", {"test": "data"})
                assert success is True
                mock_trigger.assert_called_once()

    def test_trigger_workflow_not_found(self, automation_tool):
        """Test triggering a workflow that doesn't exist."""
        with patch.object(automation_tool.workflow_engine, 'get_workflow') as mock_get:
            mock_get.return_value = None
            
            success = automation_tool.trigger_workflow("nonexistent", {})
            assert success is False

    def test_list_workflow_runs_empty(self, automation_tool):
        """Test listing workflow runs when none exist."""
        with patch.object(automation_tool.memory_store, 'search_entities') as mock_search:
            mock_search.return_value = []
            
            runs = automation_tool.list_workflow_runs()
            assert runs == []

    def test_list_workflow_runs_with_runs(self, automation_tool):
        """Test listing workflow runs when runs exist."""
        mock_entity = Mock(
            content=json.dumps({
                "id": "run-1",
                "workflow_id": "workflow-1",
                "event_id": "event-1",
                "status": "completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:01:00",
                "logs": ["Step 1 completed"],
                "error": None
            })
        )
        
        with patch.object(automation_tool.memory_store, 'search_entities') as mock_search:
            mock_search.return_value = [mock_entity]
            
            runs = automation_tool.list_workflow_runs()
            assert len(runs) == 1
            assert runs[0].id == "run-1"
            assert runs[0].workflow_id == "workflow-1"
            assert runs[0].status == "completed"

    def test_get_workflow_run_success(self, automation_tool):
        """Test getting a specific workflow run."""
        mock_entity = Mock(
            content=json.dumps({
                "id": "run-1",
                "workflow_id": "workflow-1",
                "event_id": "event-1",
                "status": "completed",
                "started_at": "2024-01-01T00:00:00",
                "completed_at": "2024-01-01T00:01:00",
                "logs": ["Step 1 completed"],
                "error": None
            })
        )
        
        with patch.object(automation_tool.memory_store, 'search_entities') as mock_search:
            mock_search.return_value = [mock_entity]
            
            run = automation_tool.get_workflow_run("run-1")
            assert run is not None
            assert run.id == "run-1"
            assert run.workflow_id == "workflow-1"
            assert run.status == "completed"

    def test_get_workflow_run_not_found(self, automation_tool):
        """Test getting a workflow run that doesn't exist."""
        with patch.object(automation_tool.memory_store, 'search_entities') as mock_search:
            mock_search.return_value = []
            
            run = automation_tool.get_workflow_run("nonexistent")
            assert run is None


class TestAutomationToolMCPIntegration:
    """Test cases for MCP tool integration."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def memory_store(self, temp_dir):
        """Create a test memory store."""
        from core import UnifiedMemoryStore
        db_path = temp_dir / "test_memory.db"
        return UnifiedMemoryStore(db_path, enable_vector_search=False, enable_ai_extraction=False)

    @pytest.fixture
    def automation_tool(self, memory_store, temp_dir):
        """Create an AutomationTool instance for testing."""
        return AutomationTool(memory_store, temp_dir)

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server."""
        mock = Mock()
        
        # Store the actual functions that get decorated
        mock.tool_functions = []
        mock.resource_functions = []
        
        def mock_tool_decorator(func=None):
            if func is None:
                # Called as @mcp.tool()
                def decorator(f):
                    mock.tool_functions.append(f)
                    return f
                return decorator
            else:
                # Called as @mcp.tool
                mock.tool_functions.append(func)
                return func
        
        def mock_resource_decorator(resource_path=None):
            if resource_path is None:
                # Called as @mcp.resource()
                def decorator(f):
                    mock.resource_functions.append(f)
                    return f
                return decorator
            elif callable(resource_path):
                # Called as @mcp.resource
                mock.resource_functions.append(resource_path)
                return resource_path
            else:
                # Called as @mcp.resource("path")
                def decorator(f):
                    mock.resource_functions.append(f)
                    return f
                return decorator
        
        mock.tool = mock_tool_decorator
        mock.resource = mock_resource_decorator
        return mock

    def test_register_mcp_tools(self, automation_tool, mock_mcp):
        """Test that MCP tools are registered correctly."""
        automation_tool.register(mock_mcp)
        
        # Check that tool decorators were called
        assert len(mock_mcp.tool_functions) >= 8  # Should have at least 8 tools
        
        # Check that resource decorators were called
        assert len(mock_mcp.resource_functions) >= 3  # Should have at least 3 resources

    @pytest.mark.asyncio
    async def test_automation_register_workflow_tool_success(self, automation_tool, mock_mcp):
        """Test the automation_register_workflow MCP tool."""
        automation_tool.register(mock_mcp)
        
        # Get the registered tool function
        tool_func = mock_mcp.tool_functions[0]  # First tool
        
        with patch.object(automation_tool, 'register_workflow') as mock_register:
            mock_workflow = Mock()
            mock_workflow.model_dump = lambda: {"id": "test-1", "name": "Test Workflow"}
            mock_workflow.name = "Test Workflow"
            mock_register.return_value = mock_workflow
            
            result = await tool_func({
                "id": "test-1",
                "name": "Test Workflow",
                "description": "Test description",
                "trigger": {"type": "entity_created"},
                "actions": [{"type": "create_task", "params": {}}]
            })
            
            assert result["success"] is True
            assert "Test Workflow" in result["message"]

    @pytest.mark.asyncio
    async def test_automation_register_workflow_tool_failure(self, automation_tool, mock_mcp):
        """Test the automation_register_workflow MCP tool with invalid input."""
        automation_tool.register(mock_mcp)
        
        # Get the registered tool function
        tool_func = mock_mcp.tool_functions[0]  # First tool
        
        with patch.object(automation_tool, 'register_workflow') as mock_register:
            mock_register.side_effect = ValueError("Invalid workflow")
            
            result = await tool_func({
                "name": "Invalid Workflow"
                # Missing required fields
            })
            
            assert result["success"] is False
            assert "Invalid workflow" in result["error"]

    @pytest.mark.asyncio
    async def test_automation_list_workflows_tool(self, automation_tool, mock_mcp):
        """Test the automation_list_workflows MCP tool."""
        automation_tool.register(mock_mcp)
        
        # Get the registered tool function
        tool_func = mock_mcp.tool_functions[1]  # Second tool
        
        with patch.object(automation_tool, 'list_workflows') as mock_list:
            mock_workflows = [Mock()]
            mock_workflows[0].model_dump = lambda: {"id": "test-1", "name": "Test"}
            mock_list.return_value = mock_workflows
            
            result = await tool_func(enabled_only=False)
            
            assert result["success"] is True
            assert result["count"] == 1
            assert len(result["workflows"]) == 1

    @pytest.mark.asyncio
    async def test_automation_trigger_workflow_tool(self, automation_tool, mock_mcp):
        """Test the automation_trigger_workflow MCP tool."""
        automation_tool.register(mock_mcp)
        
        # Get the registered tool function
        tool_func = mock_mcp.tool_functions[6]  # Seventh tool (automation_trigger_workflow)
        
        with patch.object(automation_tool, 'trigger_workflow') as mock_trigger:
            mock_trigger.return_value = True
            
            result = await tool_func("test-1", {"test": "data"})
            
            assert result["success"] is True
            assert "triggered successfully" in result["message"]

    def test_automation_workflows_resource(self, automation_tool, mock_mcp):
        """Test the automation workflows resource."""
        automation_tool.register(mock_mcp)
        
        # Get the registered resource function
        resource_func = mock_mcp.resource_functions[0]  # First resource
        
        with patch.object(automation_tool, 'list_workflows') as mock_list:
            from tools.automation.automation import WorkflowDefinition
            mock_workflows = [
                WorkflowDefinition(
                    id="test-1",
                    name="Test Workflow",
                    description="Test description",
                    enabled=True,
                    trigger={"type": "entity_created"},
                    actions=[{"type": "create_task"}, {"type": "notify"}]  # 2 actions
                )
            ]
            mock_list.return_value = mock_workflows
            
            result = resource_func()
            data = json.loads(result)
            
            assert data["count"] == 1
            assert len(data["workflows"]) == 1
            assert data["workflows"][0]["id"] == "test-1"
            assert data["workflows"][0]["action_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__]) 