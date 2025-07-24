"""
Core functionality for Emily.Tools.

This package contains the unified memory store, database management,
and data models.
"""

from .memory import UnifiedMemoryStore, create_test_memory_store, create_memory_store
from .database import DatabaseManager
from .models import MemoryEntity, MemoryRelation, MemoryContext

__all__ = [
    'UnifiedMemoryStore',
    'create_test_memory_store',
    'create_memory_store',
    'DatabaseManager', 
    'MemoryEntity',
    'MemoryRelation',
    'MemoryContext'
] 