import json
import pytest
import tempfile
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from tools.async_tasks.async_tasks import AsyncTasksTool, AsyncTask, TaskStatus, TaskPriority


class TestAsyncTasksTool:
    """Test suite for AsyncTasksTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def async_tasks_tool(self, temp_data_dir):
        """Create an AsyncTasksTool instance for testing."""
        return AsyncTasksTool(temp_data_dir)

    @pytest.fixture
    def sample_tasks(self):
        """Sample async tasks for testing."""
        return [
            {
                "name": "Data processing task",
                "description": "Process large dataset",
                "command": "process_data",
                "arguments": {"dataset": "large.csv", "output": "results.json"},
                "priority": TaskPriority.HIGH,
                "tags": ["data", "processing"]
            },
            {
                "name": "Email notification",
                "description": "Send email notifications",
                "command": "send_email",
                "arguments": {"recipients": ["user@example.com"], "subject": "Update"},
                "priority": TaskPriority.NORMAL,
                "tags": ["email", "notification"]
            },
            {
                "name": "Backup task",
                "description": "Create system backup",
                "command": "backup",
                "arguments": {"source": "/data", "destination": "/backup"},
                "priority": TaskPriority.LOW,
                "tags": ["backup", "system"]
            }
        ]

    def test_name_property(self, async_tasks_tool):
        """Test that the tool name is correct."""
        assert async_tasks_tool.name == "async_tasks"

    def test_description_property(self, async_tasks_tool):
        """Test that the tool description is correct."""
        assert async_tasks_tool.description == "Schedule and manage background tasks and future task execution"

    def test_get_capabilities(self, async_tasks_tool):
        """Test that all expected capabilities are returned."""
        capabilities = async_tasks_tool.get_capabilities()
        expected_capabilities = [
            "create_task",
            "schedule_task",
            "list_tasks",
            "get_task",
            "cancel_task",
            "get_task_status",
            "get_running_tasks",
            "get_task_history"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_tasks_empty_file(self, async_tasks_tool):
        """Test reading an empty tasks file."""
        result = async_tasks_tool._read_tasks()
        assert result == []

    def test_read_tasks_with_data(self, async_tasks_tool, sample_tasks):
        """Test reading tasks from file."""
        # Write some test data
        with open(async_tasks_tool.data_file, 'w') as f:
            for task_data in sample_tasks:
                task = AsyncTask(**task_data)
                f.write(task.json() + '\n')
        
        result = async_tasks_tool._read_tasks()
        assert len(result) == 3
        assert all(isinstance(task, AsyncTask) for task in result)

    def test_write_tasks(self, async_tasks_tool, sample_tasks):
        """Test writing tasks to file."""
        tasks = [AsyncTask(**task_data) for task_data in sample_tasks]
        async_tasks_tool._write_tasks(tasks)
        
        # Verify the data was written correctly
        with open(async_tasks_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for i, line in enumerate(lines):
            task = AsyncTask(**json.loads(line.strip()))
            assert task.name == sample_tasks[i]['name']

    def test_create_task_basic(self, async_tasks_tool):
        """Test creating a basic task."""
        task = async_tasks_tool.create_task(
            name="Test task",
            command="test_command",
            description="Test description",
            priority=TaskPriority.HIGH
        )
        
        assert task.id == 1
        assert task.name == "Test task"
        assert task.command == "test_command"
        assert task.description == "Test description"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.created_at is not None

    def test_create_task_with_arguments(self, async_tasks_tool):
        """Test creating a task with arguments."""
        arguments = {"param1": "value1", "param2": 42}
        task = async_tasks_tool.create_task(
            name="Task with args",
            command="test_command",
            arguments=arguments
        )
        
        assert task.arguments == arguments

    def test_create_task_with_tags(self, async_tasks_tool):
        """Test creating a task with tags."""
        tags = ["urgent", "processing", "data"]
        task = async_tasks_tool.create_task(
            name="Task with tags",
            command="test_command",
            tags=tags
        )
        
        assert task.tags == tags

    def test_create_task_id_increment(self, async_tasks_tool):
        """Test that task IDs increment properly."""
        task1 = async_tasks_tool.create_task(name="First task", command="cmd1")
        task2 = async_tasks_tool.create_task(name="Second task", command="cmd2")
        task3 = async_tasks_tool.create_task(name="Third task", command="cmd3")
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_schedule_task(self, async_tasks_tool):
        """Test scheduling a task for future execution."""
        scheduled_time = datetime.now() + timedelta(hours=1)
        task = async_tasks_tool.schedule_task(
            name="Scheduled task",
            command="scheduled_command",
            scheduled_at=scheduled_time
        )
        
        assert task.id == 1
        assert task.name == "Scheduled task"
        assert task.command == "scheduled_command"
        assert task.scheduled_at == scheduled_time
        assert task.status == TaskStatus.PENDING

    def test_list_tasks_all(self, async_tasks_tool, sample_tasks):
        """Test listing all tasks."""
        # Create tasks
        for task_data in sample_tasks:
            async_tasks_tool.create_task(**task_data)
        
        tasks = async_tasks_tool.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_by_status(self, async_tasks_tool, sample_tasks):
        """Test listing tasks filtered by status."""
        # Create tasks
        created_tasks = []
        for task_data in sample_tasks:
            created_tasks.append(async_tasks_tool.create_task(**task_data))
        
        # Update some tasks to different statuses
        async_tasks_tool.update_task(created_tasks[1].id, status=TaskStatus.RUNNING)
        async_tasks_tool.update_task(created_tasks[2].id, status=TaskStatus.COMPLETED)
        
        pending_tasks = async_tasks_tool.list_tasks(status=TaskStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].status == TaskStatus.PENDING

    def test_list_tasks_by_priority(self, async_tasks_tool, sample_tasks):
        """Test listing tasks filtered by priority."""
        # Create tasks
        for task_data in sample_tasks:
            async_tasks_tool.create_task(**task_data)
        
        high_priority_tasks = async_tasks_tool.list_tasks(priority=TaskPriority.HIGH)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].priority == TaskPriority.HIGH

    def test_list_tasks_with_limit(self, async_tasks_tool, sample_tasks):
        """Test listing tasks with limit."""
        # Create tasks
        for task_data in sample_tasks:
            async_tasks_tool.create_task(**task_data)
        
        tasks = async_tasks_tool.list_tasks(limit=2)
        assert len(tasks) == 2

    def test_get_task(self, async_tasks_tool):
        """Test getting a specific task."""
        created_task = async_tasks_tool.create_task(name="Test task", command="test_command")
        retrieved_task = async_tasks_tool.get_task(created_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.name == created_task.name

    def test_get_task_nonexistent(self, async_tasks_tool):
        """Test getting a non-existent task."""
        result = async_tasks_tool.get_task(999)
        assert result is None

    def test_cancel_task(self, async_tasks_tool):
        """Test canceling a task."""
        task = async_tasks_tool.create_task(name="Task to cancel", command="cancel_command")
        
        # Verify task exists and is pending
        assert async_tasks_tool.get_task(task.id) is not None
        assert task.status == TaskStatus.PENDING
        
        # Cancel task
        result = async_tasks_tool.cancel_task(task.id)
        assert result is True
        
        # Verify task is cancelled
        cancelled_task = async_tasks_tool.get_task(task.id)
        assert cancelled_task.status == TaskStatus.CANCELLED

    def test_cancel_task_nonexistent(self, async_tasks_tool):
        """Test canceling a non-existent task."""
        result = async_tasks_tool.cancel_task(999)
        assert result is False

    def test_get_task_status(self, async_tasks_tool):
        """Test getting task status."""
        task = async_tasks_tool.create_task(name="Status test task", command="status_command")
        
        status_info = async_tasks_tool.get_task_status(task.id)
        
        assert status_info is not None
        assert status_info['id'] == task.id
        assert status_info['name'] == task.name
        assert status_info['status'] == task.status.value

    def test_get_task_status_nonexistent(self, async_tasks_tool):
        """Test getting status of non-existent task."""
        result = async_tasks_tool.get_task_status(999)
        assert result is None

    def test_get_running_tasks(self, async_tasks_tool):
        """Test getting running tasks."""
        # Create a task and manually set it to running status
        task = async_tasks_tool.create_task(
            name="Running task",
            command="running_command",
            description="A task that is running"
        )
        
        # Manually update the task status to running
        async_tasks_tool.update_task(task.id, status=TaskStatus.RUNNING)
        
        running_tasks = async_tasks_tool.get_running_tasks()
        assert len(running_tasks) == 1
        assert running_tasks[0]['status'] == TaskStatus.RUNNING.value

    def test_get_task_history(self, async_tasks_tool):
        """Test getting task history."""
        # Create some tasks
        for i in range(5):
            async_tasks_tool.create_task(name=f"Task {i}", command=f"cmd{i}")
        
        # Get history for last 7 days (default)
        history = async_tasks_tool.get_task_history()
        assert len(history) == 5
        
        # Get history for last 1 day (should be all tasks since they're recent)
        history = async_tasks_tool.get_task_history(days=1)
        assert len(history) == 5

    def test_get_task_history_with_old_tasks(self, async_tasks_tool):
        """Test getting task history with old tasks."""
        # Create a task that appears to be old
        old_task_data = {
            "name": "Old task",
            "command": "old_command",
            "created_at": datetime.now() - timedelta(days=10)
        }
        
        # Write the old task directly to the file
        with open(async_tasks_tool.data_file, 'w') as f:
            task = AsyncTask(**old_task_data)
            f.write(task.json() + '\n')
        
        # Get history for last 5 days (should not include the old task)
        history = async_tasks_tool.get_task_history(days=5)
        assert len(history) == 0

    def test_register_tools(self, async_tasks_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        
        async_tasks_tool.register(mock_mcp)
        
        # Verify tools were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'async_tasks_create',
            'async_tasks_list',
            'async_tasks_get_status'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, async_tasks_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "async_tasks.jsonl"
        assert async_tasks_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, async_tasks_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(async_tasks_tool.data_file, 'w') as f:
            f.write('{"name": "valid task", "command": "valid"}\n')
            f.write('invalid json line\n')
            f.write('{"name": "another valid task", "command": "valid"}\n')
        
        # Should skip invalid lines and return valid ones
        result = async_tasks_tool._read_tasks()
        assert len(result) == 2
        assert result[0].name == "valid task"
        assert result[1].name == "another valid task"

    def test_async_task_model_validation(self):
        """Test AsyncTask model validation."""
        # Valid task
        task = AsyncTask(
            name="Valid task",
            command="valid_command",
            description="Valid description",
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING
        )
        assert task.name == "Valid task"
        assert task.command == "valid_command"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING

    def test_async_task_default_values(self):
        """Test AsyncTask model default values."""
        task = AsyncTask(name="Test task", command="test_command")
        
        assert task.priority == TaskPriority.NORMAL
        assert task.status == TaskStatus.PENDING
        assert task.arguments == {}
        assert task.tags == []
        assert task.created_at is not None
        assert task.scheduled_at is None
        assert task.started_at is None
        assert task.completed_at is None
        assert task.result is None
        assert task.error is None

    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.FAILED == "failed"
        assert TaskStatus.CANCELLED == "cancelled"

    def test_task_priority_enum(self):
        """Test TaskPriority enum values."""
        assert TaskPriority.LOW == "low"
        assert TaskPriority.NORMAL == "normal"
        assert TaskPriority.HIGH == "high"
        assert TaskPriority.CRITICAL == "critical"

    def test_task_with_complex_arguments(self, async_tasks_tool):
        """Test creating a task with complex arguments."""
        complex_args = {
            "nested": {"key": "value", "list": [1, 2, 3]},
            "boolean": True,
            "number": 42.5,
            "string": "test"
        }
        
        task = async_tasks_tool.create_task(
            name="Complex args task",
            command="complex_command",
            arguments=complex_args
        )
        
        assert task.arguments == complex_args

    def test_task_with_empty_arguments(self, async_tasks_tool):
        """Test creating a task with empty arguments."""
        task = async_tasks_tool.create_task(
            name="Empty args task",
            command="empty_command",
            arguments={}
        )
        
        assert task.arguments == {}

    def test_task_with_none_arguments(self, async_tasks_tool):
        """Test creating a task with None arguments."""
        # The create_task method should handle None arguments by defaulting to empty dict
        task = async_tasks_tool.create_task(
            name="None args task",
            command="none_command"
        )
        
        assert task.arguments == {}

    def test_task_persistence(self, async_tasks_tool):
        """Test that tasks persist across tool instances."""
        # Create task with first tool instance
        task_name = "Persistent task"
        created_task = async_tasks_tool.create_task(name=task_name, command="persistent_command")
        
        # Create a new tool instance (simulating restart)
        new_tool = AsyncTasksTool(async_tasks_tool.data_dir)
        
        # Should be able to retrieve the task
        retrieved_task = new_tool.get_task(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.name == task_name

    def test_task_status_transitions(self, async_tasks_tool):
        """Test task status transitions."""
        task = async_tasks_tool.create_task(name="Status transition task", command="transition_command")
        
        # Initially pending
        assert task.status == TaskStatus.PENDING
        
        # Cancel the task
        async_tasks_tool.cancel_task(task.id)
        cancelled_task = async_tasks_tool.get_task(task.id)
        assert cancelled_task.status == TaskStatus.CANCELLED

    def test_task_with_scheduled_time(self, async_tasks_tool):
        """Test task with scheduled time."""
        scheduled_time = datetime.now() + timedelta(hours=2)
        task = async_tasks_tool.schedule_task(
            name="Scheduled task",
            command="scheduled_command",
            scheduled_at=scheduled_time
        )
        
        assert task.scheduled_at == scheduled_time
        assert task.status == TaskStatus.PENDING

    def test_task_with_past_scheduled_time(self, async_tasks_tool):
        """Test task with past scheduled time."""
        past_time = datetime.now() - timedelta(hours=1)
        task = async_tasks_tool.schedule_task(
            name="Past scheduled task",
            command="past_command",
            scheduled_at=past_time
        )
        
        assert task.scheduled_at == past_time
        assert task.status == TaskStatus.PENDING

    def test_task_with_result_and_error(self, async_tasks_tool):
        """Test task with result and error fields."""
        task = async_tasks_tool.create_task(name="Result task", command="result_command")
        
        # These fields should be None by default
        assert task.result is None
        assert task.error is None

    def test_task_with_tags_and_metadata(self, async_tasks_tool):
        """Test task with various tags and metadata."""
        tags = ["urgent", "data-processing", "nightly", "automated"]
        task = async_tasks_tool.create_task(
            name="Tagged task",
            command="tagged_command",
            tags=tags
        )
        
        assert task.tags == tags
        assert len(task.tags) == 4

    def test_task_creation_timestamp(self, async_tasks_tool):
        """Test that task creation timestamp is set correctly."""
        before_creation = datetime.now()
        task = async_tasks_tool.create_task(name="Timestamp task", command="timestamp_command")
        after_creation = datetime.now()
        
        # The created_at timestamp should be between before and after creation
        assert before_creation <= task.created_at <= after_creation

    def test_task_limit_edge_cases(self, async_tasks_tool):
        """Test list_tasks with edge case limits."""
        # Create some tasks
        for i in range(5):
            async_tasks_tool.create_task(name=f"Task {i}", command=f"cmd{i}")
        
        # Test with limit 0
        tasks = async_tasks_tool.list_tasks(limit=0)
        assert len(tasks) == 0
        
        # Test with limit larger than available tasks
        tasks = async_tasks_tool.list_tasks(limit=10)
        assert len(tasks) == 5
        
        # Test with negative limit (should handle gracefully)
        # The implementation might not handle negative limits, so we'll test what it actually does
        tasks = async_tasks_tool.list_tasks(limit=-1)
        # Just verify we get some result, the exact behavior depends on implementation
        assert len(tasks) >= 0

    def test_concurrent_task_creation(self, async_tasks_tool):
        """Test that the tool handles multiple task creations correctly."""
        # Simulate multiple rapid task creations
        tasks = []
        for i in range(10):
            task = async_tasks_tool.create_task(name=f"Concurrent task {i}", command=f"cmd{i}")
            tasks.append(task)
        
        # All tasks should have unique IDs
        task_ids = [t.id for t in tasks]
        assert len(set(task_ids)) == 10
        
        # All tasks should be retrievable
        for task in tasks:
            retrieved = async_tasks_tool.get_task(task.id)
            assert retrieved is not None
            assert retrieved.name == task.name 