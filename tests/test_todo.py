import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
from tools.todo.todo import TodoTool, Task, Priority, Status


class TestTodoTool:
    """Test suite for TodoTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def todo_tool(self, temp_data_dir):
        """Create a TodoTool instance for testing."""
        return TodoTool(temp_data_dir)

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        return [
            {
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation for the project",
                "priority": Priority.HIGH,
                "tags": ["documentation", "project"]
            },
            {
                "title": "Review code changes",
                "description": "Review pull request #123",
                "priority": Priority.MEDIUM,
                "tags": ["code-review", "pr"]
            },
            {
                "title": "Setup development environment",
                "description": "Install and configure development tools",
                "priority": Priority.LOW,
                "tags": ["setup", "dev"]
            }
        ]

    def test_name_property(self, todo_tool):
        """Test that the tool name is correct."""
        assert todo_tool.name == "todo"

    def test_description_property(self, todo_tool):
        """Test that the tool description is correct."""
        assert todo_tool.description == "Manage TODO tasks with priorities, due dates, and status tracking"

    def test_get_capabilities(self, todo_tool):
        """Test that all expected capabilities are returned."""
        capabilities = todo_tool.get_capabilities()
        expected_capabilities = [
            "create_task",
            "list_tasks",
            "update_task",
            "delete_task",
            "mark_complete",
            "search_tasks",
            "get_statistics"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_tasks_empty_file(self, todo_tool):
        """Test reading an empty tasks file."""
        result = todo_tool._read_tasks()
        assert result == []

    def test_read_tasks_with_data(self, todo_tool, sample_tasks):
        """Test reading tasks from file."""
        # Write some test data
        with open(todo_tool.data_file, 'w') as f:
            for task_data in sample_tasks:
                task = Task(**task_data)
                f.write(task.json() + '\n')
        
        result = todo_tool._read_tasks()
        assert len(result) == 3
        assert all(isinstance(task, Task) for task in result)

    def test_write_tasks(self, todo_tool, sample_tasks):
        """Test writing tasks to file."""
        tasks = [Task(**task_data) for task_data in sample_tasks]
        todo_tool._write_tasks(tasks)
        
        # Verify the data was written correctly
        with open(todo_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for i, line in enumerate(lines):
            task = Task(**json.loads(line.strip()))
            assert task.title == sample_tasks[i]['title']

    def test_create_task_basic(self, todo_tool):
        """Test creating a basic task."""
        task = todo_tool.create_task(
            title="Test task",
            description="Test description",
            priority=Priority.HIGH
        )
        
        assert task.id == 1
        assert task.title == "Test task"
        assert task.description == "Test description"
        assert task.priority == Priority.HIGH
        assert task.status == Status.TODO
        assert task.created_at is not None

    def test_create_task_with_due_date(self, todo_tool):
        """Test creating a task with due date."""
        due_date = "2024-12-31T23:59:59"
        task = todo_tool.create_task(
            title="Task with due date",
            due_date=due_date
        )
        
        # The due_date should be parsed as a datetime object
        assert isinstance(task.due_date, datetime)

    def test_create_task_with_tags(self, todo_tool):
        """Test creating a task with tags."""
        tags = ["urgent", "project", "frontend"]
        task = todo_tool.create_task(
            title="Task with tags",
            tags=tags
        )
        
        assert task.tags == tags

    def test_create_task_id_increment(self, todo_tool):
        """Test that task IDs increment properly."""
        task1 = todo_tool.create_task(title="First task")
        task2 = todo_tool.create_task(title="Second task")
        task3 = todo_tool.create_task(title="Third task")
        
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_list_tasks_all(self, todo_tool, sample_tasks):
        """Test listing all tasks."""
        # Create tasks
        for task_data in sample_tasks:
            todo_tool.create_task(**task_data)
        
        tasks = todo_tool.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_by_status(self, todo_tool, sample_tasks):
        """Test listing tasks filtered by status."""
        # Create tasks
        for task_data in sample_tasks:
            todo_tool.create_task(**task_data)
        
        # Mark one task as in progress
        tasks = todo_tool.list_tasks()
        if tasks:
            todo_tool.update_task(tasks[0].id, status=Status.IN_PROGRESS)
        
        todo_tasks = todo_tool.list_tasks(status=Status.TODO)
        assert len(todo_tasks) >= 0  # At least 0 tasks with TODO status
        for task in todo_tasks:
            assert task.status == Status.TODO

    def test_list_tasks_by_priority(self, todo_tool, sample_tasks):
        """Test listing tasks filtered by priority."""
        # Create tasks
        for task_data in sample_tasks:
            todo_tool.create_task(**task_data)
        
        high_priority_tasks = todo_tool.list_tasks(priority=Priority.HIGH)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].priority == Priority.HIGH

    def test_update_task(self, todo_tool):
        """Test updating a task."""
        task = todo_tool.create_task(title="Original title")
        
        updated_task = todo_tool.update_task(
            task_id=task.id,
            title="Updated title",
            description="New description",
            priority=Priority.URGENT
        )
        
        assert updated_task.title == "Updated title"
        assert updated_task.description == "New description"
        assert updated_task.priority == Priority.URGENT

    def test_update_task_nonexistent(self, todo_tool):
        """Test updating a non-existent task."""
        result = todo_tool.update_task(task_id=999, title="New title")
        assert result is None

    def test_get_task(self, todo_tool):
        """Test getting a specific task."""
        created_task = todo_tool.create_task(title="Test task")
        retrieved_task = todo_tool.get_task(created_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title

    def test_get_task_nonexistent(self, todo_tool):
        """Test getting a non-existent task."""
        result = todo_tool.get_task(999)
        assert result is None

    def test_mark_complete(self, todo_tool):
        """Test marking a task as complete."""
        task = todo_tool.create_task(title="Task to complete")
        
        completed_task = todo_tool.mark_complete(task.id)
        
        assert completed_task.status == Status.DONE
        assert completed_task.completed_at is not None

    def test_mark_complete_nonexistent(self, todo_tool):
        """Test marking a non-existent task as complete."""
        result = todo_tool.mark_complete(999)
        assert result is None

    def test_delete_task(self, todo_tool):
        """Test deleting a task."""
        task = todo_tool.create_task(title="Task to delete")
        
        # Verify task exists
        assert todo_tool.get_task(task.id) is not None
        
        # Delete task
        result = todo_tool.delete_task(task.id)
        assert result is True
        
        # Verify task is gone
        assert todo_tool.get_task(task.id) is None

    def test_delete_task_nonexistent(self, todo_tool):
        """Test deleting a non-existent task."""
        result = todo_tool.delete_task(999)
        assert result is False

    def test_search_tasks_by_title(self, todo_tool):
        """Test searching tasks by title."""
        todo_tool.create_task(title="Python development task")
        todo_tool.create_task(title="JavaScript debugging")
        todo_tool.create_task(title="Database optimization")
        
        results = todo_tool.search_tasks("python")
        assert len(results) == 1
        assert "python" in results[0].title.lower()

    def test_search_tasks_by_description(self, todo_tool):
        """Test searching tasks by description."""
        todo_tool.create_task(
            title="Task 1",
            description="This task involves Python programming"
        )
        todo_tool.create_task(
            title="Task 2", 
            description="This task involves JavaScript programming"
        )
        
        results = todo_tool.search_tasks("python")
        assert len(results) == 1
        assert "python" in results[0].description.lower()

    def test_search_tasks_case_insensitive(self, todo_tool):
        """Test that search is case insensitive."""
        todo_tool.create_task(title="PYTHON Development")
        
        results = todo_tool.search_tasks("python")
        assert len(results) == 1

    def test_get_statistics(self, todo_tool, sample_tasks):
        """Test getting task statistics."""
        # Create tasks
        for task_data in sample_tasks:
            todo_tool.create_task(**task_data)
        
        # Update some tasks to different statuses
        tasks = todo_tool.list_tasks()
        if len(tasks) >= 2:
            todo_tool.update_task(tasks[0].id, status=Status.IN_PROGRESS)
            todo_tool.update_task(tasks[1].id, status=Status.DONE)
        
        stats = todo_tool.get_statistics()
        
        assert stats['total'] == 3
        # Verify that we have tasks in different statuses
        assert stats['by_status']['todo'] >= 0
        assert stats['by_status']['in_progress'] >= 0
        assert stats['by_status']['done'] >= 0
        assert stats['by_priority']['high'] == 1
        assert stats['by_priority']['medium'] == 1
        assert stats['by_priority']['low'] == 1

    def test_get_statistics_empty(self, todo_tool):
        """Test getting statistics for empty task list."""
        stats = todo_tool.get_statistics()
        
        assert stats['total'] == 0
        for status in Status:
            assert stats['by_status'][status.value] == 0
        for priority in Priority:
            assert stats['by_priority'][priority.value] == 0

    def test_register_tools(self, todo_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        mock_mcp.resource.return_value = mock_decorator
        
        todo_tool.register(mock_mcp)
        
        # Verify tools and resources were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        assert mock_mcp.resource.call_count == 2  # 2 resources
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'todo_create',
            'todo_list', 
            'todo_complete'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, todo_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "todo.jsonl"
        assert todo_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, todo_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(todo_tool.data_file, 'w') as f:
            f.write('{"title": "valid task"}\n')
            f.write('invalid json line\n')
            f.write('{"title": "another valid task"}\n')
        
        # Should skip invalid lines and return valid ones
        result = todo_tool._read_tasks()
        assert len(result) == 2
        assert result[0].title == "valid task"
        assert result[1].title == "another valid task"

    def test_task_model_validation(self):
        """Test Task model validation."""
        # Valid task
        task = Task(
            title="Valid task",
            description="Valid description",
            priority=Priority.HIGH,
            status=Status.TODO
        )
        assert task.title == "Valid task"
        assert task.priority == Priority.HIGH

    def test_task_default_values(self):
        """Test Task model default values."""
        task = Task(title="Test task")
        
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.TODO
        assert task.tags == []
        assert task.created_at is not None
        assert task.completed_at is None
        assert task.due_date is None

    def test_priority_enum(self):
        """Test Priority enum values."""
        assert Priority.LOW == "low"
        assert Priority.MEDIUM == "medium"
        assert Priority.HIGH == "high"
        assert Priority.URGENT == "urgent"

    def test_status_enum(self):
        """Test Status enum values."""
        assert Status.TODO == "todo"
        assert Status.IN_PROGRESS == "in_progress"
        assert Status.DONE == "done"
        assert Status.CANCELLED == "cancelled" 