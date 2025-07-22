"""
Comprehensive test suite for Phase 1.1: Database Schema & Core Models
"""

import tempfile
import pytest
from pathlib import Path
from datetime import datetime

from database import initialize_database
from models import MemoryEntity, MemoryRelation, MemoryContext, ENTITY_TYPES, RELATION_TYPES


class TestPhase1_1Deliverables:
    """Test all Phase 1.1 deliverables."""
    
    @pytest.fixture
    def db_manager(self):
        """Create a temporary database for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            db_manager = initialize_database(data_dir)
            yield db_manager
            db_manager.disconnect()
    
    def test_schema_creation(self, db_manager):
        """Test that all required tables are created."""
        # Verify schema
        assert db_manager.verify_schema(), "Schema verification failed"
        
        # Check that all required tables exist
        conn = db_manager.connect()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row['name'] for row in cursor.fetchall()}
        
        required_tables = {'entities', 'entity_data', 'entity_relations', 'contexts'}
        assert required_tables.issubset(tables), f"Missing tables: {required_tables - tables}"
    
    def test_entity_creation_and_storage(self, db_manager):
        """Test creating and storing entities."""
        conn = db_manager.connect()
        
        # Create test entities
        person = MemoryEntity(
            type="person",
            name="Alice Johnson",
            content="Software engineer working on authentication",
            tags=["engineer", "auth", "python"]
        )
        
        task = MemoryEntity(
            type="task",
            name="Implement OAuth2",
            content="Add OAuth2 authentication to the web application",
            tags=["auth", "oauth2", "security"]
        )
        
        # Insert into entities table first
        conn.execute("INSERT INTO entities (uuid) VALUES (?)", (person.id,))
        conn.execute("INSERT INTO entities (uuid) VALUES (?)", (task.id,))
        
        # Insert into entity_data table
        person_data = person.to_dict()
        conn.execute("""
            INSERT INTO entity_data (id, type, name, content, metadata, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            person_data['id'], person_data['type'], person_data['name'],
            person_data['content'], str(person_data['metadata']), person_data['tags'],
            person_data['created_at'], person_data['updated_at']
        ))
        
        task_data = task.to_dict()
        conn.execute("""
            INSERT INTO entity_data (id, type, name, content, metadata, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data['id'], task_data['type'], task_data['name'],
            task_data['content'], str(task_data['metadata']), task_data['tags'],
            task_data['created_at'], task_data['updated_at']
        ))
        
        conn.commit()
        
        # Verify entities were stored
        cursor = conn.execute("SELECT * FROM entity_data WHERE type = ?", ("person",))
        person_row = cursor.fetchone()
        assert person_row is not None, "Person entity not found"
        assert person_row['name'] == "Alice Johnson"
        
        cursor = conn.execute("SELECT * FROM entity_data WHERE type = ?", ("task",))
        task_row = cursor.fetchone()
        assert task_row is not None, "Task entity not found"
        assert task_row['name'] == "Implement OAuth2"
    
    def test_relation_creation_and_storage(self, db_manager):
        """Test creating and storing relations."""
        conn = db_manager.connect()
        
        # Create test entities first
        person = MemoryEntity(type="person", name="Bob")
        task = MemoryEntity(type="task", name="Fix bug")
        
        conn.execute("INSERT INTO entities (uuid) VALUES (?)", (person.id,))
        conn.execute("INSERT INTO entities (uuid) VALUES (?)", (task.id,))
        
        person_data = person.to_dict()
        task_data = task.to_dict()
        
        conn.execute("""
            INSERT INTO entity_data (id, type, name, content, metadata, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            person_data['id'], person_data['type'], person_data['name'],
            person_data['content'], str(person_data['metadata']), person_data['tags'],
            person_data['created_at'], person_data['updated_at']
        ))
        
        conn.execute("""
            INSERT INTO entity_data (id, type, name, content, metadata, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data['id'], task_data['type'], task_data['name'],
            task_data['content'], str(task_data['metadata']), task_data['tags'],
            task_data['created_at'], task_data['updated_at']
        ))
        
        # Create relation
        relation = MemoryRelation(
            source_id=task.id,
            target_id=person.id,
            relation_type="assigned_to",
            strength=0.9
        )
        
        relation_data = relation.to_dict()
        conn.execute("""
            INSERT INTO entity_relations (id, source_id, target_id, relation_type, strength, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            relation_data['id'], relation_data['source_id'], relation_data['target_id'],
            relation_data['relation_type'], relation_data['strength'],
            str(relation_data['metadata']), relation_data['created_at']
        ))
        
        conn.commit()
        
        # Verify relation was stored
        cursor = conn.execute("""
            SELECT * FROM entity_relations 
            WHERE source_id = ? AND target_id = ?
        """, (task.id, person.id))
        relation_row = cursor.fetchone()
        assert relation_row is not None, "Relation not found"
        assert relation_row['relation_type'] == "assigned_to"
        assert relation_row['strength'] == 0.9
    
    def test_context_creation_and_storage(self, db_manager):
        """Test creating and storing contexts."""
        conn = db_manager.connect()
        
        # Create test context
        context = MemoryContext(
            type="handoff",
            content="Discussed OAuth2 implementation with Alice. She will handle the authentication flow.",
            summary="OAuth2 implementation handoff",
            topics=["oauth2", "authentication", "handoff"],
            entity_ids=["person-1", "task-1"]
        )
        
        context_data = context.to_dict()
        conn.execute("""
            INSERT INTO contexts (id, type, content, summary, topics, entity_ids, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            context_data['id'], context_data['type'], context_data['content'],
            context_data['summary'], context_data['topics'], context_data['entity_ids'],
            str(context_data['metadata']), context_data['created_at']
        ))
        
        conn.commit()
        
        # Verify context was stored
        cursor = conn.execute("SELECT * FROM contexts WHERE type = ?", ("handoff",))
        context_row = cursor.fetchone()
        assert context_row is not None, "Context not found"
        assert "OAuth2" in context_row['content']
        assert context_row['summary'] == "OAuth2 implementation handoff"
    
    def test_indexes_created(self, db_manager):
        """Test that all required indexes are created."""
        conn = db_manager.connect()
        
        # Check entity_data indexes
        cursor = conn.execute("PRAGMA index_list(entity_data)")
        entity_data_indexes = {row['name'] for row in cursor.fetchall()}
        expected_entity_indexes = {
            'idx_entity_data_type_created',
            'idx_entity_data_tags', 
            'idx_entity_data_name'
        }
        assert expected_entity_indexes.issubset(entity_data_indexes), \
            f"Missing entity_data indexes: {expected_entity_indexes - entity_data_indexes}"
        
        # Check entity_relations indexes
        cursor = conn.execute("PRAGMA index_list(entity_relations)")
        entity_relations_indexes = {row['name'] for row in cursor.fetchall()}
        expected_relation_indexes = {
            'idx_entity_relations_source',
            'idx_entity_relations_target',
            'idx_entity_relations_type'
        }
        assert expected_relation_indexes.issubset(entity_relations_indexes), \
            f"Missing entity_relations indexes: {expected_relation_indexes - entity_relations_indexes}"
        
        # Check contexts indexes
        cursor = conn.execute("PRAGMA index_list(contexts)")
        contexts_indexes = {row['name'] for row in cursor.fetchall()}
        expected_context_indexes = {'idx_contexts_type_created'}
        assert expected_context_indexes.issubset(contexts_indexes), \
            f"Missing contexts indexes: {expected_context_indexes - contexts_indexes}"
    
    def test_model_validation(self):
        """Test that all model validations work correctly."""
        # Test all entity types
        for entity_type in ENTITY_TYPES.keys():
            entity = MemoryEntity(type=entity_type, name=f"Test {entity_type}")
            assert entity.type == entity_type
        
        # Test all relation types
        for relation_type in RELATION_TYPES.keys():
            relation = MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type=relation_type
            )
            assert relation.relation_type == relation_type
        
        # Test invalid types raise errors
        with pytest.raises(ValueError):
            MemoryEntity(type="invalid_type", name="Test")
        
        with pytest.raises(ValueError):
            MemoryRelation(
                source_id="entity-1",
                target_id="entity-2",
                relation_type="invalid_relation"
            )
    
    def test_model_serialization(self):
        """Test model serialization and deserialization."""
        # Test entity serialization
        entity = MemoryEntity(
            type="project",
            name="My Project",
            content="A test project",
            tags=["project", "test"],
            metadata={"status": "active"}
        )
        
        data = entity.to_dict()
        restored_entity = MemoryEntity.from_dict(data)
        
        assert restored_entity.type == entity.type
        assert restored_entity.name == entity.name
        assert restored_entity.content == entity.content
        assert restored_entity.tags == entity.tags
        assert restored_entity.metadata == entity.metadata
        
        # Test relation serialization
        relation = MemoryRelation(
            source_id="task-1",
            target_id="person-1",
            relation_type="assigned_to",
            strength=0.8,
            metadata={"priority": "high"}
        )
        
        data = relation.to_dict()
        restored_relation = MemoryRelation.from_dict(data)
        
        assert restored_relation.source_id == relation.source_id
        assert restored_relation.target_id == relation.target_id
        assert restored_relation.relation_type == relation.relation_type
        assert restored_relation.strength == relation.strength
        assert restored_relation.metadata == relation.metadata
        
        # Test context serialization
        context = MemoryContext(
            type="meeting",
            content="Team meeting about project",
            summary="Project discussion",
            topics=["project", "planning"],
            entity_ids=["person-1", "project-1"],
            metadata={"duration": "1 hour"}
        )
        
        data = context.to_dict()
        restored_context = MemoryContext.from_dict(data)
        
        assert restored_context.type == context.type
        assert restored_context.content == context.content
        assert restored_context.summary == context.summary
        assert restored_context.topics == context.topics
        assert restored_context.entity_ids == context.entity_ids
        assert restored_context.metadata == context.metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 