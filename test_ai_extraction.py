"""
Tests for AI Entity Extraction & Enhancement.
Phase 2.2: AI-powered content analysis and entity extraction.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from ai_extraction import AIExtractor, EntityMatcher, ContentEnhancer
from core import UnifiedMemoryStore
from models import MemoryEntity, MemoryContext


class TestAIExtractor:
    """Test AI entity extraction functionality."""
    
    def test_extract_people_regex(self):
        """Test person name extraction using regex."""
        extractor = AIExtractor(use_spacy=False)
        
        text = "John Smith and Sarah Johnson discussed the project with Mike Wilson."
        people = extractor._extract_people_regex(text)
        
        assert len(people) >= 3
        names = [name for name, _ in people]
        assert "John Smith" in names
        assert "Sarah Johnson" in names
        assert "Mike Wilson" in names
    
    def test_extract_people_false_positives(self):
        """Test that common false positives are filtered out."""
        extractor = AIExtractor(use_spacy=False)
        
        text = "We're using React and Python for the project. Docker is also involved."
        people = extractor._extract_people_regex(text)
        
        names = [name for name, _ in people]
        assert "React" not in names
        assert "Python" not in names
        assert "Docker" not in names
    
    def test_extract_technologies(self):
        """Test technology extraction."""
        extractor = AIExtractor()
        
        text = "We're using React, TypeScript, and PostgreSQL for the backend."
        technologies = extractor._extract_technologies(text)
        
        tech_names = [tech for tech, _ in technologies]
        assert "React" in tech_names
        assert "TypeScript" in tech_names
        assert "PostgreSQL" in tech_names
    
    def test_extract_file_references(self):
        """Test file reference extraction."""
        extractor = AIExtractor()
        
        text = "Check the main.py file and the utils/helper.js module."
        files = extractor._extract_file_references(text)
        
        file_names = [file for file, _ in files]
        assert "main.py" in file_names
        assert "utils/helper.js" in file_names
    
    def test_extract_projects(self):
        """Test project extraction."""
        extractor = AIExtractor()
        
        text = "We're working on the Ecommerce project and the Analytics platform."
        projects = extractor._extract_projects(text)
        
        project_names = [project for project, _ in projects]
        assert "Ecommerce" in project_names
        assert "Analytics" in project_names
    
    def test_extract_topics(self):
        """Test topic extraction."""
        extractor = AIExtractor()
        
        text = "We had a debugging session and discussed the API performance issues."
        topics = extractor.extract_topics(text)
        
        assert "debugging" in topics
        assert "api" in topics
        assert "performance" in topics
    
    def test_generate_summary(self):
        """Test summary generation."""
        extractor = AIExtractor()
        
        long_text = """
        We had a long meeting today about the new feature implementation. 
        The team discussed various approaches and decided to use React for the frontend.
        We also identified several performance issues that need to be addressed.
        The next steps include setting up the development environment and creating the initial components.
        """
        
        summary = extractor.generate_summary(long_text, max_length=100)
        
        assert len(summary) <= 103  # Allow for "..."
        assert "meeting" in summary.lower()
    
    def test_extract_action_items(self):
        """Test action item extraction."""
        extractor = AIExtractor()
        
        text = """
        We need to fix the bug in the authentication system.
        Action item: Set up the new database schema.
        Next steps: Deploy the updated API endpoints.
        """
        
        actions = extractor.extract_action_items(text)
        
        assert len(actions) >= 2
        assert any("fix" in action.lower() for action in actions)
        assert any("database" in action.lower() for action in actions)
    
    def test_content_hash_calculation(self):
        """Test content hash calculation for caching."""
        extractor = AIExtractor()
        
        text1 = "Hello world"
        text2 = "Hello world"
        text3 = "Different content"
        
        hash1 = extractor.calculate_content_hash(text1)
        hash2 = extractor.calculate_content_hash(text2)
        hash3 = extractor.calculate_content_hash(text3)
        
        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 40  # SHA-1 hash length


class TestEntityMatcher:
    """Test entity matching functionality."""
    
    @pytest.fixture
    def mock_memory_store(self):
        """Create a mock memory store for testing."""
        store = Mock()
        
        # Mock search results - return different results for different queries
        def mock_search(query, filters=None, limit=10):
            if query == 'John Smith' and filters and filters.get('type') == 'person':
                return [{'id': '1', 'name': 'John Smith', 'type': 'person'}]
            elif query == 'Sarah Johnson' and filters and filters.get('type') == 'person':
                return [{'id': '2', 'name': 'Sarah Johnson', 'type': 'person'}]
            elif query == 'React' and filters and filters.get('type') == 'technology':
                return [{'id': '3', 'name': 'React', 'type': 'technology'}]
            else:
                return []
        
        store.search = mock_search
        return store
    
    @pytest.fixture
    def matcher(self, mock_memory_store):
        """Create entity matcher with mock store."""
        return EntityMatcher(mock_memory_store)
    
    def test_find_similar_entities_exact_match(self, matcher):
        """Test exact entity matching."""
        candidates = [
            {'type': 'person', 'name': 'John Smith', 'confidence': 0.9}
        ]
        
        matches = matcher.find_similar_entities(candidates)
        
        assert len(matches) == 1
        assert matches[0]['action'] == 'link'
        assert matches[0]['existing_id'] == '1'
        assert matches[0]['similarity'] > 0.8
    
    def test_find_similar_entities_no_match(self, matcher):
        """Test when no similar entities are found."""
        candidates = [
            {'type': 'person', 'name': 'Unknown Person', 'confidence': 0.9}
        ]
        
        matches = matcher.find_similar_entities(candidates)
        
        assert len(matches) == 1
        assert matches[0]['action'] == 'create'
    
    def test_name_similarity_calculation(self, matcher):
        """Test name similarity calculation."""
        # Exact match
        similarity = matcher._calculate_name_similarity("John Smith", "John Smith")
        assert similarity == 1.0
        
        # Partial match
        similarity = matcher._calculate_name_similarity("John Smith", "John")
        assert similarity >= 0.7
        
        # No match
        similarity = matcher._calculate_name_similarity("John Smith", "Jane Doe")
        assert similarity < 0.8


class TestContentEnhancer:
    """Test content enhancement functionality."""
    
    @pytest.fixture
    def mock_memory_store(self):
        """Create a mock memory store."""
        return Mock()
    
    @pytest.fixture
    def extractor(self):
        """Create AI extractor."""
        return AIExtractor(use_spacy=False)
    
    @pytest.fixture
    def matcher(self, mock_memory_store):
        """Create entity matcher."""
        return EntityMatcher(mock_memory_store)
    
    @pytest.fixture
    def enhancer(self, mock_memory_store, extractor, matcher):
        """Create content enhancer."""
        return ContentEnhancer(mock_memory_store, extractor, matcher)
    
    def test_enhance_context_new_content(self, enhancer):
        """Test enhancing context with new content."""
        context = MemoryContext(
            type="handoff",
            content="John Smith discussed the React project with Sarah Johnson."
        )
        
        # Mock the search method to return empty results (no existing entities)
        enhancer.memory_store.search.return_value = []
        
        enhancement = enhancer.enhance_context(context)
        
        assert 'topics' in enhancement
        assert 'extracted_entities' in enhancement
        assert 'extract_hash' in enhancement
        assert len(enhancement['extracted_entities']) >= 2  # John Smith, Sarah Johnson
    
    def test_enhance_context_cached_content(self, enhancer):
        """Test that cached content skips re-extraction."""
        context = MemoryContext(
            type="handoff",
            content="John Smith discussed the React project.",
            metadata={'extract_hash': 'test_hash'}
        )
        
        # Mock the extractor to return a specific hash
        enhancer.extractor.calculate_content_hash = Mock(return_value='test_hash')
        
        enhancement = enhancer.enhance_context(context)
        
        # Should use cached results
        assert enhancement['topics'] == context.topics
        assert enhancement['summary'] == context.summary
    
    def test_create_content_relationships(self, enhancer):
        """Test creating relationships from extracted entities."""
        extracted_entities = [
            {
                'type': 'person',
                'name': 'John Smith',
                'action': 'link',
                'existing_id': '1',
                'confidence': 0.9,
                'similarity': 0.95
            }
        ]
        
        relationships = enhancer.create_content_relationships('context_1', extracted_entities)
        
        assert len(relationships) == 1
        relation = relationships[0]
        assert relation['source_id'] == 'context_1'
        assert relation['target_id'] == '1'
        assert relation['relation_type'] == 'mentions'
        assert relation['metadata']['auto_generated'] is True
    
    def test_determine_relation_type(self, enhancer):
        """Test relationship type determination."""
        entity_data = {'type': 'technology', 'name': 'React'}
        relation_type = enhancer._determine_relation_type(entity_data)
        assert relation_type == 'references'
        
        entity_data = {'type': 'file', 'name': 'main.py'}
        relation_type = enhancer._determine_relation_type(entity_data)
        assert relation_type == 'references'


class TestAIExtractionIntegration:
    """Integration tests for AI extraction with UnifiedMemoryStore."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_store(self, temp_dir):
        """Create memory store with AI extraction enabled."""
        db_path = temp_dir / "test_ai.db"
        return UnifiedMemoryStore(
            db_path=db_path,
            enable_vector_search=False,  # Disable for faster tests
            enable_ai_extraction=True
        )
    
    def test_save_context_with_ai_enhancement(self, memory_store):
        """Test saving context with AI enhancement."""
        context = MemoryContext(
            type="handoff",
            content="""
            John Smith and Sarah Johnson discussed the React project at length during our weekly meeting.
            They decided to use TypeScript for better type safety and discussed the benefits of static typing.
            The team also reviewed the current architecture and identified several areas for improvement.
            Action item: Set up the development environment with proper TypeScript configuration.
            Next steps: Create the initial components in src/components/ and implement the authentication system.
            We also need to consider the database schema changes and API endpoint modifications.
            The project timeline has been updated to reflect these new requirements and dependencies.
            """
        )
        
        saved_context = memory_store.save_context(context)
        
        # Check that AI enhancement was applied
        assert saved_context.topics
        # Summary is only generated for content > 300 characters
        if len(context.content) > 300:
            assert saved_context.summary
        assert 'action_items' in saved_context.metadata
        assert 'extracted_entities' in saved_context.metadata
        assert 'extract_hash' in saved_context.metadata
        
        # Check that entities were created
        assert len(saved_context.entity_ids) > 0
    
    def test_extract_entities_from_text(self, memory_store):
        """Test entity extraction from text."""
        text = "John Smith is working on the React project with Sarah Johnson."
        
        entities = memory_store.extract_entities_from_text(text)
        
        assert len(entities) >= 2
        entity_types = [entity['type'] for entity in entities]
        assert 'person' in entity_types
        assert 'technology' in entity_types
    
    def test_extract_topics_from_text(self, memory_store):
        """Test topic extraction from text."""
        text = "We had a debugging session and discussed API performance issues."
        
        topics = memory_store.extract_topics_from_text(text)
        
        assert len(topics) >= 2
        assert 'debugging' in topics
        assert 'api' in topics
    
    def test_generate_summary(self, memory_store):
        """Test summary generation."""
        long_text = """
        We had a comprehensive meeting today about the new feature implementation.
        The team discussed various approaches and decided to use React for the frontend.
        We also identified several performance issues that need to be addressed.
        The next steps include setting up the development environment and creating the initial components.
        """
        
        summary = memory_store.generate_summary(long_text, max_length=100)
        
        assert len(summary) <= 103
        assert "meeting" in summary.lower()
    
    def test_extract_action_items(self, memory_store):
        """Test action item extraction."""
        text = """
        We need to fix the authentication bug.
        Action item: Set up the database schema.
        Next steps: Deploy the API endpoints.
        """
        
        actions = memory_store.extract_action_items(text)
        
        assert len(actions) >= 2
        assert any("fix" in action.lower() for action in actions)
        assert any("database" in action.lower() for action in actions)
    
    def test_ai_extraction_disabled(self, temp_dir):
        """Test behavior when AI extraction is disabled."""
        db_path = temp_dir / "test_no_ai.db"
        memory_store = UnifiedMemoryStore(
            db_path=db_path,
            enable_ai_extraction=False
        )
        
        text = "John Smith discussed the React project."
        
        # Should return empty results when AI extraction is disabled
        entities = memory_store.extract_entities_from_text(text)
        topics = memory_store.extract_topics_from_text(text)
        actions = memory_store.extract_action_items(text)
        
        assert entities == []
        assert topics == []
        assert actions == []
    
    def test_graceful_fallback_on_extraction_error(self, memory_store):
        """Test graceful handling of extraction errors."""
        # Mock the extractor to raise an exception
        with patch.object(memory_store.ai_extractor, 'extract_entities', side_effect=Exception("Test error")):
            entities = memory_store.extract_entities_from_text("Test text")
            assert entities == []
    
    def test_relationship_creation(self, memory_store):
        """Test that relationships are created for linked entities."""
        # First, create some entities
        person_entity = MemoryEntity(
            type="person",
            name="John Smith",
            content="Team member"
        )
        saved_person = memory_store.save_entity(person_entity)
        
        # Create context that mentions the person
        context = MemoryContext(
            type="handoff",
            content="John Smith discussed the project requirements."
        )
        
        saved_context = memory_store.save_context(context)
        
        # Check that relationships were created
        related = memory_store.get_related(saved_context.id)
        assert len(related) > 0
        
        # Should have relationship to John Smith
        person_relations = [r for r in related if r['id'] == saved_person.id]
        assert len(person_relations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 