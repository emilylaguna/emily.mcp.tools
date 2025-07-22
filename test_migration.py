"""
Tests for Migration System

Tests migration from JSONL files to unified memory store with sample data.
"""

import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest

from core import UnifiedMemoryStore
from migration import MigrationManager
from models import MemoryEntity, MemoryRelation, MemoryContext


class TestMigrationSystem:
    """Test migration system functionality."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory with sample JSONL files."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample handoff data
        handoff_data = [
            {
                "id": 1,
                "context": "Working on API authentication. Need to implement OAuth2 flow for user login.",
                "created_at": "2024-01-15T10:30:00"
            },
            {
                "id": 2,
                "context": "Database connection timeout issue. PostgreSQL connections timing out after 30 seconds.",
                "created_at": "2024-01-16T14:20:00"
            }
        ]
        
        with open(temp_dir / "handoff.jsonl", 'w') as f:
            for item in handoff_data:
                f.write(json.dumps(item) + '\n')
        
        # Create sample todo data
        todo_data = [
            {
                "id": 1,
                "title": "Fix database connection timeout",
                "description": "PostgreSQL connections timing out after 30 seconds. Need to investigate connection pool settings.",
                "priority": "high",
                "status": "todo",
                "tags": ["database", "urgent"],
                "created_at": "2024-01-15T09:00:00"
            },
            {
                "id": 2,
                "title": "Implement OAuth2 authentication",
                "description": "Add OAuth2 flow for user authentication using Google and GitHub providers.",
                "priority": "medium",
                "status": "in_progress",
                "tags": ["auth", "security"],
                "created_at": "2024-01-14T16:00:00"
            }
        ]
        
        with open(temp_dir / "todo.jsonl", 'w') as f:
            for item in todo_data:
                f.write(json.dumps(item) + '\n')
        
        # Create sample memory graph data
        memory_data = [
            {
                "type": "entity",
                "id": "person_alice",
                "name": "Alice Johnson",
                "entity_type": "person",
                "metadata": {"role": "Frontend Developer"},
                "created_at": "2024-01-10T14:00:00"
            },
            {
                "type": "entity",
                "id": "project_website",
                "name": "Company Website",
                "entity_type": "project",
                "metadata": {"status": "active"},
                "created_at": "2024-01-10T14:02:00"
            },
            {
                "type": "relation",
                "source": "person_alice",
                "target": "project_website",
                "relation": "works_on",
                "strength": 0.8,
                "created_at": "2024-01-10T14:05:00"
            }
        ]
        
        with open(temp_dir / "memory_graph.jsonl", 'w') as f:
            for item in memory_data:
                f.write(json.dumps(item) + '\n')
        
        # Create sample knowledgebase data
        kb_data = [
            {
                "id": "file_api_auth_py",
                "type": "file",
                "path": "src/auth/authentication.py",
                "content": "Contains OAuth2 implementation for user authentication",
                "functions": ["authenticate_user", "validate_token"],
                "created_at": "2024-01-12T16:00:00"
            },
            {
                "id": "file_db_config_js",
                "type": "file",
                "path": "config/database.js",
                "content": "Database configuration and connection pool settings",
                "functions": ["createConnection", "getConnectionPool"],
                "created_at": "2024-01-13T11:00:00"
            }
        ]
        
        with open(temp_dir / "knowledgebase.jsonl", 'w') as f:
            for item in kb_data:
                f.write(json.dumps(item) + '\n')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path."""
        temp_dir = Path(tempfile.mkdtemp())
        db_path = temp_dir / "test_migration.db"
        yield db_path
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_store(self, temp_db_path):
        """Create memory store instance."""
        return UnifiedMemoryStore(str(temp_db_path), enable_vector_search=False, enable_ai_extraction=False)
    
    @pytest.fixture
    def migration_manager(self, memory_store, temp_data_dir):
        """Create migration manager instance."""
        return MigrationManager(memory_store, temp_data_dir)
    
    def test_migration_manager_initialization(self, migration_manager, temp_data_dir):
        """Test migration manager initialization."""
        assert migration_manager.data_dir == temp_data_dir
        assert migration_manager.migration_log == []
        assert migration_manager.memory_store is not None
    
    def test_backup_creation(self, migration_manager):
        """Test backup creation functionality."""
        backup_path = migration_manager.create_backup()
        
        assert Path(backup_path).exists()
        assert (Path(backup_path) / "handoff.jsonl").exists()
        assert (Path(backup_path) / "todo.jsonl").exists()
        assert (Path(backup_path) / "memory_graph.jsonl").exists()
        assert (Path(backup_path) / "knowledgebase.jsonl").exists()
    
    def test_handoff_migration(self, migration_manager):
        """Test handoff data migration."""
        result = migration_manager.migrate_handoff()
        
        assert result['status'] == 'completed'
        assert result['migrated_count'] == 2
        assert result['error_count'] == 0
        assert len(result['migrated_ids']) == 2
        
        # Verify contexts were created
        contexts = migration_manager.memory_store.search_contexts("", filters={"type": "handoff"})
        assert len(contexts) == 2
        
        # Find the context with original_id 1 (API authentication)
        context1 = None
        for context in contexts:
            if context.metadata['original_id'] == 1:
                context1 = context
                break
        
        assert context1 is not None
        assert context1.type == "handoff"
        assert "API authentication" in context1.content
        assert context1.metadata['migrated_from'] == 'handoff.jsonl'
        assert context1.metadata['original_id'] == 1
    
    def test_todo_migration(self, migration_manager):
        """Test todo data migration."""
        result = migration_manager.migrate_todo()
        
        assert result['status'] == 'completed'
        assert result['migrated_count'] == 2
        assert result['error_count'] == 0
        assert len(result['migrated_ids']) == 2
        
        # Verify tasks were created
        tasks = migration_manager.memory_store.search_entities("task")
        assert len(tasks) == 2
        
        # Check first task
        task1 = tasks[0]
        assert task1.type == "task"
        assert "database connection timeout" in task1.name.lower()
        assert task1.metadata['priority'] == 'high'
        assert task1.metadata['status'] == 'todo'
        assert 'database' in task1.tags
        assert task1.metadata['migrated_from'] == 'todo.jsonl'
    
    def test_memory_graph_migration(self, migration_manager):
        """Test memory graph data migration."""
        result = migration_manager.migrate_memory_graph()
        
        assert result['status'] == 'completed'
        assert result['migrated_entities'] == 2
        assert result['migrated_relations'] == 1
        assert result['error_count'] == 0
        
        # Verify entities were created
        entities = migration_manager.memory_store.search_entities("person")
        assert len(entities) == 1
        
        entities = migration_manager.memory_store.search_entities("project")
        assert len(entities) == 1
        
        # Check person entity
        person = entities[0] if entities[0].type == "person" else entities[1]
        assert person.name == "Alice Johnson"
        assert person.metadata['role'] == "Frontend Developer"
        assert person.metadata['migrated_from'] == 'memory_graph.jsonl'
        
        # Verify relations were created
        relations = migration_manager.memory_store.get_relations_by_type("works_on")
        assert len(relations) == 1
    
    def test_knowledgebase_migration(self, migration_manager):
        """Test knowledgebase data migration."""
        result = migration_manager.migrate_knowledgebase()
        
        assert result['status'] == 'completed'
        assert result['migrated_files'] == 2
        assert result['migrated_functions'] == 4  # 2 files * 2 functions each
        assert result['error_count'] == 0
        
        # Verify file entities were created
        files = migration_manager.memory_store.search_entities("file")
        assert len(files) == 2
        
        # Check first file
        file1 = files[0]
        assert file1.type == "file"
        assert "authentication.py" in file1.name
        assert file1.metadata['language'] == 'python'
        assert file1.metadata['migrated_from'] == 'knowledgebase.jsonl'
        
        # Verify function entities were created
        functions = migration_manager.memory_store.search_entities("function")
        assert len(functions) == 4
        
        # Verify file-function relationships
        relations = migration_manager.memory_store.get_relations_by_type("contains")
        assert len(relations) == 4  # 2 files * 2 functions each
    
    def test_full_migration(self, migration_manager):
        """Test complete migration process."""
        result = migration_manager.migrate_all(backup=True)
        
        assert result['summary']['tools_processed'] == 4
        assert result['summary']['tools_successful'] == 4
        assert result['summary']['tools_failed'] == 0
        assert result['summary']['total_records_migrated'] > 0
        assert result['summary']['total_errors'] == 0
        assert result['validation']['validation_passed'] == True
        
        # Verify all data types were migrated
        validation = result['validation']
        assert validation['database_counts']['entities'] > 0
        assert validation['database_counts']['relations'] > 0
        assert validation['database_counts']['contexts'] > 0
    
    def test_incremental_migration(self, migration_manager):
        """Test single tool migration."""
        # Test handoff migration
        result = migration_manager.migrate_incremental('handoff')
        assert result['status'] == 'completed'
        assert result['migrated_count'] == 2
        
        # Test todo migration
        result = migration_manager.migrate_incremental('todo')
        assert result['status'] == 'completed'
        assert result['migrated_count'] == 2
        
        # Test invalid tool
        result = migration_manager.migrate_incremental('invalid_tool')
        assert result['status'] == 'error'
        assert 'Unknown tool' in result['message']
    
    def test_migration_with_missing_files(self, memory_store, temp_db_path):
        """Test migration when some files are missing."""
        # Create migration manager with empty directory
        empty_dir = Path(tempfile.mkdtemp())
        migration_manager = MigrationManager(memory_store, empty_dir)
        
        result = migration_manager.migrate_all(backup=False)
        
        assert result['summary']['tools_processed'] == 4
        assert result['summary']['tools_successful'] == 0
        assert result['summary']['tools_failed'] == 0  # Skipped, not failed
        
        # All tools should be skipped
        for tool_result in result['results'].values():
            assert tool_result['status'] == 'skipped'
            assert tool_result['reason'] == 'file not found'
        
        shutil.rmtree(empty_dir)
    
    def test_migration_validation(self, migration_manager):
        """Test migration validation functionality."""
        # Run migration first
        migration_manager.migrate_all(backup=False)
        
        # Test validation
        validation = migration_manager.validate_migration({
            'handoff': {'status': 'completed', 'migrated_count': 2},
            'todo': {'status': 'completed', 'migrated_count': 2}
        })
        
        assert validation['total_records_migrated'] == 4
        assert validation['total_errors'] == 0
        assert validation['validation_passed'] == True
        assert len(validation['tools_migrated']) == 2
        assert 'database_counts' in validation
    
    def test_migration_with_errors(self, memory_store, temp_data_dir):
        """Test migration handling of malformed data."""
        # Add malformed data to handoff file
        with open(temp_data_dir / "handoff.jsonl", 'a') as f:
            f.write("invalid json data\n")
            f.write('{"id": 3, "context": "valid data"}\n')
        
        migration_manager = MigrationManager(memory_store, temp_data_dir)
        result = migration_manager.migrate_handoff()
        
        assert result['status'] == 'completed'
        assert result['migrated_count'] == 3  # Original 2 + 1 valid
        assert result['error_count'] == 1  # 1 malformed line
        assert len(result['errors']) == 1
        assert "Line 3" in result['errors'][0]  # Invalid JSON on line 3
    
    def test_timestamp_preservation(self, migration_manager):
        """Test that original timestamps are preserved during migration."""
        result = migration_manager.migrate_handoff()
        
        assert result['status'] == 'completed'
        
        # Check that timestamps were preserved
        contexts = migration_manager.memory_store.search_contexts("", filters={"type": "handoff"})
        assert len(contexts) == 2
        
        # Find the context with original ID 1
        context1 = None
        for context in contexts:
            if context.metadata['original_id'] == 1:
                context1 = context
                break
        
        assert context1 is not None
        expected_time = datetime.fromisoformat("2024-01-15T10:30:00")
        assert context1.created_at == expected_time
    
    def test_entity_extraction_from_tasks(self, migration_manager):
        """Test that entities are extracted from task content during migration."""
        result = migration_manager.migrate_todo()
        
        assert result['status'] == 'completed'
        
        # Check that entities were extracted from task content
        # The task mentions "PostgreSQL" and "OAuth2" which should be extracted
        extracted_entities = migration_manager.memory_store.search_entities("tech")
        assert len(extracted_entities) > 0
        
        # Check that relationships were created
        relations = migration_manager.memory_store.get_relations_by_type("relates_to")
        assert len(relations) > 0
    
    def test_language_detection(self, migration_manager):
        """Test programming language detection in knowledgebase migration."""
        result = migration_manager.migrate_knowledgebase()
        
        assert result['status'] == 'completed'
        
        # Check language detection
        files = migration_manager.memory_store.search_entities("file")
        python_file = None
        js_file = None
        
        for file in files:
            if "authentication.py" in file.name:
                python_file = file
            elif "database.js" in file.name:
                js_file = file
        
        assert python_file is not None
        assert python_file.metadata['language'] == 'python'
        
        assert js_file is not None
        assert js_file.metadata['language'] == 'javascript'


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 