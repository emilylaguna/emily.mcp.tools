"""
Core functionality for Emily.Tools.

This package contains the unified memory store, database management,
and data models.
"""

from .memory import UnifiedMemoryStore
from .database import DatabaseManager
from .models import MemoryEntity, MemoryRelation, MemoryContext

__all__ = [
    'UnifiedMemoryStore',
    'DatabaseManager', 
    'MemoryEntity',
    'MemoryRelation',
    'MemoryContext'
] 