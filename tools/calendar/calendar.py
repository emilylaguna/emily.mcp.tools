"""
Calendar tool for Emily Tools MCP server.
"""

from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseTool
import json


class EventType(str, Enum):
    MEETING = "meeting"
    TASK = "task"
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    OTHER = "other"


class Event(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    start_time: datetime
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: List[str] = []
    is_all_day: bool = False
    created_at: datetime = datetime.now()
    tags: List[str] = []


class CalendarTool(BaseTool):
    """Calendar event management tool using JSONL."""
    
    @property
    def name(self) -> str:
        return "calendar"
    
    @property
    def description(self) -> str:
        return "Manage calendar events, meetings, and appointments"
    
    def get_capabilities(self) -> List[str]:
        return [
            "create_event",
            "list_events",
            "get_event",
            "update_event", 
            "delete_event",
            "search_events",
            "get_upcoming_events",
            "get_events_by_date_range"
        ]
    
    def _read_events(self) -> List[Event]:
        if not self.data_file.exists():
            return []
        with open(self.data_file, 'r') as f:
            return [Event(**json.loads(line)) for line in f if line.strip()]

    def _write_events(self, events: List[Event]):
        with open(self.data_file, 'w') as f:
            for event in events:
                f.write(event.json() + '\n')

    def create_event(self, title: str, start_time: str, end_time: Optional[str] = None,
                    description: Optional[str] = None, event_type: EventType = EventType.OTHER,
                    location: Optional[str] = None, attendees: List[str] = [],
                    is_all_day: bool = False, tags: List[str] = []) -> Event:
        """Create a new calendar event and append to JSONL."""
        events = self._read_events()
        new_id = max([e.id for e in events if e.id is not None] + [0]) + 1
        event = Event(
            id=new_id,
            title=title,
            description=description,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendees=attendees,
            is_all_day=is_all_day,
            created_at=datetime.now(),
            tags=tags,
        )
        with open(self.data_file, 'a') as f:
            f.write(event.json() + '\n')
        return event

    def list_events(self, event_type: Optional[EventType] = None,
                   limit: int = 50) -> List[Event]:
        events = self._read_events()
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[:limit]

    def get_event(self, event_id: int) -> Optional[Event]:
        events = self._read_events()
        for e in events:
            if e.id == event_id:
                return e
        return None

    def update_event(self, event_id: int, **kwargs) -> Optional[Event]:
        events = self._read_events()
        updated = None
        for e in events:
            if e.id == event_id:
                for k, v in kwargs.items():
                    setattr(e, k, v)
                updated = e
        self._write_events(events)
        return updated

    def delete_event(self, event_id: int) -> bool:
        events = self._read_events()
        new_events = [e for e in events if e.id != event_id]
        self._write_events(new_events)
        return len(new_events) < len(events)

    def search_events(self, query: str) -> List[Event]:
        events = self._read_events()
        return [e for e in events if query.lower() in e.title.lower() or (e.description and query.lower() in e.description.lower())]

    def get_upcoming_events(self, days: int = 7) -> List[Event]:
        events = self._read_events()
        now = datetime.now()
        future = now + timedelta(days=days)
        return [e for e in events if e.start_time and now <= datetime.fromisoformat(str(e.start_time)) <= future]

    def get_events_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        events = self._read_events()
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return [e for e in events if e.start_time and start <= datetime.fromisoformat(str(e.start_time)) <= end]
    
    def _row_to_event(self, row) -> Event:
        """Convert database row to Event object."""
        return Event(
            id=row[0],
            title=row[1],
            description=row[2],
            event_type=EventType(row[3]),
            start_time=datetime.fromisoformat(row[4]),
            end_time=datetime.fromisoformat(row[5]) if row[5] else None,
            location=row[6],
            attendees=row[7].split(',') if row[7] else [],
            is_all_day=bool(row[8]),
            created_at=datetime.fromisoformat(row[9]),
            tags=row[10].split(',') if row[10] else []
        ) 

    def register(self, mcp):
        @mcp.tool()
        async def calendar_create_event(title: str, start_time: str, end_time: str = None,
                                       description: str = None, event_type: str = "other",
                                       location: str = None, attendees: list = None, 
                                       is_all_day: bool = False, tags: list = None, ctx: object = None) -> dict:
            """Create a new calendar event."""
            if attendees is None:
                attendees = []
            if tags is None:
                tags = []
            event_type_enum = EventType(event_type.lower())
            event = self.create_event(
                title=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                event_type=event_type_enum,
                location=location,
                attendees=attendees,
                is_all_day=is_all_day,
                tags=tags
            )
            return {
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "event_type": event.event_type.value,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "location": event.location,
                "attendees": event.attendees,
                "is_all_day": event.is_all_day,
                "tags": event.tags
            }

        @mcp.tool()
        async def calendar_list_events(event_type: str = None, limit: int = 50, ctx: object = None) -> list:
            """List calendar events with optional filtering."""
            event_type_enum = EventType(event_type.lower()) if event_type else None
            events = self.list_events(event_type=event_type_enum, limit=limit)
            return [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_type": event.event_type.value,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat() if event.end_time else None,
                    "location": event.location,
                    "attendees": event.attendees,
                    "is_all_day": event.is_all_day,
                    "tags": event.tags
                }
                for event in events
            ]

        @mcp.tool()
        async def calendar_get_upcoming_events(days: int = 7, ctx: object = None) -> list:
            """Get upcoming calendar events."""
            events = self.get_upcoming_events(days=days)
            return [
                {
                    "id": event.id,
                    "title": event.title,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat() if event.end_time else None,
                    "location": event.location,
                    "event_type": event.event_type.value
                }
                for event in events
            ]

        @mcp.resource("resource://calendar/all")
        def resource_calendar_all() -> list:
            """Return all calendar events as a list of dicts."""
            return [event.dict() for event in self.list_events()]

        @mcp.resource("resource://calendar/{event_id}")
        def resource_calendar_by_id(event_id: int) -> dict:
            """Return a single calendar event by ID as a dict."""
            event = self.get_event(event_id)
            return event.dict() if event else {} 