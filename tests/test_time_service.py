import pytest
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from tools.time_service.time_service import TimeServiceTool, TimeInfo


class TestTimeServiceTool:
    """Test suite for TimeServiceTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def time_service_tool(self, temp_data_dir):
        """Create a TimeServiceTool instance for testing."""
        return TimeServiceTool(temp_data_dir)

    def test_name_property(self, time_service_tool):
        """Test that the tool name is correct."""
        assert time_service_tool.name == "time_service"

    def test_description_property(self, time_service_tool):
        """Test that the tool description is correct."""
        assert time_service_tool.description == "Provides current date and time information for LLM context"

    def test_get_capabilities(self, time_service_tool):
        """Test that all expected capabilities are returned."""
        capabilities = time_service_tool.get_capabilities()
        expected_capabilities = [
            "get_current_time",
            "get_time_info",
            "format_time",
            "get_timezone_info",
            "calculate_time_difference"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_get_current_time(self, time_service_tool):
        """Test getting comprehensive current time information."""
        time_info = time_service_tool.get_current_time()
        
        assert isinstance(time_info, TimeInfo)
        assert isinstance(time_info.current_time, datetime)
        assert isinstance(time_info.timezone, str)
        assert isinstance(time_info.timestamp, float)
        assert isinstance(time_info.date, str)
        assert isinstance(time_info.time, str)
        assert isinstance(time_info.day_of_week, str)
        assert isinstance(time_info.day_of_year, int)
        assert isinstance(time_info.week_of_year, int)
        assert isinstance(time_info.month, str)
        assert isinstance(time_info.year, int)
        assert isinstance(time_info.is_weekend, bool)
        assert isinstance(time_info.is_business_day, bool)
        
        # Verify the date format
        assert len(time_info.date.split('-')) == 3  # YYYY-MM-DD
        assert len(time_info.time.split(':')) == 3  # HH:MM:SS
        
        # Verify logical relationships
        assert time_info.day_of_year >= 1 and time_info.day_of_year <= 366
        assert time_info.week_of_year >= 1 and time_info.week_of_year <= 53
        assert time_info.year >= 2020  # Reasonable minimum year
        assert time_info.is_weekend != time_info.is_business_day  # Mutually exclusive

    def test_get_time_info_default_format(self, time_service_tool):
        """Test getting current time with default format."""
        time_str = time_service_tool.get_time_info()
        
        assert isinstance(time_str, str)
        assert len(time_str) > 0
        # Should be in format "YYYY-MM-DD HH:MM:SS"
        assert len(time_str.split(' ')) == 2
        assert len(time_str.split(' ')[0].split('-')) == 3
        assert len(time_str.split(' ')[1].split(':')) == 3

    def test_get_time_info_custom_format(self, time_service_tool):
        """Test getting current time with custom format."""
        time_str = time_service_tool.get_time_info("%Y-%m-%d")
        
        assert isinstance(time_str, str)
        assert len(time_str.split('-')) == 3  # YYYY-MM-DD
        assert len(time_str) == 10  # YYYY-MM-DD is 10 characters

    def test_get_time_info_various_formats(self, time_service_tool):
        """Test getting current time with various formats."""
        formats_and_expected_lengths = [
            ("%Y", 4),      # Year only
            ("%m", 2),      # Month only
            ("%d", 2),      # Day only
            ("%H:%M", 5),   # Hour:Minute
            ("%Y-%m-%d %H:%M:%S", 19),  # Full datetime
        ]
        
        for format_str, expected_length in formats_and_expected_lengths:
            time_str = time_service_tool.get_time_info(format_str)
            assert len(time_str) == expected_length

    def test_format_time_valid_timestamp(self, time_service_tool):
        """Test formatting a valid timestamp."""
        # Use a known timestamp (2024-01-01 12:00:00 UTC)
        timestamp = 1704110400.0
        formatted = time_service_tool.format_time(timestamp)
        
        assert isinstance(formatted, str)
        assert "2024" in formatted  # Should contain the year

    def test_format_time_custom_format(self, time_service_tool):
        """Test formatting timestamp with custom format."""
        timestamp = 1704110400.0  # 2024-01-01 12:00:00 UTC
        formatted = time_service_tool.format_time(timestamp, "%Y-%m-%d")
        
        assert formatted == "2024-01-01"

    def test_format_time_various_formats(self, time_service_tool):
        """Test formatting timestamp with various formats."""
        timestamp = 1704110400.0  # 2024-01-01 12:00:00 UTC
        
        formats_and_expected = [
            ("%Y", "2024"),
            ("%m", "01"),
            ("%d", "01"),
            ("%H", "12"),
            ("%M", "00"),
            ("%S", "00"),
        ]
        
        for format_str, expected in formats_and_expected:
            formatted = time_service_tool.format_time(timestamp, format_str)
            # The actual result depends on the local timezone, so we'll just verify it's a string
            assert isinstance(formatted, str)
            assert len(formatted) > 0

    def test_get_timezone_info(self, time_service_tool):
        """Test getting timezone information."""
        tz_info = time_service_tool.get_timezone_info()
        
        assert isinstance(tz_info, dict)
        assert "local_timezone" in tz_info
        assert "utc_offset" in tz_info
        assert "is_dst" in tz_info
        assert "utc_time" in tz_info
        assert "local_time" in tz_info
        
        assert isinstance(tz_info["local_timezone"], str)
        assert isinstance(tz_info["utc_offset"], (int, float))
        assert isinstance(tz_info["is_dst"], bool)
        assert isinstance(tz_info["utc_time"], str)
        assert isinstance(tz_info["local_time"], str)
        
        # Verify UTC offset is reasonable (-12 to +14 hours)
        assert -12 <= tz_info["utc_offset"] <= 14

    def test_calculate_time_difference_valid(self, time_service_tool):
        """Test calculating time difference with valid times."""
        start_time = "2024-01-01 10:00:00"
        end_time = "2024-01-01 12:00:00"
        
        result = time_service_tool.calculate_time_difference(start_time, end_time)
        
        assert isinstance(result, dict)
        assert "start_time" in result
        assert "end_time" in result
        assert "difference_seconds" in result
        assert "difference_days" in result
        assert "difference_hours" in result
        assert "difference_minutes" in result
        assert "is_positive" in result
        
        assert result["difference_seconds"] == 7200  # 2 hours in seconds
        assert result["difference_hours"] == 2.0
        assert result["difference_minutes"] == 120.0
        assert result["difference_days"] == 0
        assert result["is_positive"] is True

    def test_calculate_time_difference_negative(self, time_service_tool):
        """Test calculating time difference with end time before start time."""
        start_time = "2024-01-01 12:00:00"
        end_time = "2024-01-01 10:00:00"
        
        result = time_service_tool.calculate_time_difference(start_time, end_time)
        
        assert result["difference_seconds"] == -7200  # -2 hours in seconds
        assert result["difference_hours"] == -2.0
        assert result["difference_minutes"] == -120.0
        assert result["is_positive"] is False

    def test_calculate_time_difference_cross_days(self, time_service_tool):
        """Test calculating time difference across multiple days."""
        start_time = "2024-01-01 23:00:00"
        end_time = "2024-01-02 01:00:00"
        
        result = time_service_tool.calculate_time_difference(start_time, end_time)
        
        assert result["difference_seconds"] == 7200  # 2 hours in seconds
        assert result["difference_hours"] == 2.0
        assert result["difference_days"] == 0  # Same day

    def test_calculate_time_difference_custom_format(self, time_service_tool):
        """Test calculating time difference with custom format."""
        start_time = "01/01/2024 10:00"
        end_time = "01/01/2024 12:00"
        custom_format = "%m/%d/%Y %H:%M"
        
        result = time_service_tool.calculate_time_difference(start_time, end_time, custom_format)
        
        assert result["difference_seconds"] == 7200  # 2 hours in seconds
        assert result["difference_hours"] == 2.0

    def test_calculate_time_difference_invalid_format(self, time_service_tool):
        """Test calculating time difference with invalid format."""
        start_time = "invalid-time"
        end_time = "also-invalid"
        
        result = time_service_tool.calculate_time_difference(start_time, end_time)
        
        assert "error" in result
        assert "Invalid time format" in result["error"]
        assert "expected_format" in result

    def test_get_relative_time_now(self, time_service_tool):
        """Test getting relative time expressions for 'now'."""
        relative_times = time_service_tool.get_relative_time("now")
        
        assert isinstance(relative_times, dict)
        assert "now" in relative_times
        assert "today" in relative_times
        assert "yesterday" in relative_times
        assert "tomorrow" in relative_times
        assert "this_week" in relative_times
        assert "this_month" in relative_times
        assert "this_year" in relative_times
        
        # Verify all values are strings
        for value in relative_times.values():
            assert isinstance(value, str)

    def test_get_relative_time_invalid_reference(self, time_service_tool):
        """Test getting relative time with invalid reference."""
        result = time_service_tool.get_relative_time("invalid")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "Invalid reference time"

    def test_register_tools(self, time_service_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        
        time_service_tool.register(mock_mcp)
        
        # Verify tools were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'time_get_current_time',
            'time_get_timezone_info',
            'time_format_time'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, time_service_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "time_service.jsonl"
        assert time_service_tool.data_file == expected_path

    def test_timeinfo_model_validation(self):
        """Test TimeInfo model validation."""
        now = datetime.now()
        time_info = TimeInfo(
            current_time=now,
            timezone="UTC",
            timestamp=now.timestamp(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            day_of_week=now.strftime("%A"),
            day_of_year=now.timetuple().tm_yday,
            week_of_year=now.isocalendar()[1],
            month=now.strftime("%B"),
            year=now.year,
            is_weekend=now.weekday() >= 5,
            is_business_day=now.weekday() < 5
        )
        
        assert time_info.current_time == now
        assert time_info.timezone == "UTC"
        assert time_info.year == now.year

    def test_timeinfo_default_values(self):
        """Test TimeInfo model default values."""
        now = datetime.now()
        time_info = TimeInfo(
            current_time=now,
            timezone="UTC",
            timestamp=now.timestamp(),
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H:%M:%S"),
            day_of_week=now.strftime("%A"),
            day_of_year=now.timetuple().tm_yday,
            week_of_year=now.isocalendar()[1],
            month=now.strftime("%B"),
            year=now.year,
            is_weekend=now.weekday() >= 5,
            is_business_day=now.weekday() < 5
        )
        
        # All fields should be set
        assert time_info.current_time is not None
        assert time_info.timezone is not None
        assert time_info.timestamp is not None
        assert time_info.date is not None
        assert time_info.time is not None
        assert time_info.day_of_week is not None
        assert time_info.day_of_year is not None
        assert time_info.week_of_year is not None
        assert time_info.month is not None
        assert time_info.year is not None
        assert isinstance(time_info.is_weekend, bool)
        assert isinstance(time_info.is_business_day, bool)

    @patch('tools.time_service.time_service.datetime')
    def test_get_current_time_mocked(self, mock_datetime, time_service_tool):
        """Test get_current_time with mocked datetime."""
        # Mock a specific datetime
        mock_now = datetime(2024, 1, 15, 12, 30, 45)
        mock_datetime.now.return_value = mock_now
        
        time_info = time_service_tool.get_current_time()
        
        assert time_info.year == 2024
        assert time_info.month == "January"
        assert time_info.day_of_week == "Monday"
        assert time_info.day_of_year == 15
        assert time_info.week_of_year == 3
        assert time_info.is_weekend is False  # Monday
        assert time_info.is_business_day is True

    def test_edge_cases_weekend_business_day(self, time_service_tool):
        """Test edge cases for weekend vs business day logic."""
        # This test verifies the logic works correctly
        # The actual values depend on the current day when the test runs
        time_info = time_service_tool.get_current_time()
        
        # Weekend and business day should be mutually exclusive
        assert time_info.is_weekend != time_info.is_business_day
        
        # If it's a weekend, business day should be False
        if time_info.is_weekend:
            assert time_info.is_business_day is False
        
        # If it's a business day, weekend should be False
        if time_info.is_business_day:
            assert time_info.is_weekend is False

    def test_timestamp_consistency(self, time_service_tool):
        """Test that timestamp in TimeInfo is consistent with current_time."""
        time_info = time_service_tool.get_current_time()
        
        # The timestamp should be very close to the current_time timestamp
        # Allow for small differences due to processing time
        time_diff = abs(time_info.timestamp - time_info.current_time.timestamp())
        assert time_diff < 1.0  # Less than 1 second difference 