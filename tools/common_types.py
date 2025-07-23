"""
Common type definitions for Emily Tools MCP server.
Provides shared enums, literals, and type aliases for consistent type safety.
"""

from enum import Enum
from typing import Literal, Union

# Literal types for common string parameters
TimeFrame = Literal["today", "week", "month", "quarter", "year"]
SortOrder = Literal["asc", "desc", "ascending", "descending"]
FilterOperator = Literal["equals", "contains", "starts_with", "ends_with", "greater_than", "less_than", "in", "not_in"]

# Common status enums
class Status(str, Enum):
    """Common status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class Priority(str, Enum):
    """Priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class EnergyLevel(str, Enum):
    """Energy levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Time-related enums
class TimeUnit(str, Enum):
    """Time units for scheduling and estimates."""
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


class DayOfWeek(str, Enum):
    """Days of the week."""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


# Notification and communication enums
class NotificationType(str, Enum):
    """Notification types."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    SLACK = "slack"
    DISCORD = "discord"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# File and data enums
class FileType(str, Enum):
    """Common file types."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"


class DataFormat(str, Enum):
    """Data formats."""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    YAML = "yaml"
    TOML = "toml"
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"


# Permission and access enums
class PermissionLevel(str, Enum):
    """Permission levels."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


class AccessType(str, Enum):
    """Access types."""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"
    RESTRICTED = "restricted"


# Workflow and automation enums
class TriggerType(str, Enum):
    """Trigger types for workflows."""
    SCHEDULE = "schedule"
    EVENT = "event"
    CONDITION = "condition"
    MANUAL = "manual"
    WEBHOOK = "webhook"


class ActionType(str, Enum):
    """Action types for workflows."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    NOTIFY = "notify"
    EXECUTE = "execute"
    TRANSFORM = "transform"


# Search and analysis enums
class SearchMode(str, Enum):
    """Search modes."""
    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"
    REGEX = "regex"


class AnalysisType(str, Enum):
    """Analysis types."""
    SENTIMENT = "sentiment"
    TOPIC = "topic"
    ENTITY = "entity"
    RELATIONSHIP = "relationship"
    PATTERN = "pattern"
    TREND = "trend"


# Calendar and scheduling enums
class EventType(str, Enum):
    """Calendar event types."""
    MEETING = "meeting"
    TASK = "task"
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    DEADLINE = "deadline"
    MILESTONE = "milestone"
    OTHER = "other"


class RecurrenceType(str, Enum):
    """Recurrence types for events."""
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


# Task and project enums
class TaskType(str, Enum):
    """Task types."""
    TODO = "todo"
    BUG = "bug"
    FEATURE = "feature"
    RESEARCH = "research"
    REVIEW = "review"
    MEETING = "meeting"
    DOCUMENTATION = "documentation"


class ProjectType(str, Enum):
    """Project types."""
    PERSONAL = "personal"
    WORK = "work"
    COLLABORATIVE = "collaborative"
    OPEN_SOURCE = "open_source"
    RESEARCH = "research"
    LEARNING = "learning"


# Integration and API enums
class IntegrationType(str, Enum):
    """Integration types."""
    GITHUB = "github"
    SLACK = "slack"
    JIRA = "jira"
    TRELLO = "trello"
    NOTION = "notion"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    CUSTOM = "custom"


class APIMethod(str, Enum):
    """HTTP methods for API calls."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# Type aliases for common parameter combinations
StatusFilter = Union[Status, Literal["all"]]
PriorityFilter = Union[Priority, Literal["all"]]
TimeFrameFilter = Union[TimeFrame, Literal["all", "custom"]]
SearchTypeFilter = Union[SearchMode, Literal["all"]] 