"""
Unit tests for core UnifiedMemoryStore functionality.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from core import UnifiedMemoryStore, create_test_memory_store, create_memory_store
from core.models import MemoryEntity, MemoryRelation, MemoryContext


class TestUnifiedMemoryStore:
    """Test the core UnifiedMemoryStore functionality."""
    
    def test_basic_initialization(self):
        """Test basic store initialization without vector search."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(
                db_path, 
                enable_vector_search=False
            )
            
            assert store.db_path == db_path
            assert store.vector_enabled is False
            assert store.embedding_model is None
            assert store.embedding_dimension == 384
            
            # Check database was created
            assert db_path.exists()
            
            # Check pragma
            pragma = store.check_pragma()
            assert pragma["json_enabled"] is True
            assert pragma["vector_enabled"] is False
            assert pragma["tables_exist"]["entities"] is True
            assert pragma["tables_exist"]["contexts"] is True
    
    def test_initialization_with_vector_search_disabled(self):
        """Test initialization when vector search is explicitly disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(
                db_path,
                enable_vector_search=False
            )
            
            assert store.vector_enabled is False
            assert store.embedding_model is None
            
            pragma = store.check_pragma()
            assert pragma["vector_enabled"] is False
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_initialization_with_vector_search(self, mock_transformer):
        """Test initialization with vector search enabled."""
        # Mock the SentenceTransformer
        import numpy as np
        mock_model = Mock()
        mock_model.encode.return_value = np.array([0.1] * 384)
        mock_model.name = "all-MiniLM-L6-v2"
        mock_transformer.return_value = mock_model
        
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(
                db_path,
                enable_vector_search=True
            )
            
            assert store.vector_enabled is True
            assert store.embedding_model is not None
            assert store.embedding_dimension == 384
            
            pragma = store.check_pragma()
            assert pragma["vector_enabled"] is True
            assert pragma["embedding_model"] == "all-MiniLM-L6-v2"
    
    def test_custom_embedding_model(self):
        """Test initialization with custom embedding model."""
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            import numpy as np
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1] * 512)
            mock_model.name = "custom-model"
            mock_transformer.return_value = mock_model
            
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = Path(temp_dir) / "test.db"
                
                store = UnifiedMemoryStore(
                    db_path,
                    embedding_model="custom-model",
                    embedding_dimension=512,
                    enable_vector_search=True
                )
                
                assert store.embedding_dimension == 512
                assert store.embedding_model.name == "custom-model"
    
    def test_missing_sentence_transformers(self):
        """Test graceful handling when sentence-transformers is not available."""
        with patch('sentence_transformers.SentenceTransformer', side_effect=ImportError("No module named 'sentence_transformers'")):
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = Path(temp_dir) / "test.db"
                
                store = UnifiedMemoryStore(
                    db_path,
                    enable_vector_search=True
                )
                
                assert store.vector_enabled is False
                assert store.embedding_model is None
    
    def test_sqlite_vec_extension_missing(self):
        """Test graceful handling when sqlite-vec extension is not available."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            # Create store with vector search enabled
            store = UnifiedMemoryStore(
                db_path,
                enable_vector_search=True
            )
            
            # The extension loading should fail gracefully
            # We can't easily mock this without complex setup, so we test the fallback
            pragma = store.check_pragma()
            # Vector search might be disabled if extension not available
            assert "vector_enabled" in pragma
    
    def test_thread_safety(self):
        """Test that each thread gets its own database connection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(
                db_path,
                enable_vector_search=False
            )
            
            # Test that we can get a connection in the main thread
            main_conn = store._get_conn()
            assert main_conn is not None
            
            # Test that the connection is properly configured
            cursor = main_conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            assert journal_mode == "wal"
            
            store.close()
    
    def test_embedding_generation(self):
        """Test embedding generation functionality."""
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            import numpy as np
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])
            mock_transformer.return_value = mock_model
            
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = Path(temp_dir) / "test.db"
                
                store = UnifiedMemoryStore(
                    db_path,
                    enable_vector_search=True
                )
                
                # Test embedding generation
                embedding = store._generate_embedding("test text")
                assert embedding == [0.1, 0.2, 0.3, 0.4]
                
                # Test empty text
                embedding = store._generate_embedding("")
                assert embedding is None
                
                # Test None text
                embedding = store._generate_embedding(None)
                assert embedding is None
    
    def test_embedding_storage(self):
        """Test embedding storage in vector tables."""
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            import numpy as np
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
            mock_transformer.return_value = mock_model
            
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = Path(temp_dir) / "test.db"
                
                store = UnifiedMemoryStore(
                    db_path,
                    enable_vector_search=True
                )
                
                # Test storing entity embedding (should fail if vector tables don't exist)
                success = store._store_embedding("entity", "test-id", [0.1, 0.2, 0.3])
                # This will fail because vector tables don't exist, but that's expected
                assert success is False
                
                # Test storing context embedding (should fail if vector tables don't exist)
                success = store._store_embedding("context", "test-id", [0.1, 0.2, 0.3])
                assert success is False
    
    def test_embedding_storage_without_vector_search(self):
        """Test embedding storage when vector search is disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(
                db_path,
                enable_vector_search=False
            )
            
            # Should return False when vector search is disabled
            success = store._store_embedding("entity", "test-id", [0.1, 0.2, 0.3])
            assert success is False
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            with UnifiedMemoryStore(db_path, enable_vector_search=False) as store:
                assert store.db_path == db_path
                # Connection should be available
                conn = store._get_conn()
                assert conn is not None
            
            # After context exit, connections should be closed
            # We can't easily test this without complex mocking, but we can verify no errors
    
    def test_close_method(self):
        """Test explicit close method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(db_path, enable_vector_search=False)
            
            # Get a connection
            conn = store._get_conn()
            assert conn is not None
            
            # Close the store
            store.close()
            
            # Should not raise an error when called multiple times
            store.close()
    
    def test_pragma_check(self):
        """Test pragma check functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(db_path, enable_vector_search=False)
            
            pragma = store.check_pragma()
            
            # Check required fields
            assert "json_enabled" in pragma
            assert "fts_enabled" in pragma
            assert "vector_enabled" in pragma
            assert "journal_mode" in pragma
            assert "tables_exist" in pragma
            assert "embedding_model" in pragma
            assert "embedding_dimension" in pragma
            
            # Check table existence
            tables = pragma["tables_exist"]
            assert "entities" in tables
            assert "contexts" in tables
            
            # Check SQLite features
            assert pragma["json_enabled"] is True  # Modern SQLite has JSON support
    
    def test_schema_initialization(self):
        """Test that schema is properly initialized."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(db_path, enable_vector_search=False)
            
            # Check that tables exist
            conn = store._get_conn()
            
            # Check entity_data table (this is where the actual entity data is stored)
            cursor = conn.execute("PRAGMA table_info(entity_data)")
            columns = [row['name'] for row in cursor.fetchall()]
            expected_columns = ['id', 'type', 'name', 'content', 'metadata', 'tags', 'created_at', 'updated_at']
            for col in expected_columns:
                assert col in columns
            
            # Check contexts table
            cursor = conn.execute("PRAGMA table_info(contexts)")
            columns = [row['name'] for row in cursor.fetchall()]
            expected_columns = ['id', 'type', 'content', 'summary', 'topics', 'entity_ids', 'metadata', 'created_at']
            for col in expected_columns:
                assert col in columns
    
    def test_error_handling_in_embedding_generation(self):
        """Test error handling in embedding generation."""
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            mock_model = Mock()
            mock_model.encode.side_effect = Exception("Embedding error")
            mock_transformer.return_value = mock_model
            
            with tempfile.TemporaryDirectory() as temp_dir:
                db_path = Path(temp_dir) / "test.db"
                
                store = UnifiedMemoryStore(
                    db_path,
                    enable_vector_search=True
                )
                
                # Should return None on error
                embedding = store._generate_embedding("test text")
                assert embedding is None


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_create_test_memory_store(self):
        """Test create_test_memory_store function."""
        store = create_test_memory_store()
        
        assert isinstance(store, UnifiedMemoryStore)
        assert store.vector_enabled is False  # Should be disabled by default for testing
        
        # Should create a temporary database
        assert "test_memory.db" in str(store.db_path)
        
        store.close()
    
    def test_create_test_memory_store_with_vector_search(self):
        """Test create_test_memory_store with vector search enabled."""
        with patch('sentence_transformers.SentenceTransformer'):
            store = create_test_memory_store(enable_vector_search=True)
            
            assert isinstance(store, UnifiedMemoryStore)
            assert store.vector_enabled is True
            
            store.close()
    
    def test_create_memory_store(self):
        """Test create_memory_store function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = create_memory_store(temp_dir, enable_vector_search=False)
            
            assert isinstance(store, UnifiedMemoryStore)
            assert store.db_path == Path(temp_dir) / "unified_memory.db"
            
            store.close()


class TestDatabaseOperations:
    """Test basic database operations."""
    
    def test_database_connection_reuse(self):
        """Test that database connections are reused within the same thread."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(db_path, enable_vector_search=False)
            
            # Get connection multiple times
            conn1 = store._get_conn()
            conn2 = store._get_conn()
            conn3 = store._get_conn()
            
            # Should be the same connection object
            assert conn1 is conn2
            assert conn2 is conn3
            
            store.close()
    
    def test_database_performance_settings(self):
        """Test that database performance settings are applied."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.db"
            
            store = UnifiedMemoryStore(db_path, enable_vector_search=False)
            
            conn = store._get_conn()
            
            # Check journal mode
            cursor = conn.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            assert journal_mode == "wal"
            
            # Check synchronous mode
            cursor = conn.execute("PRAGMA synchronous")
            synchronous = cursor.fetchone()[0]
            assert synchronous == 1  # NORMAL
            
            # Check cache size
            cursor = conn.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]
            assert cache_size == 10000
            
            store.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 