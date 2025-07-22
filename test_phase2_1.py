"""
Tests for Phase 2.1: CRUD Operations with Vector Search
"""

import json
import pytest
import tempfile
from datetime import datetime, UTC
from pathlib import Path

from core import create_test_memory_store
from models import MemoryEntity, MemoryRelation, MemoryContext


class TestEntityCRUD:
    """Test entity CRUD operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def test_save_entity_basic(self):
        """Test basic entity save operation."""
        entity = MemoryEntity(
            type="task",
            name="Test Task",
            content="This is a test task",
            tags=["test", "python"]
        )
        
        saved_entity = self.store.save_entity(entity)
        
        assert saved_entity.id is not None
        assert saved_entity.type == "task"
        assert saved_entity.name == "Test Task"
        assert saved_entity.content == "This is a test task"
        assert saved_entity.tags == ["test", "python"]
        assert saved_entity.created_at is not None
        assert saved_entity.updated_at is not None
    
    def test_save_entity_with_metadata(self):
        """Test entity save with metadata."""
        entity = MemoryEntity(
            type="project",
            name="Test Project",
            content="A test project",
            metadata={"priority": "high", "status": "active"},
            tags=["project", "test"]
        )
        
        saved_entity = self.store.save_entity(entity)
        
        assert saved_entity.metadata["priority"] == "high"
        assert saved_entity.metadata["status"] == "active"
    
    def test_get_entity(self):
        """Test entity retrieval."""
        entity = MemoryEntity(
            type="person",
            name="John Doe",
            content="A test person"
        )
        
        saved_entity = self.store.save_entity(entity)
        retrieved_entity = self.store.get_entity(saved_entity.id)
        
        assert retrieved_entity is not None
        assert retrieved_entity.id == saved_entity.id
        assert retrieved_entity.name == "John Doe"
        assert retrieved_entity.type == "person"
    
    def test_get_nonexistent_entity(self):
        """Test retrieving non-existent entity."""
        entity = self.store.get_entity("nonexistent-id")
        assert entity is None
    
    def test_update_entity(self):
        """Test entity update operation."""
        entity = MemoryEntity(
            type="task",
            name="Original Task",
            content="Original content"
        )
        
        saved_entity = self.store.save_entity(entity)
        original_created_at = saved_entity.created_at
        
        # Update the entity
        saved_entity.name = "Updated Task"
        saved_entity.content = "Updated content"
        updated_entity = self.store.update_entity(saved_entity)
        
        assert updated_entity.name == "Updated Task"
        assert updated_entity.content == "Updated content"
        assert updated_entity.created_at == original_created_at
        assert updated_entity.updated_at > original_created_at
    
    def test_update_nonexistent_entity(self):
        """Test updating non-existent entity."""
        entity = MemoryEntity(
            id="nonexistent-id",
            type="task",
            name="Test Task"
        )
        
        with pytest.raises(ValueError, match="Entity nonexistent-id not found"):
            self.store.update_entity(entity)
    
    def test_delete_entity(self):
        """Test entity deletion."""
        entity = MemoryEntity(
            type="task",
            name="Task to Delete",
            content="This will be deleted"
        )
        
        saved_entity = self.store.save_entity(entity)
        entity_id = saved_entity.id
        
        # Verify entity exists
        assert self.store.get_entity(entity_id) is not None
        
        # Delete entity
        success = self.store.delete_entity(entity_id)
        assert success is True
        
        # Verify entity is deleted
        assert self.store.get_entity(entity_id) is None
    
    def test_delete_nonexistent_entity(self):
        """Test deleting non-existent entity."""
        success = self.store.delete_entity("nonexistent-id")
        assert success is False


class TestSearchOperations:
    """Test search functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
        self._create_test_data()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def _create_test_data(self):
        """Create test data for search tests."""
        entities = [
            MemoryEntity(type="task", name="Fix login bug", content="The login system has a bug", tags=["bug", "urgent"]),
            MemoryEntity(type="task", name="Add user authentication", content="Implement user login and registration", tags=["feature", "auth"]),
            MemoryEntity(type="project", name="E-commerce platform", content="Build an online shopping platform", tags=["project", "web"]),
            MemoryEntity(type="person", name="Alice Johnson", content="Frontend developer", tags=["developer", "frontend"]),
            MemoryEntity(type="technology", name="React", content="JavaScript library for building user interfaces", tags=["javascript", "frontend"]),
        ]
        
        for entity in entities:
            self.store.save_entity(entity)
    
    def test_basic_search(self):
        """Test basic search functionality."""
        results = self.store.search("login")
        
        assert len(results) >= 2
        # Should find both login-related tasks
        names = [r['name'] for r in results]
        assert "Fix login bug" in names
        assert "Add user authentication" in names
    
    def test_search_with_filters(self):
        """Test search with filters."""
        results = self.store.search("bug", filters={"type": "task"})
        
        assert len(results) >= 1
        for result in results:
            assert result['type'] == "task"
    
    def test_search_with_multiple_filters(self):
        """Test search with multiple filters."""
        results = self.store.search("user", filters={
            "types": ["task", "project"],
            "tags": ["feature"]
        })
        
        assert len(results) >= 1
        for result in results:
            assert result['type'] in ["task", "project"]
    
    def test_search_with_metadata_filters(self):
        """Test search with metadata filters."""
        # Create entity with metadata
        entity = MemoryEntity(
            type="task",
            name="Priority task",
            content="High priority task",
            metadata={"priority": "high", "assignee": "alice"}
        )
        self.store.save_entity(entity)
        
        results = self.store.search("priority", filters={"metadata.priority": "high"})
        
        assert len(results) >= 1
        for result in results:
            assert result['metadata'].get("priority") == "high"
    
    def test_empty_search_query(self):
        """Test search with empty query."""
        results = self.store.search("")
        assert results == []
    
    def test_search_limit(self):
        """Test search result limiting."""
        results = self.store.search("task", limit=2)
        assert len(results) <= 2


class TestRelationshipOperations:
    """Test relationship management."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
        self._create_test_entities()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def _create_test_entities(self):
        """Create test entities for relationship tests."""
        self.task = self.store.save_entity(MemoryEntity(
            type="task",
            name="Implement feature",
            content="Implement new feature"
        ))
        
        self.person = self.store.save_entity(MemoryEntity(
            type="person",
            name="John Doe",
            content="Developer"
        ))
        
        self.project = self.store.save_entity(MemoryEntity(
            type="project",
            name="Test Project",
            content="A test project"
        ))
    
    def test_save_relation(self):
        """Test saving a relationship."""
        relation = MemoryRelation(
            source_id=self.task.id,
            target_id=self.person.id,
            relation_type="assigned_to",
            strength=0.8
        )
        
        saved_relation = self.store.save_relation(relation)
        
        assert saved_relation.id is not None
        assert saved_relation.source_id == self.task.id
        assert saved_relation.target_id == self.person.id
        assert saved_relation.relation_type == "assigned_to"
        assert saved_relation.strength == 0.8
    
    def test_save_relation_with_nonexistent_entity(self):
        """Test saving relation with non-existent entity."""
        relation = MemoryRelation(
            source_id="nonexistent-id",
            target_id=self.person.id,
            relation_type="assigned_to"
        )
        
        with pytest.raises(ValueError, match="Source entity nonexistent-id not found"):
            self.store.save_relation(relation)
    
    def test_get_related_entities(self):
        """Test retrieving related entities."""
        # Create relationships
        relation1 = MemoryRelation(
            source_id=self.task.id,
            target_id=self.person.id,
            relation_type="assigned_to"
        )
        self.store.save_relation(relation1)
        
        relation2 = MemoryRelation(
            source_id=self.task.id,
            target_id=self.project.id,
            relation_type="part_of"
        )
        self.store.save_relation(relation2)
        
        # Get all related entities
        related = self.store.get_related(self.task.id)
        
        assert len(related) == 2
        entity_ids = [r['id'] for r in related]
        assert self.person.id in entity_ids
        assert self.project.id in entity_ids
    
    def test_get_related_with_filter(self):
        """Test getting related entities with type filter."""
        # Create relationships
        relation1 = MemoryRelation(
            source_id=self.task.id,
            target_id=self.person.id,
            relation_type="assigned_to"
        )
        self.store.save_relation(relation1)
        
        relation2 = MemoryRelation(
            source_id=self.task.id,
            target_id=self.project.id,
            relation_type="part_of"
        )
        self.store.save_relation(relation2)
        
        # Get only assigned_to relationships
        related = self.store.get_related(self.task.id, relation_types=["assigned_to"])
        
        assert len(related) == 1
        assert related[0]['id'] == self.person.id
        assert related[0]['relation_type'] == "assigned_to"
    
    def test_delete_relation(self):
        """Test deleting a relationship."""
        relation = MemoryRelation(
            source_id=self.task.id,
            target_id=self.person.id,
            relation_type="assigned_to"
        )
        
        saved_relation = self.store.save_relation(relation)
        
        # Verify relation exists
        related = self.store.get_related(self.task.id)
        assert len(related) == 1
        
        # Delete relation
        success = self.store.delete_relation(saved_relation.id)
        assert success is True
        
        # Verify relation is deleted
        related = self.store.get_related(self.task.id)
        assert len(related) == 0
    
    def test_delete_nonexistent_relation(self):
        """Test deleting non-existent relation."""
        success = self.store.delete_relation("nonexistent-id")
        assert success is False


class TestContextOperations:
    """Test context operations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def test_save_context(self):
        """Test saving context."""
        # Create a store with AI extraction disabled for this test
        test_store = create_test_memory_store(enable_ai_extraction=False)
        
        context = MemoryContext(
            type="meeting",
            content="Team meeting about project planning",
            summary="Discussed project timeline and milestones",
            topics=["planning", "timeline"],
            entity_ids=["entity1", "entity2"]
        )
        
        saved_context = test_store.save_context(context)
        
        assert saved_context.id is not None
        assert saved_context.type == "meeting"
        assert saved_context.content == "Team meeting about project planning"
        assert saved_context.summary == "Discussed project timeline and milestones"
        assert saved_context.topics == ["planning", "timeline"]
        assert saved_context.entity_ids == ["entity1", "entity2"]
        
        test_store.close()
    
    def test_search_contexts(self):
        """Test context search."""
        context1 = MemoryContext(
            type="meeting",
            content="Team meeting about project planning and timeline"
        )
        self.store.save_context(context1)
        
        context2 = MemoryContext(
            type="handoff",
            content="Handoff meeting with new team member"
        )
        self.store.save_context(context2)
        
        results = self.store.search_contexts("meeting")
        
        assert len(results) >= 2
        types = [c.type for c in results]
        assert "meeting" in types
        assert "handoff" in types
    
    def test_search_contexts_with_filters(self):
        """Test context search with filters."""
        context1 = MemoryContext(
            type="meeting",
            content="Team meeting about project planning"
        )
        self.store.save_context(context1)
        
        context2 = MemoryContext(
            type="handoff",
            content="Handoff meeting with new team member"
        )
        self.store.save_context(context2)
        
        results = self.store.search_contexts("meeting", filters={"type": "meeting"})
        
        assert len(results) >= 1
        for context in results:
            assert context.type == "meeting"


class TestVectorSearch:
    """Test vector search functionality (when enabled)."""
    
    def setup_method(self):
        """Set up test environment."""
        # Only run vector tests if sentence-transformers is available
        try:
            import sentence_transformers
            self.store = create_test_memory_store(enable_vector_search=True)
            self._create_test_data()
        except ImportError:
            pytest.skip("sentence-transformers not available")
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'store'):
            self.store.close()
    
    def _create_test_data(self):
        """Create test data for vector search."""
        entities = [
            MemoryEntity(type="task", name="Fix authentication bug", content="The login system has a critical bug"),
            MemoryEntity(type="task", name="Add user registration", content="Implement user signup functionality"),
            MemoryEntity(type="project", name="E-commerce website", content="Build online shopping platform"),
            MemoryEntity(type="technology", name="Python Django", content="Web framework for building applications"),
        ]
        
        for entity in entities:
            self.store.save_entity(entity)
    
    def test_vector_search_enabled(self):
        """Test that vector search is enabled."""
        pragma = self.store.check_pragma()
        assert pragma["vector_enabled"] is True
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        # Search for authentication-related content
        results = self.store.search("authentication login")
        
        assert len(results) >= 1
        # Should find the authentication bug task
        names = [r['name'] for r in results]
        assert "Fix authentication bug" in names
    
    def test_combined_search_results(self):
        """Test that vector and FTS results are combined."""
        results = self.store.search("user registration")
        
        assert len(results) >= 1
        # Should find the registration task
        names = [r['name'] for r in results]
        assert "Add user registration" in names


class TestPerformance:
    """Test performance characteristics."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def test_bulk_entity_operations(self):
        """Test performance of bulk entity operations."""
        import time
        
        # Create 100 entities
        start_time = time.time()
        
        for i in range(100):
            entity = MemoryEntity(
                type="task",
                name=f"Task {i}",
                content=f"Content for task {i}",
                tags=[f"tag{i}"]
            )
            self.store.save_entity(entity)
        
        save_time = time.time() - start_time
        
        # Verify all entities were saved
        results = self.store.search("Task", limit=1000)
        assert len(results) >= 100
        
        # Performance check (should be under 5 seconds for 100 entities)
        assert save_time < 5.0
    
    def test_search_performance(self):
        """Test search performance."""
        import time
        
        # Create test data
        for i in range(50):
            entity = MemoryEntity(
                type="task",
                name=f"Task {i}",
                content=f"Content for task {i}",
                tags=[f"tag{i}"]
            )
            self.store.save_entity(entity)
        
        # Test search performance
        start_time = time.time()
        results = self.store.search("Task", limit=10)
        search_time = time.time() - start_time
        
        assert len(results) >= 1
        # Search should be fast (under 1 second)
        assert search_time < 1.0


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Set up test environment."""
        self.store = create_test_memory_store(enable_vector_search=False)
    
    def teardown_method(self):
        """Clean up test environment."""
        self.store.close()
    
    def test_invalid_entity_type(self):
        """Test handling of invalid entity type."""
        with pytest.raises(ValueError, match="Entity type must be one of"):
            entity = MemoryEntity(
                type="invalid_type",
                name="Test"
            )
            self.store.save_entity(entity)
    
    def test_invalid_relation_type(self):
        """Test handling of invalid relation type."""
        # Create valid entities first
        entity1 = self.store.save_entity(MemoryEntity(type="task", name="Task 1"))
        entity2 = self.store.save_entity(MemoryEntity(type="task", name="Task 2"))
        
        with pytest.raises(ValueError, match="Relation type must be one of"):
            relation = MemoryRelation(
                source_id=entity1.id,
                target_id=entity2.id,
                relation_type="invalid_relation"
            )
            self.store.save_relation(relation)
    
    def test_large_content_handling(self):
        """Test handling of large content fields."""
        large_content = "x" * 10000  # 10KB content
        
        entity = MemoryEntity(
            type="note",
            name="Large Note",
            content=large_content
        )
        
        saved_entity = self.store.save_entity(entity)
        retrieved_entity = self.store.get_entity(saved_entity.id)
        
        assert retrieved_entity.content == large_content
    
    def test_special_characters(self):
        """Test handling of special characters in content."""
        special_content = "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        entity = MemoryEntity(
            type="note",
            name="Special Note",
            content=special_content
        )
        
        saved_entity = self.store.save_entity(entity)
        retrieved_entity = self.store.get_entity(saved_entity.id)
        
        assert retrieved_entity.content == special_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 