import json
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock
from tools.calendar.calendar import CalendarTool, Event, EventType


class TestCalendarTool:
    """Test suite for CalendarTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def calendar_tool(self, temp_data_dir):
        """Create a CalendarTool instance for testing."""
        return CalendarTool(temp_data_dir)

    @pytest.fixture
    def sample_events(self):
        """Sample events for testing."""
        now = datetime.now()
        return [
            {
                "title": "Team Meeting",
                "description": "Weekly team sync meeting",
                "event_type": EventType.MEETING,
                "start_time": (now + timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=2)).isoformat(),
                "location": "Conference Room A",
                "attendees": ["alice@company.com", "bob@company.com"],
                "tags": ["team", "weekly"]
            },
            {
                "title": "Code Review",
                "description": "Review pull request #123",
                "event_type": EventType.TASK,
                "start_time": (now + timedelta(hours=3)).isoformat(),
                "end_time": (now + timedelta(hours=4)).isoformat(),
                "attendees": ["alice@company.com"],
                "tags": ["code-review", "pr"]
            },
            {
                "title": "Doctor Appointment",
                "description": "Annual checkup",
                "event_type": EventType.APPOINTMENT,
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
                "location": "Medical Center",
                "attendees": ["patient@email.com"],
                "tags": ["health", "annual"]
            }
        ]

    def test_name_property(self, calendar_tool):
        """Test that the tool name is correct."""
        assert calendar_tool.name == "calendar"

    def test_description_property(self, calendar_tool):
        """Test that the tool description is correct."""
        assert calendar_tool.description == "Manage calendar events, meetings, and appointments"

    def test_get_capabilities(self, calendar_tool):
        """Test that all expected capabilities are returned."""
        capabilities = calendar_tool.get_capabilities()
        expected_capabilities = [
            "create_event",
            "list_events",
            "get_event",
            "update_event",
            "delete_event",
            "search_events",
            "get_upcoming_events",
            "get_events_by_date_range"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_events_empty_file(self, calendar_tool):
        """Test reading an empty events file."""
        result = calendar_tool._read_events()
        assert result == []

    def test_read_events_with_data(self, calendar_tool, sample_events):
        """Test reading events from file."""
        # Write some test data
        with open(calendar_tool.data_file, 'w') as f:
            for event_data in sample_events:
                event = Event(**event_data)
                f.write(event.json() + '\n')
        
        result = calendar_tool._read_events()
        assert len(result) == 3
        assert all(isinstance(event, Event) for event in result)

    def test_write_events(self, calendar_tool, sample_events):
        """Test writing events to file."""
        events = [Event(**event_data) for event_data in sample_events]
        calendar_tool._write_events(events)
        
        # Verify the data was written correctly
        with open(calendar_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for i, line in enumerate(lines):
            event = Event(**json.loads(line.strip()))
            assert event.title == sample_events[i]['title']

    def test_create_event_basic(self, calendar_tool):
        """Test creating a basic event."""
        start_time = datetime.now().isoformat()
        event = calendar_tool.create_event(
            title="Test event",
            start_time=start_time,
            description="Test description",
            event_type=EventType.MEETING
        )
        
        assert event.id == 1
        assert event.title == "Test event"
        assert event.description == "Test description"
        assert event.event_type == EventType.MEETING
        # The start_time should be parsed as a datetime object
        assert isinstance(event.start_time, datetime)
        assert event.created_at is not None

    def test_create_event_with_end_time(self, calendar_tool):
        """Test creating an event with end time."""
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() + timedelta(hours=1)).isoformat()
        event = calendar_tool.create_event(
            title="Event with end time",
            start_time=start_time,
            end_time=end_time
        )
        
        # The end_time should be parsed as a datetime object
        assert isinstance(event.end_time, datetime)

    def test_create_event_with_location(self, calendar_tool):
        """Test creating an event with location."""
        start_time = datetime.now().isoformat()
        event = calendar_tool.create_event(
            title="Event with location",
            start_time=start_time,
            location="Conference Room B"
        )
        
        assert event.location == "Conference Room B"

    def test_create_event_with_attendees(self, calendar_tool):
        """Test creating an event with attendees."""
        start_time = datetime.now().isoformat()
        attendees = ["alice@company.com", "bob@company.com"]
        event = calendar_tool.create_event(
            title="Event with attendees",
            start_time=start_time,
            attendees=attendees
        )
        
        assert event.attendees == attendees

    def test_create_event_all_day(self, calendar_tool):
        """Test creating an all-day event."""
        start_time = datetime.now().isoformat()
        event = calendar_tool.create_event(
            title="All-day event",
            start_time=start_time,
            is_all_day=True
        )
        
        assert event.is_all_day is True

    def test_create_event_with_tags(self, calendar_tool):
        """Test creating an event with tags."""
        start_time = datetime.now().isoformat()
        tags = ["important", "project", "deadline"]
        event = calendar_tool.create_event(
            title="Event with tags",
            start_time=start_time,
            tags=tags
        )
        
        assert event.tags == tags

    def test_create_event_id_increment(self, calendar_tool):
        """Test that event IDs increment properly."""
        start_time = datetime.now().isoformat()
        event1 = calendar_tool.create_event(title="First event", start_time=start_time)
        event2 = calendar_tool.create_event(title="Second event", start_time=start_time)
        event3 = calendar_tool.create_event(title="Third event", start_time=start_time)
        
        assert event1.id == 1
        assert event2.id == 2
        assert event3.id == 3

    def test_list_events_all(self, calendar_tool, sample_events):
        """Test listing all events."""
        # Create events
        for event_data in sample_events:
            calendar_tool.create_event(**event_data)
        
        events = calendar_tool.list_events()
        assert len(events) == 3

    def test_list_events_by_type(self, calendar_tool, sample_events):
        """Test listing events filtered by type."""
        # Create events
        for event_data in sample_events:
            calendar_tool.create_event(**event_data)
        
        meetings = calendar_tool.list_events(event_type=EventType.MEETING)
        assert len(meetings) == 1
        assert meetings[0].event_type == EventType.MEETING

    def test_list_events_with_limit(self, calendar_tool, sample_events):
        """Test listing events with limit."""
        # Create events
        for event_data in sample_events:
            calendar_tool.create_event(**event_data)
        
        events = calendar_tool.list_events(limit=2)
        assert len(events) == 2

    def test_get_event(self, calendar_tool):
        """Test getting a specific event."""
        start_time = datetime.now().isoformat()
        created_event = calendar_tool.create_event(title="Test event", start_time=start_time)
        retrieved_event = calendar_tool.get_event(created_event.id)
        
        assert retrieved_event is not None
        assert retrieved_event.id == created_event.id
        assert retrieved_event.title == created_event.title

    def test_get_event_nonexistent(self, calendar_tool):
        """Test getting a non-existent event."""
        result = calendar_tool.get_event(999)
        assert result is None

    def test_update_event(self, calendar_tool):
        """Test updating an event."""
        start_time = datetime.now().isoformat()
        event = calendar_tool.create_event(title="Original title", start_time=start_time)
        
        updated_event = calendar_tool.update_event(
            event_id=event.id,
            title="Updated title",
            description="New description",
            event_type=EventType.APPOINTMENT
        )
        
        assert updated_event.title == "Updated title"
        assert updated_event.description == "New description"
        assert updated_event.event_type == EventType.APPOINTMENT

    def test_update_event_nonexistent(self, calendar_tool):
        """Test updating a non-existent event."""
        result = calendar_tool.update_event(event_id=999, title="New title")
        assert result is None

    def test_delete_event(self, calendar_tool):
        """Test deleting an event."""
        start_time = datetime.now().isoformat()
        event = calendar_tool.create_event(title="Event to delete", start_time=start_time)
        
        # Verify event exists
        assert calendar_tool.get_event(event.id) is not None
        
        # Delete event
        result = calendar_tool.delete_event(event.id)
        assert result is True
        
        # Verify event is gone
        assert calendar_tool.get_event(event.id) is None

    def test_delete_event_nonexistent(self, calendar_tool):
        """Test deleting a non-existent event."""
        result = calendar_tool.delete_event(999)
        assert result is False

    def test_search_events_by_title(self, calendar_tool):
        """Test searching events by title."""
        start_time = datetime.now().isoformat()
        calendar_tool.create_event(title="Python development meeting", start_time=start_time)
        calendar_tool.create_event(title="JavaScript review session", start_time=start_time)
        calendar_tool.create_event(title="Database optimization workshop", start_time=start_time)
        
        results = calendar_tool.search_events("python")
        assert len(results) == 1
        assert "python" in results[0].title.lower()

    def test_search_events_by_description(self, calendar_tool):
        """Test searching events by description."""
        start_time = datetime.now().isoformat()
        calendar_tool.create_event(
            title="Event 1",
            start_time=start_time,
            description="This event involves Python programming"
        )
        calendar_tool.create_event(
            title="Event 2",
            start_time=start_time,
            description="This event involves JavaScript programming"
        )
        
        results = calendar_tool.search_events("python")
        assert len(results) == 1
        assert "python" in results[0].description.lower()

    def test_search_events_case_insensitive(self, calendar_tool):
        """Test that search is case insensitive."""
        start_time = datetime.now().isoformat()
        calendar_tool.create_event(title="PYTHON Development Meeting", start_time=start_time)
        
        results = calendar_tool.search_events("python")
        assert len(results) == 1

    def test_get_upcoming_events(self, calendar_tool):
        """Test getting upcoming events."""
        now = datetime.now()
        
        # Create events in the future
        future_event1 = calendar_tool.create_event(
            title="Future event 1",
            start_time=(now + timedelta(hours=1)).isoformat()
        )
        future_event2 = calendar_tool.create_event(
            title="Future event 2",
            start_time=(now + timedelta(days=2)).isoformat()
        )
        
        # Create event in the past
        calendar_tool.create_event(
            title="Past event",
            start_time=(now - timedelta(hours=1)).isoformat()
        )
        
        upcoming = calendar_tool.get_upcoming_events(days=7)
        assert len(upcoming) == 2
        assert all(event.title.startswith("Future") for event in upcoming)

    def test_get_events_by_date_range(self, calendar_tool):
        """Test getting events by date range."""
        now = datetime.now()
        
        # Create events on different dates
        calendar_tool.create_event(
            title="Today's event",
            start_time=now.isoformat()
        )
        calendar_tool.create_event(
            title="Tomorrow's event",
            start_time=(now + timedelta(days=1)).isoformat()
        )
        calendar_tool.create_event(
            title="Next week's event",
            start_time=(now + timedelta(days=7)).isoformat()
        )
        
        start_date = now.strftime("%Y-%m-%d")
        end_date = (now + timedelta(days=2)).strftime("%Y-%m-%d")
        
        events_in_range = calendar_tool.get_events_by_date_range(start_date, end_date)
        assert len(events_in_range) == 2
        assert all("week" not in event.title for event in events_in_range)

    def test_register_tools(self, calendar_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        mock_mcp.resource.return_value = mock_decorator
        
        calendar_tool.register(mock_mcp)
        
        # Verify tools and resources were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        assert mock_mcp.resource.call_count == 2  # 2 resources
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'calendar_create_event',
            'calendar_list_events',
            'calendar_get_upcoming_events'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, calendar_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "calendar.jsonl"
        assert calendar_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, calendar_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(calendar_tool.data_file, 'w') as f:
            f.write('{"title": "valid event", "start_time": "2024-01-01T10:00:00"}\n')
            f.write('invalid json line\n')
            f.write('{"title": "another valid event", "start_time": "2024-01-01T11:00:00"}\n')
        
        # Should skip invalid lines and return valid ones
        result = calendar_tool._read_events()
        assert len(result) == 2
        assert result[0].title == "valid event"
        assert result[1].title == "another valid event"

    def test_event_model_validation(self):
        """Test Event model validation."""
        # Valid event
        start_time = datetime.now().isoformat()
        event = Event(
            title="Valid event",
            description="Valid description",
            event_type=EventType.MEETING,
            start_time=start_time
        )
        assert event.title == "Valid event"
        assert event.event_type == EventType.MEETING

    def test_event_default_values(self):
        """Test Event model default values."""
        start_time = datetime.now().isoformat()
        event = Event(title="Test event", start_time=start_time)
        
        assert event.event_type == EventType.OTHER
        assert event.attendees == []
        assert event.is_all_day is False
        assert event.tags == []
        assert event.created_at is not None
        assert event.end_time is None
        assert event.location is None

    def test_event_type_enum(self):
        """Test EventType enum values."""
        assert EventType.MEETING == "meeting"
        assert EventType.TASK == "task"
        assert EventType.REMINDER == "reminder"
        assert EventType.APPOINTMENT == "appointment"
        assert EventType.OTHER == "other"

    def test_datetime_parsing(self, calendar_tool):
        """Test datetime parsing in events."""
        start_time = "2024-01-01T10:00:00"
        end_time = "2024-01-01T11:00:00"
        
        event = calendar_tool.create_event(
            title="Test datetime parsing",
            start_time=start_time,
            end_time=end_time
        )
        
        # The times should be parsed as datetime objects
        assert isinstance(event.start_time, datetime)
        assert isinstance(event.end_time, datetime)

    def test_invalid_datetime_format(self, calendar_tool):
        """Test handling of invalid datetime format."""
        # This should raise a validation error for invalid datetime
        start_time = "invalid-datetime"
        with pytest.raises(Exception):  # Should raise some kind of validation error
            calendar_tool.create_event(
                title="Test invalid datetime",
                start_time=start_time
            ) 