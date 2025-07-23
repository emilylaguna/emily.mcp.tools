"""
Time Service tool for Emily Tools MCP server.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel

from ..base import BaseTool
from ..common_types import DayOfWeek, TimeUnit

logger = logging.getLogger(__name__)


# Common time format literals
TimeFormat = Literal[
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%H:%M:%S", 
    "%B %d, %Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ"
]

logger = logging.getLogger(__name__)


class TimeInfo(BaseModel):
    current_time: datetime
    timezone: str
    timestamp: float
    date: str
    time: str
    day_of_week: str
    day_of_year: int
    week_of_year: int
    month: str
    year: int
    is_weekend: bool
    is_business_day: bool


class TimeServiceTool(BaseTool):
    """Time service for providing current date/time information to LLMs."""
    
    @property
    def name(self) -> str:
        return "time_service"
    
    @property
    def description(self) -> str:
        return "Provides current date and time information for LLM context"
    
    def get_capabilities(self) -> List[str]:
        return [
            "get_current_time",
            "get_time_info",
            "format_time",
            "get_timezone_info",
            "calculate_time_difference"
        ]
    
    def get_current_time(self) -> TimeInfo:
        """Get comprehensive current time information."""
        now = datetime.now()
        
        return TimeInfo(
            current_time=now,
            timezone=str(now.astimezone().tzinfo),
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
    
    def get_time_info(self, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current time in a specific format."""
        return datetime.now().strftime(format_string)
    
    def format_time(self, timestamp: float, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format a timestamp in a specific format."""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_string)
    
    def get_timezone_info(self) -> Dict[str, Any]:
        """Get current timezone information."""
        now = datetime.now()
        utc_now = datetime.now(timezone.utc)
        
        return {
            "local_timezone": str(now.astimezone().tzinfo),
            "utc_offset": now.astimezone().utcoffset().total_seconds() / 3600,
            "is_dst": now.astimezone().dst().total_seconds() > 0 if now.astimezone().dst() else False,
            "utc_time": utc_now.isoformat(),
            "local_time": now.isoformat()
        }
    
    def calculate_time_difference(self, start_time: str, end_time: str, 
                                format_string: str = "%Y-%m-%d %H:%M:%S") -> Dict[str, Any]:
        """Calculate the difference between two times."""
        try:
            start_dt = datetime.strptime(start_time, format_string)
            end_dt = datetime.strptime(end_time, format_string)
            
            diff = end_dt - start_dt
            
            return {
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "difference_seconds": diff.total_seconds(),
                "difference_days": diff.days,
                "difference_hours": diff.total_seconds() / 3600,
                "difference_minutes": diff.total_seconds() / 60,
                "is_positive": diff.total_seconds() >= 0
            }
        except ValueError as e:
            return {
                "error": f"Invalid time format: {e}",
                "expected_format": format_string
            }
    
    def get_relative_time(self, reference_time: str = "now") -> Dict[str, str]:
        """Get relative time expressions."""
        now = datetime.now()
        
        if reference_time == "now":
            return {
                "now": now.isoformat(),
                "today": now.strftime("%Y-%m-%d"),
                "yesterday": (now.replace(day=now.day-1)).strftime("%Y-%m-%d"),
                "tomorrow": (now.replace(day=now.day+1)).strftime("%Y-%m-%d"),
                "this_week": f"Week {now.isocalendar()[1]} of {now.year}",
                "this_month": now.strftime("%B %Y"),
                "this_year": str(now.year)
            }
        
        return {"error": "Invalid reference time"} 

    def register(self, mcp):
        @mcp.tool(
            name="time_get_current_time",
            description="Get comprehensive current time information including timezone, dates, and business day indicators",
            tags={"time", "current", "timezone", "date", "business"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def time_get_current_time(ctx: Optional[object] = None) -> dict:
            """Get comprehensive current time information."""
            time_info = self.get_current_time()
            return {
                "current_time": time_info.current_time.isoformat(),
                "timezone": time_info.timezone,
                "timestamp": time_info.timestamp,
                "date": time_info.date,
                "time": time_info.time,
                "day_of_week": time_info.day_of_week,
                "day_of_year": time_info.day_of_year,
                "week_of_year": time_info.week_of_year,
                "month": time_info.month,
                "year": time_info.year,
                "is_weekend": time_info.is_weekend,
                "is_business_day": time_info.is_business_day
            }

        @mcp.tool(
            name="time_get_timezone_info",
            description="Get current timezone information including offset and daylight saving time status",
            tags={"time", "timezone", "offset", "dst", "locale"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def time_get_timezone_info(ctx: Optional[object] = None) -> dict:
            """Get current timezone information."""
            return self.get_timezone_info()

        @mcp.tool(
            name="time_format_time",
            description="Format a timestamp in a specific format using standard strftime formatting codes",
            tags={"time", "format", "timestamp", "strftime", "conversion"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def time_format_time(timestamp: float, format_string: TimeFormat = "%Y-%m-%d %H:%M:%S", ctx: Optional[object] = None) -> str:
            """Format a timestamp in a specific format."""
            return self.format_time(timestamp, format_string)
        
        logger.info("Time Service MCP tools registered successfully")