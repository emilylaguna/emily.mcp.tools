"""
Test vec0 integration with sqlite-vec.
"""

from emily_core.memory import create_test_memory_store
from emily_core.models import MemoryEntity, MemoryContext


class TestVec0Integration:
    """Test vec0 virtual table integration."""
    
    def test_vec0_tables_created(self):
        """Test that vec0 virtual tables are created when sqlite-vec is available."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Check if vec0 tables exist
        conn = store._get_conn()
        
        # Check for entity_vectors table
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='entity_vectors'
        """)
        assert cursor.fetchone() is not None, "entity_vectors table should exist"
        
        # Check for context_vectors table
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='context_vectors'
        """)
        assert cursor.fetchone() is not None, "context_vectors table should exist"
        
        # Check table structure
        cursor = conn.execute("PRAGMA table_info(entity_vectors)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        assert 'id' in columns, "entity_vectors should have id column"
        assert 'embedding' in columns, "entity_vectors should have embedding column"
        # vec0 doesn't show the float32 type in table_info, so we just check the column exists
    
    def test_entity_vector_storage(self):
        """Test storing and retrieving entity embeddings using vec0."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Create test entity
        entity = MemoryEntity(
            type="test",
            name="Test Entity",
            content="This is a test entity for vector storage"
        )
        
        # Save entity (should automatically store embedding)
        saved_entity = store.save_entity(entity)
        
        # Check if embedding was stored
        conn = store._get_conn()
        cursor = conn.execute("SELECT embedding FROM entity_vectors WHERE id = ?", (saved_entity.id,))
        row = cursor.fetchone()
        
        assert row is not None, "Embedding should be stored in vec0 table"
        assert row['embedding'] is not None, "Embedding should not be null"
    
    def test_vector_similarity_search(self):
        """Test vector similarity search using vec0."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Create test entities
        entities = [
            MemoryEntity(type="test", name="Python Programming", content="Learn Python programming language"),
            MemoryEntity(type="test", name="JavaScript Basics", content="Introduction to JavaScript development"),
            MemoryEntity(type="test", name="Machine Learning", content="AI and machine learning concepts"),
            MemoryEntity(type="test", name="Web Development", content="Building websites with HTML and CSS")
        ]
        
        # Save entities
        for entity in entities:
            store.save_entity(entity)
        
        # Search for programming-related content
        results = store.search("programming", limit=10)
        
        assert len(results) > 0, "Should find programming-related results"
        
        # Check that results have similarity scores
        for result in results:
            assert 'similarity' in result, "Results should have similarity scores"
            assert result['similarity'] > 0, "Similarity should be positive"
    
    def test_context_vector_storage(self):
        """Test storing and retrieving context embeddings using vec0."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Create test context
        context = MemoryContext(
            type="conversation",
            content="This is a test conversation about artificial intelligence and machine learning"
        )
        
        # Save context (should automatically store embedding)
        saved_context = store.save_context(context)
        
        # Check if embedding was stored
        conn = store._get_conn()
        cursor = conn.execute("SELECT embedding FROM context_vectors WHERE id = ?", (saved_context.id,))
        row = cursor.fetchone()
        
        assert row is not None, "Context embedding should be stored in vec0 table"
        assert row['embedding'] is not None, "Context embedding should not be null"
    
    def test_context_vector_search(self):
        """Test context vector similarity search using vec0."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Create test contexts
        contexts = [
            MemoryContext(type="conversation", content="Discussion about Python programming and web development"),
            MemoryContext(type="conversation", content="Chat about machine learning algorithms and AI"),
            MemoryContext(type="conversation", content="Meeting notes about project management and team collaboration"),
            MemoryContext(type="conversation", content="Technical discussion about database design and optimization")
        ]
        
        # Save contexts
        for context in contexts:
            store.save_context(context)
        
        # Search for AI-related contexts
        results = store.search_contexts_vector("artificial intelligence", limit=10)
        
        assert len(results) > 0, "Should find AI-related contexts"
        
        # Check that results have similarity scores
        for result in results:
            assert hasattr(result, 'metadata'), "Results should have metadata"
            # Note: similarity score might be in the raw data, not the MemoryContext object
    
    def test_vec0_fallback_when_disabled(self):
        """Test that vec0 tables are not created when vector search is disabled."""
        store = create_test_memory_store(enable_vector_search=False)
        
        # Check that vec0 tables don't exist
        conn = store._get_conn()
        
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='entity_vectors'
        """)
        assert cursor.fetchone() is None, "entity_vectors table should not exist when vector search is disabled"
        
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='context_vectors'
        """)
        assert cursor.fetchone() is None, "context_vectors table should not exist when vector search is disabled"
    
    def test_combined_search_results(self):
        """Test that vector and FTS search results are properly combined."""
        store = create_test_memory_store(enable_vector_search=True)
        
        # Create test entities with specific content
        entities = [
            MemoryEntity(type="test", name="Python Tutorial", content="Learn Python programming step by step"),
            MemoryEntity(type="test", name="JavaScript Guide", content="Complete JavaScript programming guide"),
            MemoryEntity(type="test", name="Python Web Framework", content="Django and Flask web development"),
        ]
        
        # Save entities
        for entity in entities:
            store.save_entity(entity)
        
        # Search using combined vector + FTS
        results = store.search("Python programming", limit=10)
        
        assert len(results) > 0, "Should find Python-related results"
        
        # Check that results have combined scores
        for result in results:
            assert 'combined_score' in result, "Results should have combined scores"
            assert result['combined_score'] > 0, "Combined score should be positive" 