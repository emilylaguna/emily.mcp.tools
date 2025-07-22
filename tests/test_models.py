"""
Unit tests for unified memory architecture data models.
Phase 1.1: Database Schema & Core Models
"""

import pytest
from datetime import datetime
from core.models import MemoryEntity, MemoryRelation, MemoryContext, ENTITY_TYPES, RELATION_TYPES


class TestMemoryEntity:
    """Test MemoryEntity model validation and serialization."""
    
    def test_valid_entity_creation(self):
        """Test creating a valid entity."""
        entity = MemoryEntity(
            type="task",
            name="Implement user authentication",
            content="Add OAuth2 authentication to the web app",
            tags=["auth", "security", "frontend"]
        )
        
        assert entity.type == "task"
        assert entity.name == "Implement user authentication"
        assert entity.content == "Add OAuth2 authentication to the web app"
        assert entity.tags == ["auth", "security", "frontend"]
        assert entity.id is not None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
    
    def test_invalid_entity_type(self):
        """Test that invalid entity types raise validation error."""
        with pytest.raises(ValueError, match="Entity type must be one of"):
            MemoryEntity(
                type="invalid_type",
                name="Test entity"
            )
    
    def test_tags_from_string(self):
        """Test that tags can be created from comma-separated string."""
        entity = MemoryEntity(
            type="task",
            name="Test task",
            tags="tag1,tag2, tag3 , tag4"
        )
        
        assert entity.tags == ["tag1", "tag2", "tag3", "tag4"]
    
    def test_empty_tags(self):
        """Test handling of empty tags."""
        entity = MemoryEntity(
            type="task",
            name="Test task",
            tags=""
        )
        
        assert entity.tags == []
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary for database storage."""
        entity = MemoryEntity(
            type="person",
            name="John Doe",
            content="Software engineer",
            tags=["engineer", "python"],
            metadata={"email": "john@example.com"}
        )
        
        data = entity.to_dict()
        
        assert data["type"] == "person"
        assert data["name"] == "John Doe"
        assert data["content"] == "Software engineer"
        assert data["tags"] == "engineer,python"
        assert data["metadata"] == {"email": "john@example.com"}
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary from database."""
        data = {
            "id": "test-uuid",
            "type": "project",
            "name": "My Project",
            "content": "A test project",
            "tags": "project,test,demo",
            "metadata": {"status": "active"},
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-01T12:00:00"
        }
        
        entity = MemoryEntity.from_dict(data)
        
        assert entity.id == "test-uuid"
        assert entity.type == "project"
        assert entity.name == "My Project"
        assert entity.content == "A test project"
        assert entity.tags == ["project", "test", "demo"]
        assert entity.metadata == {"status": "active"}
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
    
    def test_all_valid_entity_types(self):
        """Test that all defined entity types are valid."""
        for entity_type in ENTITY_TYPES.keys():
            entity = MemoryEntity(type=entity_type, name=f"Test {entity_type}")
            assert entity.type == entity_type


class TestMemoryRelation:
    """Test MemoryRelation model validation and serialization."""
    
    def test_valid_relation_creation(self):
        """Test creating a valid relation."""
        relation = MemoryRelation(
            source_id="entity-1",
            target_id="entity-2",
            relation_type="relates_to",
            strength=0.8
        )
        
        assert relation.source_id == "entity-1"
        assert relation.target_id == "entity-2"
        assert relation.relation_type == "relates_to"
        assert relation.strength == 0.8
        assert relation.id is not None
        assert isinstance(relation.created_at, datetime)
    
    def test_invalid_relation_type(self):
        """Test that invalid relation types raise validation error."""
        with pytest.raises(ValueError, match="Relation type must be one of"):
            MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type="invalid_relation"
            )
    
    def test_strength_validation(self):
        """Test that strength is constrained to 0.0-1.0 range."""
        # Valid strength values
        MemoryRelation(
            source_id="entity-1",
            target_id="entity-2",
            relation_type="relates_to",
            strength=0.0
        )
        
        MemoryRelation(
            source_id="entity-1",
            target_id="entity-2",
            relation_type="relates_to",
            strength=1.0
        )
        
        # Invalid strength values
        with pytest.raises(ValueError):
            MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type="relates_to",
                strength=-0.1
            )
        
        with pytest.raises(ValueError):
            MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type="relates_to",
                strength=1.1
            )
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary for database storage."""
        relation = MemoryRelation(
            source_id="task-1",
            target_id="person-1",
            relation_type="assigned_to",
            strength=0.9,
            metadata={"priority": "high"}
        )
        
        data = relation.to_dict()
        
        assert data["source_id"] == "task-1"
        assert data["target_id"] == "person-1"
        assert data["relation_type"] == "assigned_to"
        assert data["strength"] == 0.9
        assert data["metadata"] == {"priority": "high"}
        assert "id" in data
        assert "created_at" in data
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary from database."""
        data = {
            "id": "relation-uuid",
            "source_id": "file-1",
            "target_id": "project-1",
            "relation_type": "part_of",
            "strength": 0.7,
            "metadata": {"path": "/src/main.py"},
            "created_at": "2024-01-01T12:00:00"
        }
        
        relation = MemoryRelation.from_dict(data)
        
        assert relation.id == "relation-uuid"
        assert relation.source_id == "file-1"
        assert relation.target_id == "project-1"
        assert relation.relation_type == "part_of"
        assert relation.strength == 0.7
        assert relation.metadata == {"path": "/src/main.py"}
        assert isinstance(relation.created_at, datetime)
    
    def test_all_valid_relation_types(self):
        """Test that all defined relation types are valid."""
        for relation_type in RELATION_TYPES.keys():
            relation = MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type=relation_type
            )
            assert relation.relation_type == relation_type


class TestMemoryContext:
    """Test MemoryContext model validation and serialization."""
    
    def test_valid_context_creation(self):
        """Test creating a valid context."""
        context = MemoryContext(
            type="handoff",
            content="Discussed authentication implementation with team",
            summary="Team meeting about auth",
            topics=["authentication", "security"],
            entity_ids=["person-1", "task-1"]
        )
        
        assert context.type == "handoff"
        assert context.content == "Discussed authentication implementation with team"
        assert context.summary == "Team meeting about auth"
        assert context.topics == ["authentication", "security"]
        assert context.entity_ids == ["person-1", "task-1"]
        assert context.id is not None
        assert isinstance(context.created_at, datetime)
    
    def test_invalid_context_type(self):
        """Test that invalid context types raise validation error."""
        with pytest.raises(ValueError, match="Context type must be one of"):
            MemoryContext(
                type="invalid_context",
                content="Test content"
            )
    
    def test_topics_from_string(self):
        """Test that topics can be created from comma-separated string."""
        context = MemoryContext(
            type="meeting",
            content="Test meeting",
            topics="topic1,topic2, topic3 , topic4"
        )
        
        assert context.topics == ["topic1", "topic2", "topic3", "topic4"]
    
    def test_entity_ids_from_string(self):
        """Test that entity_ids can be created from comma-separated string."""
        context = MemoryContext(
            type="conversation",
            content="Test conversation",
            entity_ids="entity-1,entity-2, entity-3 , entity-4"
        )
        
        assert context.entity_ids == ["entity-1", "entity-2", "entity-3", "entity-4"]
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary for database storage."""
        context = MemoryContext(
            type="debug_session",
            content="Debugged authentication issue",
            summary="Fixed OAuth2 bug",
            topics=["debugging", "auth", "oauth2"],
            entity_ids=["bug-1", "file-1"],
            metadata={"duration": "2 hours"}
        )
        
        data = context.to_dict()
        
        assert data["type"] == "debug_session"
        assert data["content"] == "Debugged authentication issue"
        assert data["summary"] == "Fixed OAuth2 bug"
        assert data["topics"] == "debugging,auth,oauth2"
        assert data["entity_ids"] == "bug-1,file-1"
        assert data["metadata"] == {"duration": "2 hours"}
        assert "id" in data
        assert "created_at" in data
    
    def test_from_dict_conversion(self):
        """Test creation from dictionary from database."""
        data = {
            "id": "context-uuid",
            "type": "code_review",
            "content": "Reviewed authentication PR",
            "summary": "Approved with minor changes",
            "topics": "auth,review,pr",
            "entity_ids": "pr-1,person-1",
            "metadata": {"status": "approved"},
            "created_at": "2024-01-01T12:00:00"
        }
        
        context = MemoryContext.from_dict(data)
        
        assert context.id == "context-uuid"
        assert context.type == "code_review"
        assert context.content == "Reviewed authentication PR"
        assert context.summary == "Approved with minor changes"
        assert context.topics == ["auth", "review", "pr"]
        assert context.entity_ids == ["pr-1", "person-1"]
        assert context.metadata == {"status": "approved"}
        assert isinstance(context.created_at, datetime)


class TestModelIntegration:
    """Test integration between different models."""
    
    def test_entity_relation_integration(self):
        """Test creating entities and relations between them."""
        # Create entities
        person = MemoryEntity(
            type="person",
            name="Alice",
            content="Software engineer"
        )
        
        task = MemoryEntity(
            type="task",
            name="Implement login",
            content="Add user login functionality"
        )
        
        # Create relation
        relation = MemoryRelation(
            source_id=task.id,
            target_id=person.id,
            relation_type="assigned_to",
            strength=0.9
        )
        
        assert relation.source_id == task.id
        assert relation.target_id == person.id
        assert relation.relation_type == "assigned_to"
    
    def test_context_entity_references(self):
        """Test creating context that references entities."""
        # Create entities
        person = MemoryEntity(type="person", name="Bob")
        task = MemoryEntity(type="task", name="Fix bug")
        
        # Create context referencing entities
        context = MemoryContext(
            type="handoff",
            content="Discussed bug fix with Bob",
            entity_ids=[person.id, task.id]
        )
        
        assert person.id in context.entity_ids
        assert task.id in context.entity_ids 