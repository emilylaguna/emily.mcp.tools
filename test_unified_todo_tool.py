"""
Tests for Unified Todo Tool
Phase 3.2: Advanced Todo Tool Testing
"""

import pytest
import tempfile
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from core import create_test_memory_store, UnifiedMemoryStore
from tools.todo.unified_todo_tool import UnifiedTodoTool, Priority, Status, EnergyLevel
from models import MemoryEntity, MemoryRelation


class TestUnifiedTodoTool:
    """Test suite for UnifiedTodoTool with advanced features."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_store(self, temp_dir):
        """Create test memory store."""
        db_path = temp_dir / "test_memory.db"
        return UnifiedMemoryStore(db_path, enable_vector_search=False, enable_ai_extraction=False)
    
    @pytest.fixture
    def todo_tool(self, memory_store):
        """Create unified todo tool instance."""
        return UnifiedTodoTool(memory_store)
    
    @pytest.fixture
    def sample_area(self, todo_tool):
        """Create a sample area for testing."""
        return todo_tool.create_area(
            name="Work",
            description="Work-related tasks and projects",
            color="#007AFF"
        )
    
    @pytest.fixture
    def sample_project(self, todo_tool, sample_area):
        """Create a sample project for testing."""
        return todo_tool.create_project(
            name="API Redesign",
            area_id=sample_area.id,
            description="Redesign the API for better performance",
            deadline="2024-02-15"
        )
    
    @pytest.fixture
    def sample_task(self, todo_tool, sample_project):
        """Create a sample task for testing."""
        return todo_tool.create_task(
            title="Review API documentation",
            description="Go through the current API docs",
            project_id=sample_project.id,
            priority="high",
            energy_level="medium",
            time_estimate=60
        )

    def test_create_area(self, todo_tool):
        """Test area creation."""
        area = todo_tool.create_area(
            name="Personal",
            description="Personal tasks and projects",
            color="#FF3B30"
        )
        
        assert area.id is not None
        assert area.name == "Personal"
        assert area.content == "Personal tasks and projects"
        assert area.type == "area"
        assert area.metadata["status"] == "active"
        assert area.metadata["color"] == "#FF3B30"
    
    def test_get_areas(self, todo_tool, sample_area):
        """Test retrieving areas."""
        areas = todo_tool.get_areas()
        assert len(areas) == 1
        assert areas[0].id == sample_area.id
        assert areas[0].name == "Work"
    
    def test_update_area(self, todo_tool, sample_area):
        """Test updating area properties."""
        updated_area = todo_tool.update_area(
            sample_area.id,
            name="Updated Work",
            description="Updated description"
        )
        
        assert updated_area.name == "Updated Work"
        assert updated_area.content == "Updated description"
    
    def test_archive_area(self, todo_tool, sample_area, sample_project):
        """Test archiving an area."""
        success = todo_tool.archive_area(sample_area.id)
        assert success is True
        
        # Check area is archived
        archived_areas = todo_tool.get_areas(status="archived")
        assert len(archived_areas) == 1
        assert archived_areas[0].id == sample_area.id
        
        # Check project is on hold
        projects = todo_tool.get_projects(status="on_hold")
        assert len(projects) == 1
        assert projects[0].id == sample_project.id
    
    def test_create_project(self, todo_tool, sample_area):
        """Test project creation."""
        project = todo_tool.create_project(
            name="Website Redesign",
            area_id=sample_area.id,
            description="Redesign the company website",
            deadline="2024-03-01"
        )
        
        assert project.id is not None
        assert project.name == "Website Redesign"
        assert project.type == "project"
        assert project.metadata["area_id"] == sample_area.id
        assert project.metadata["status"] == "active"
        assert project.metadata["deadline"] == "2024-03-01"
        assert project.metadata["progress"] == 0.0
    
    def test_get_projects(self, todo_tool, sample_area, sample_project):
        """Test retrieving projects."""
        projects = todo_tool.get_projects(area_id=sample_area.id)
        assert len(projects) == 1
        assert projects[0].id == sample_project.id
        
        # Test filtering by status
        active_projects = todo_tool.get_projects(status="active")
        assert len(active_projects) == 1
        assert active_projects[0].id == sample_project.id
    
    def test_complete_project(self, todo_tool, sample_project, sample_task):
        """Test completing a project."""
        result = todo_tool.complete_project(sample_project.id)
        
        assert result["project_id"] == sample_project.id
        assert result["project_name"] == "API Redesign"
        assert result["total_tasks"] == 1
        assert result["completed_tasks"] == 1
        
        # Check project status
        project = todo_tool.memory.get_entity(sample_project.id)
        assert project.metadata["status"] == "completed"
        
        # Check task status
        task = todo_tool.memory.get_entity(sample_task.id)
        assert task.metadata["status"] == "completed"
    
    def test_get_project_progress(self, todo_tool, sample_project, sample_task):
        """Test getting project progress."""
        progress = todo_tool.get_project_progress(sample_project.id)
        
        assert progress["project_id"] == sample_project.id
        assert progress["project_name"] == "API Redesign"
        assert progress["total_tasks"] == 1
        assert progress["completed_tasks"] == 0
        assert progress["in_progress_tasks"] == 0
        assert progress["todo_tasks"] == 1
        assert progress["progress_percentage"] == 0.0
    
    def test_create_task(self, todo_tool, sample_project):
        """Test task creation with advanced features."""
        task = todo_tool.create_task(
            title="Write API tests",
            description="Create comprehensive test suite",
            project_id=sample_project.id,
            priority="high",
            scheduled_date="2024-01-15",
            due_date="2024-01-20",
            energy_level="high",
            time_estimate=120,
            tags=["testing", "api"]
        )
        
        assert task.id is not None
        assert task.name == "Write API tests"
        assert task.type == "task"
        assert task.metadata["project_id"] == sample_project.id
        assert task.metadata["priority"] == "high"
        assert task.metadata["scheduled_date"] == "2024-01-15"
        assert task.metadata["due_date"] == "2024-01-20"
        assert task.metadata["energy_level"] == "high"
        assert task.metadata["time_estimate"] == 120
        assert task.metadata["status"] == "todo"
        assert "testing" in task.tags
        assert "api" in task.tags
    
    def test_update_task(self, todo_tool, sample_task):
        """Test updating task properties."""
        updated_task = todo_tool.update_task(
            sample_task.id,
            priority="urgent",
            status="in_progress",
            time_estimate=90
        )
        
        assert updated_task.metadata["priority"] == "urgent"
        assert updated_task.metadata["status"] == "in_progress"
        assert updated_task.metadata["time_estimate"] == 90
    
    def test_complete_task(self, todo_tool, sample_task):
        """Test completing a task."""
        completed_task = todo_tool.complete_task(sample_task.id)
        
        assert completed_task.metadata["status"] == "completed"
        assert "completed_at" in completed_task.metadata
    
    def test_delete_task(self, todo_tool, sample_task):
        """Test deleting a task."""
        success = todo_tool.delete_task(sample_task.id)
        assert success is True
        
        # Verify task is deleted
        task = todo_tool.memory.get_entity(sample_task.id)
        assert task is None
    
    def test_get_today_tasks(self, todo_tool, sample_task):
        """Test getting today's tasks with AI suggestions."""
        # Schedule task for today
        today = datetime.now().strftime("%Y-%m-%d")
        todo_tool.update_task(sample_task.id, scheduled_date=today)
        
        today_tasks = todo_tool.get_today_tasks()
        
        assert "scheduled" in today_tasks
        assert "overdue" in today_tasks
        assert "suggested" in today_tasks
        assert "calendar_events" in today_tasks
        assert "evening" in today_tasks
        
        # Check scheduled task is included
        scheduled_ids = [task.id for task in today_tasks["scheduled"]]
        assert sample_task.id in scheduled_ids
    
    def test_get_evening_tasks(self, todo_tool):
        """Test getting evening tasks."""
        # Create low-energy task
        evening_task = todo_tool.create_task(
            title="Read documentation",
            energy_level="low",
            tags=["reading"]
        )
        
        evening_tasks = todo_tool.get_evening_tasks()
        evening_task_ids = [task.id for task in evening_tasks]
        assert evening_task.id in evening_task_ids
    
    def test_get_upcoming_tasks(self, todo_tool, sample_task):
        """Test getting upcoming tasks."""
        # Schedule task for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        todo_tool.update_task(sample_task.id, scheduled_date=tomorrow)
        
        upcoming = todo_tool.get_upcoming_tasks(days=7)
        
        assert len(upcoming) == 7
        assert tomorrow in upcoming
        
        day_data = upcoming[tomorrow]
        assert "scheduled_tasks" in day_data
        assert "due_tasks" in day_data
        assert "project_deadlines" in day_data
        assert "calendar_events" in day_data
        assert "suggestions" in day_data
        assert "workload_score" in day_data
    
    def test_get_anytime_tasks(self, todo_tool, sample_task):
        """Test getting anytime tasks."""
        anytime_tasks = todo_tool.get_anytime_tasks()
        anytime_task_ids = [task.id for task in anytime_tasks]
        assert sample_task.id in anytime_task_ids
    
    def test_get_someday_tasks(self, todo_tool):
        """Test getting someday tasks."""
        # Create someday task
        someday_task = todo_tool.create_task(
            title="Learn new framework",
            priority="low",
            tags=["someday"]
        )
        
        someday_tasks = todo_tool.get_someday_tasks()
        someday_task_ids = [task.id for task in someday_tasks]
        assert someday_task.id in someday_task_ids
    
    def test_create_task_with_natural_language(self, todo_tool):
        """Test creating task from natural language."""
        task = todo_tool.create_task_with_natural_language(
            "Call Alice about the API design tomorrow #urgent #work"
        )
        
        assert task.name == "Call Alice about the API design"
        assert task.metadata["priority"] == "high"  # From #urgent
        assert "work" in task.tags
        assert "urgent" in task.tags
        
        # Check date parsing
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert task.metadata["scheduled_date"] == tomorrow
    
    def test_create_task_from_conversation(self, todo_tool, memory_store):
        """Test creating task from conversation context."""
        # Create a handoff context
        context = MemoryEntity(
            id=str(uuid.uuid4()),
            name="API Discussion",
            content="We need to redesign the API for better performance. This is urgent.",
            type="handoff",
            tags=["api", "urgent"]
        )
        context = memory_store.save_entity(context)
        
        task = todo_tool.create_task_from_conversation(context.id)
        
        # The task name should either start with "Follow up on:" or be an extracted action item
        assert (task.name.startswith("Follow up on:") or 
                "redesign" in task.name.lower() or 
                "api" in task.name.lower())
        assert task.metadata["source_context"] == context.id
        assert task.metadata["auto_created"] is True
        
        # Check relation was created
        relations = memory_store.get_related(task.id)
        assert len(relations) > 0
    
    def test_get_project_timeline(self, todo_tool, sample_project, sample_task):
        """Test getting project timeline."""
        timeline = todo_tool.get_project_timeline(sample_project.id)
        
        assert len(timeline) >= 1  # At least the task
        
        # Find the task in timeline
        task_events = [event for event in timeline if event["type"] == "task"]
        assert len(task_events) == 1
        assert task_events[0]["title"] == "Review API documentation"
    
    def test_suggest_task_priorities(self, todo_tool, sample_task):
        """Test AI task priority suggestions."""
        suggestions = todo_tool.suggest_task_priorities()
        
        assert isinstance(suggestions, list)
        # Should suggest the high priority task
        task_suggestions = [s for s in suggestions if s.get("task_id") == sample_task.id]
        assert len(task_suggestions) > 0
    
    def test_quick_find(self, todo_tool, sample_area, sample_project, sample_task):
        """Test quick find functionality."""
        results = todo_tool.quick_find("API")
        
        assert "tasks" in results
        assert "projects" in results
        assert "areas" in results
        
        # Should find the API-related task and project
        task_ids = [task["id"] for task in results["tasks"]]
        project_ids = [project["id"] for project in results["projects"]]
        
        assert sample_task.id in task_ids
        assert sample_project.id in project_ids
    
    def test_parse_natural_date(self, todo_tool):
        """Test natural language date parsing."""
        # Test direct mappings
        today = todo_tool.parse_natural_date("today")
        tomorrow = todo_tool.parse_natural_date("tomorrow")
        
        assert today.date() == datetime.now().date()
        assert tomorrow.date() == (datetime.now() + timedelta(days=1)).date()
        
        # Test weekday parsing
        next_monday = todo_tool.parse_natural_date("monday")
        assert next_monday is not None
        assert next_monday.weekday() == 0  # Monday
    
    def test_get_overdue_tasks(self, todo_tool):
        """Test getting overdue tasks."""
        # Create overdue task
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        overdue_task = todo_tool.create_task(
            title="Overdue task",
            due_date=yesterday
        )
        
        overdue_tasks = todo_tool._get_overdue_tasks()
        overdue_task_ids = [task.id for task in overdue_tasks]
        assert overdue_task.id in overdue_task_ids
    
    def test_analyze_conversation_urgency(self, todo_tool):
        """Test conversation urgency analysis."""
        urgent_text = "This is urgent and needs immediate attention"
        high_text = "This is important and needs priority"
        normal_text = "This is a regular update"
        
        assert todo_tool._analyze_conversation_urgency(urgent_text) == "high"
        assert todo_tool._analyze_conversation_urgency(high_text) == "medium"
        assert todo_tool._analyze_conversation_urgency(normal_text) == "low"
    
    def test_detect_project_from_tags(self, todo_tool, sample_project):
        """Test project detection from tags."""
        # Add tag to project
        todo_tool.memory.update_entity(sample_project)
        
        project_id = todo_tool._detect_project_from_tags(["api"])
        assert project_id == sample_project.id
    
    def test_detect_area_from_tags(self, todo_tool, sample_area):
        """Test area detection from tags."""
        # Add tag to area
        todo_tool.memory.update_entity(sample_area)
        
        area_id = todo_tool._detect_area_from_tags(["work"])
        assert area_id == sample_area.id
    
    def test_calculate_workload_score(self, todo_tool):
        """Test workload score calculation."""
        # Create tasks with time estimates
        task1 = todo_tool.create_task(title="Task 1", time_estimate=30)
        task2 = todo_tool.create_task(title="Task 2", time_estimate=60)
        
        tasks = [task1, task2]
        score = todo_tool._calculate_workload_score(tasks)
        
        # 90 minutes = 1.5 hours, should be capped at 10
        assert score == 1.5
    
    def test_get_projects_with_approaching_deadlines(self, todo_tool, sample_project):
        """Test getting projects with approaching deadlines."""
        # Set deadline to tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        todo_tool.update_project(sample_project.id, deadline=tomorrow)
        
        urgent_projects = todo_tool._get_projects_with_approaching_deadlines()
        project_ids = [project.id for project in urgent_projects]
        assert sample_project.id in project_ids
    
    def test_create_repeat_task(self, todo_tool):
        """Test creating repeat tasks."""
        # Create task with daily repeat
        original_task = todo_tool.create_task(
            title="Daily standup",
            repeat_pattern="daily"
        )
        
        # Complete the task
        completed_task = todo_tool.complete_task(original_task.id)
        
                # Check that a new task was created for tomorrow
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_tasks = todo_tool.memory.search_entities("task")
        tomorrow_tasks = [task for task in tomorrow_tasks if task.metadata.get("scheduled_date") == tomorrow]
    
        assert len(tomorrow_tasks) == 1
        assert tomorrow_tasks[0].name == "Daily standup"
    
    def test_error_handling(self, todo_tool):
        """Test error handling for invalid operations."""
        # Test updating non-existent task
        with pytest.raises(ValueError, match="Task.*not found"):
            todo_tool.update_task("non-existent-id", priority="high")
        
        # Test completing non-existent project
        with pytest.raises(ValueError, match="Project.*not found"):
            todo_tool.complete_project("non-existent-id")
        
        # Test creating task from non-existent conversation
        with pytest.raises(ValueError, match="Context.*not found"):
            todo_tool.create_task_from_conversation("non-existent-id")
    
    def test_comprehensive_workflow(self, todo_tool):
        """Test a comprehensive todo workflow."""
        # 1. Create area
        work_area = todo_tool.create_area("Work", color="#007AFF")
        
        # 2. Create project
        project = todo_tool.create_project(
            "Website Launch",
            area_id=work_area.id,
            deadline="2024-02-01"
        )
        
        # 3. Create tasks
        task1 = todo_tool.create_task(
            title="Design homepage",
            project_id=project.id,
            priority="high",
            scheduled_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        task2 = todo_tool.create_task(
            title="Write content",
            project_id=project.id,
            priority="medium",
            energy_level="low"
        )
        
        # 4. Check today's tasks
        today_tasks = todo_tool.get_today_tasks()
        assert len(today_tasks["scheduled"]) >= 1
        
        # 5. Complete a task
        completed_task = todo_tool.complete_task(task1.id)
        assert completed_task.metadata["status"] == "completed"
        
        # 6. Check project progress
        progress = todo_tool.get_project_progress(project.id)
        assert progress["completed_tasks"] == 1
        assert progress["progress_percentage"] == 50.0
        
        # 7. Complete project
        result = todo_tool.complete_project(project.id)
        assert result["completed_tasks"] == 1
        
        # 8. Check final state
        project_entity = todo_tool.memory.get_entity(project.id)
        assert project_entity.metadata["status"] == "completed"
        
        task2_entity = todo_tool.memory.get_entity(task2.id)
        assert task2_entity.metadata["status"] == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 