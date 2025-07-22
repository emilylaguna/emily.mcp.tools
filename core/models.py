"""
Data models for the unified memory architecture.
Phase 1.1: Database Schema & Core Models
"""

import uuid
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MemoryEntity(BaseModel):
    """Represents a memory entity in the unified system."""
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(..., description="Entity type (task, person, project, file, etc.)")
    name: str = Field(..., description="Display name for the entity")
    content: Optional[str] = Field(None, description="Full content/description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Flexible metadata")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate entity type is supported."""
        valid_types = {
            'task', 'person', 'project', 'file', 'handoff', 'area', 
            'meeting', 'technology', 'conversation', 'note', 'workflow', 'workflow_run'
        }
        if v not in valid_types:
            raise ValueError(f"Entity type must be one of: {valid_types}")
        return v
    
    @field_validator('tags', mode='before')
    @classmethod
    def validate_tags(cls, v):
        """Ensure tags is always a list."""
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'content': self.content,
            'metadata': self.metadata,
            'tags': ','.join(self.tags) if self.tags else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntity':
        """Create from dictionary from database."""
        # Handle tags conversion
        tags = data.get('tags')
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get('id'),
            type=data['type'],
            name=data['name'],
            content=data.get('content'),
            metadata=data.get('metadata', {}),
            tags=tags or [],
            created_at=created_at,
            updated_at=updated_at
        )


class MemoryRelation(BaseModel):
    """Represents a relationship between two memory entities."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Relationship type")
    strength: float = Field(1.0, ge=0.0, le=1.0, description="Relationship strength (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Relationship metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('relation_type')
    @classmethod
    def validate_relation_type(cls, v):
        """Validate relation type is supported."""
        valid_types = {
            'relates_to', 'contains', 'follows_from', 'depends_on', 
            'mentions', 'implements', 'references', 'assigned_to',
            'created_by', 'part_of', 'similar_to'
        }
        if v not in valid_types:
            raise ValueError(f"Relation type must be one of: {valid_types}")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryRelation':
        """Create from dictionary from database."""
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get('id'),
            source_id=data['source_id'],
            target_id=data['target_id'],
            relation_type=data['relation_type'],
            strength=data.get('strength', 1.0),
            metadata=data.get('metadata', {}),
            created_at=created_at
        )


class MemoryContext(BaseModel):
    """Represents a conversation or session context."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(..., description="Context type (handoff, meeting, debug_session, etc.)")
    content: str = Field(..., description="Full content")
    summary: Optional[str] = Field(None, description="AI-generated summary")
    topics: List[str] = Field(default_factory=list, description="AI-extracted topics")
    entity_ids: List[str] = Field(default_factory=list, description="Referenced entity IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Context metadata")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate context type is supported."""
        valid_types = {
            'handoff', 'meeting', 'debug_session', 'conversation', 
            'code_review', 'planning_session', 'retrospective'
        }
        if v not in valid_types:
            raise ValueError(f"Context type must be one of: {valid_types}")
        return v
    
    @field_validator('topics', mode='before')
    @classmethod
    def validate_topics(cls, v):
        """Ensure topics is always a list."""
        if isinstance(v, str):
            return [topic.strip() for topic in v.split(',') if topic.strip()]
        return v or []
    
    @field_validator('entity_ids', mode='before')
    @classmethod
    def validate_entity_ids(cls, v):
        """Ensure entity_ids is always a list."""
        if isinstance(v, str):
            return [eid.strip() for eid in v.split(',') if eid.strip()]
        return v or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'summary': self.summary,
            'topics': ','.join(self.topics) if self.topics else None,
            'entity_ids': ','.join(self.entity_ids) if self.entity_ids else None,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryContext':
        """Create from dictionary from database."""
        # Handle topics conversion
        topics = data.get('topics')
        if isinstance(topics, str):
            topics = [topic.strip() for topic in topics.split(',') if topic.strip()]
        
        # Handle entity_ids conversion
        entity_ids = data.get('entity_ids')
        if isinstance(entity_ids, str):
            entity_ids = [eid.strip() for eid in entity_ids.split(',') if eid.strip()]
        
        # Handle datetime conversion
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            id=data.get('id'),
            type=data['type'],
            content=data['content'],
            summary=data.get('summary'),
            topics=topics or [],
            entity_ids=entity_ids or [],
            metadata=data.get('metadata', {}),
            created_at=created_at
        )


# Type aliases for common entity types
EntityType = str
RelationType = str
ContextType = str

# Constants for common entity types
ENTITY_TYPES = {
    'task': 'Todo items, action items',
    'person': 'People mentioned in conversations',
    'project': 'Software projects, initiatives',
    'file': 'Code files, documents',
    'handoff': 'Conversation contexts',
    'area': 'Areas for organization',
    'meeting': 'Meeting notes and outcomes',
    'technology': 'Programming languages, frameworks, tools',
    'conversation': 'General conversation contexts',
    'note': 'General notes and documentation'
}

# Constants for common relation types
RELATION_TYPES = {
    'relates_to': 'General relationship',
    'contains': 'Hierarchical containment',
    'follows_from': 'Temporal or logical sequence',
    'depends_on': 'Dependency relationship',
    'mentions': 'Entity mentioned in content',
    'implements': 'Implementation relationship',
    'references': 'Reference relationship',
    'assigned_to': 'Assignment relationship',
    'created_by': 'Creation relationship',
    'part_of': 'Part-whole relationship',
    'similar_to': 'Similarity relationship'
} 