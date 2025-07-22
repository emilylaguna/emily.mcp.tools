"""
Unit tests for intelligent search and cross-domain intelligence features.
Phase 4.1: Semantic Search & Cross-Domain Intelligence
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from core import UnifiedMemoryStore, create_test_memory_store
from core.models import MemoryEntity, MemoryRelation, MemoryContext
from intelligence.search import IntelligentSearchEngine
from intelligence.smart_suggestions import SmartSuggestionsEngine
from intelligence.natural_query import NaturalQueryProcessor
from intelligence.search_mcp import IntelligentSearchMCPTools


# Shared memory store for all tests
@pytest.fixture(scope="session")
def shared_memory_store():
    """Create a shared memory store for all tests."""
    return create_test_memory_store(enable_ai_extraction=False)


class TestIntelligentSearchEngine:
    """Test the intelligent search engine."""
    
    @pytest.fixture
    def memory_store(self, shared_memory_store):
        """Use the shared memory store."""
        return shared_memory_store
    
    @pytest.fixture
    def search_engine(self, memory_store):
        """Create a test search engine."""
        return IntelligentSearchEngine(memory_store)
    
    @pytest.fixture
    def sample_data(self, memory_store):
        """Create sample data for testing."""
        # Create a project
        project = MemoryEntity(
            type="project",
            name="API Development",
            content="Building a new REST API for user management"
        )
        saved_project = memory_store.save_entity(project)
        
        # Create tasks
        task1 = MemoryEntity(
            type="task",
            name="Design API endpoints",
            content="Create OpenAPI specification for user endpoints",
            metadata={"status": "completed", "project_id": saved_project.id}
        )
        task2 = MemoryEntity(
            type="task",
            name="Implement authentication",
            content="Add JWT authentication to the API",
            metadata={"status": "in_progress", "project_id": saved_project.id}
        )
        saved_task1 = memory_store.save_entity(task1)
        saved_task2 = memory_store.save_entity(task2)
        
        # Create people
        person1 = MemoryEntity(
            type="person",
            name="Alice Johnson",
            content="Senior developer"
        )
        person2 = MemoryEntity(
            type="person",
            name="Bob Smith",
            content="Backend developer"
        )
        saved_person1 = memory_store.save_entity(person1)
        saved_person2 = memory_store.save_entity(person2)
        
        # Create conversations
        conv1 = MemoryContext(
            type="handoff",
            content="Discussed API design with Alice and Bob. Need to implement authentication using JWT tokens.",
            summary="API design discussion"
        )
        conv2 = MemoryContext(
            type="handoff",
            content="Bob mentioned using PostgreSQL for the database. Alice suggested using Redis for caching.",
            summary="Database discussion"
        )
        saved_conv1 = memory_store.save_context(conv1)
        saved_conv2 = memory_store.save_context(conv2)
        
        # Create relationships
        memory_store.save_relation(MemoryRelation(
            source_id=saved_project.id,
            target_id=saved_task1.id,
            relation_type="contains"
        ))
        memory_store.save_relation(MemoryRelation(
            source_id=saved_project.id,
            target_id=saved_task2.id,
            relation_type="contains"
        ))
        memory_store.save_relation(MemoryRelation(
            source_id=saved_person1.id,
            target_id=saved_conv1.id,
            relation_type="relates_to"
        ))
        memory_store.save_relation(MemoryRelation(
            source_id=saved_person2.id,
            target_id=saved_conv1.id,
            relation_type="relates_to"
        ))
        
        return {
            'project': saved_project,
            'tasks': [saved_task1, saved_task2],
            'people': [saved_person1, saved_person2],
            'conversations': [saved_conv1, saved_conv2]
        }
    
    def test_universal_search_basic(self, search_engine, sample_data):
        """Test basic universal search functionality."""
        results = search_engine.universal_search("API")
        
        assert isinstance(results, dict)
        assert len(results) > 0
        
        # Should find the project and tasks
        if 'project' in results:
            assert any('API' in p.get('name', '') for p in results['project'])
        if 'task' in results:
            assert any('API' in t.get('name', '') for t in results['task'])
    
    def test_universal_search_with_filters(self, search_engine, sample_data):
        """Test universal search with entity type filters."""
        results = search_engine.universal_search("API", entity_types=["project"])
        
        assert isinstance(results, dict)
        # Should only contain project results
        assert all(entity_type == "project" for entity_type in results.keys())
    
    def test_intent_based_search_timeline(self, search_engine, sample_data):
        """Test intent-based search for timeline queries."""
        results = search_engine.intent_based_search("Show me the timeline for API Development")
        
        assert isinstance(results, dict)
        assert results.get('intent') == 'timeline'
        assert 'timeline' in results
    
    def test_intent_based_search_expertise(self, search_engine, sample_data):
        """Test intent-based search for expertise queries."""
        results = search_engine.intent_based_search("Who knows about authentication")
        
        assert isinstance(results, dict)
        assert results.get('intent') == 'expertise_lookup'
        assert 'experts' in results
    
    def test_intent_based_search_project_status(self, search_engine, sample_data):
        """Test intent-based search for project status queries."""
        results = search_engine.intent_based_search("What's the status of API Development")
        
        assert isinstance(results, dict)
        assert results.get('intent') == 'project_status'
        assert 'intelligence' in results
    
    def test_get_project_intelligence(self, search_engine, sample_data):
        """Test project intelligence generation."""
        project_id = sample_data['project'].id
        intelligence = search_engine.get_project_intelligence(project_id)
        
        assert isinstance(intelligence, dict)
        assert 'project' in intelligence
        assert 'metrics' in intelligence
        assert 'insights' in intelligence
        assert 'ai_analysis' in intelligence
        
        # Check metrics
        metrics = intelligence['metrics']
        assert 'task_completion' in metrics
        assert 'conversation_volume' in metrics
        assert 'team_size' in metrics
    
    def test_find_expert_for_technology(self, search_engine, sample_data):
        """Test finding experts for specific technology."""
        experts = search_engine._find_expert_for_technology("authentication")
        
        assert isinstance(experts, list)
        # Should find people mentioned in conversations about authentication
        if experts:
            assert all('name' in expert for expert in experts)
            assert all('relevance_score' in expert for expert in experts)
    
    def test_intelligent_ranking(self, search_engine, sample_data):
        """Test intelligent ranking of search results."""
        # Create multiple result sets
        result_set1 = [{'id': '1', 'type': 'task', 'relevance_score': 0.8}]
        result_set2 = [{'id': '1', 'type': 'task', 'relevance_score': 0.6}]
        result_set3 = [{'id': '2', 'type': 'project', 'relevance_score': 0.9}]
        
        ranked_results = search_engine._intelligent_ranking(result_set1, result_set2, result_set3)
        
        assert len(ranked_results) == 2  # Two unique entities
        # Entity 1 should have higher score due to multiple matches
        assert ranked_results[0]['id'] == '1'
        assert ranked_results[0]['search_matches'] == 2
    
    def test_parse_search_intent(self, search_engine):
        """Test search intent parsing."""
        # Timeline intent
        intent = search_engine._parse_search_intent("Show me the timeline for project X")
        assert intent['type'] == 'timeline'
        assert intent['project'] == 'x'  # Lowercase due to query_lower
        
        # Expertise intent
        intent = search_engine._parse_search_intent("Who knows about Python")
        assert intent['type'] == 'expertise_lookup'
        assert intent['technology'] == 'python'  # Lowercase due to query_lower
        
        # Related content intent
        intent = search_engine._parse_search_intent("Find content related to authentication")
        assert intent['type'] == 'find_related'
        
        # Project status intent
        intent = search_engine._parse_search_intent("What's the status of project Y")
        assert intent['type'] == 'project_status'
        assert intent['project'] == 'y'  # Lowercase due to query_lower


class TestSmartSuggestionsEngine:
    """Test the smart suggestions engine."""
    
    @pytest.fixture
    def memory_store(self, shared_memory_store):
        """Use the shared memory store."""
        return shared_memory_store
    
    @pytest.fixture
    def suggestions_engine(self, memory_store):
        """Create a test suggestions engine."""
        return SmartSuggestionsEngine(memory_store)
    
    @pytest.fixture
    def sample_data(self, memory_store):
        """Create sample data for testing."""
        # Create a task
        task = MemoryEntity(
            type="task",
            name="Implement user authentication",
            content="Add JWT authentication to the API with Alice Johnson",
            metadata={"status": "in_progress", "due_date": (datetime.now() + timedelta(days=7)).isoformat()}
        )
        saved_task = memory_store.save_entity(task)
        
        # Create a conversation
        conv = MemoryContext(
            type="handoff",
            content="Discussed authentication implementation. Need to use JWT tokens and integrate with PostgreSQL database.",
            summary="Authentication discussion"
        )
        saved_conv = memory_store.save_context(conv)
        
        # Create a person
        person = MemoryEntity(
            type="person",
            name="Alice Johnson",
            content="Senior developer"
        )
        saved_person = memory_store.save_entity(person)
        
        # Create relationships
        memory_store.save_relation(MemoryRelation(
            source_id=saved_task.id,
            target_id=saved_conv.id,
            relation_type="relates_to"
        ))
        memory_store.save_relation(MemoryRelation(
            source_id=saved_person.id,
            target_id=saved_task.id,
            relation_type="assigned_to"
        ))
        
        return {
            'task': saved_task,
            'conversation': saved_conv,
            'person': saved_person
        }
    
    def test_task_suggestions(self, suggestions_engine, sample_data):
        """Test task-specific suggestions."""
        context = {
            'type': 'task',
            'id': sample_data['task'].id
        }
        
        suggestions = suggestions_engine.get_contextual_suggestions(context)
        
        assert isinstance(suggestions, dict)
        assert 'related_content' in suggestions
        assert 'follow_up_actions' in suggestions
        assert 'relevant_people' in suggestions
        
        # Should suggest related conversations
        assert len(suggestions['related_content']) > 0
    
    def test_conversation_suggestions(self, suggestions_engine, sample_data):
        """Test conversation-specific suggestions."""
        context = {
            'type': 'handoff',
            'id': sample_data['conversation'].id
        }
        
        suggestions = suggestions_engine.get_contextual_suggestions(context)
        
        assert isinstance(suggestions, dict)
        assert 'follow_up_actions' in suggestions
        assert 'related_content' in suggestions
        
        # Should extract action items
        assert len(suggestions['follow_up_actions']) > 0
    
    def test_project_suggestions(self, suggestions_engine, memory_store):
        """Test project-specific suggestions."""
        # Create a project
        project = MemoryEntity(
            type="project",
            name="Web Application",
            content="Building a modern web application"
        )
        saved_project = memory_store.save_entity(project)
        
        context = {
            'type': 'project',
            'id': saved_project.id
        }
        
        suggestions = suggestions_engine.get_contextual_suggestions(context)
        
        assert isinstance(suggestions, dict)
        assert 'follow_up_actions' in suggestions
        assert 'similar_projects' in suggestions
        
        # Should suggest creating initial tasks
        assert any("Create initial project tasks" in action for action in suggestions['follow_up_actions'])
    
    def test_extract_entities_from_text(self, suggestions_engine):
        """Test entity extraction from text."""
        text = "Alice Johnson and Bob Smith discussed Python and React implementation"
        
        entities = suggestions_engine._extract_entities_from_text(text)
        
        assert isinstance(entities, list)
        # Should find people
        people = [e for e in entities if e['type'] == 'person']
        assert len(people) >= 2
        
        # Should find technologies
        tech = [e for e in entities if e['type'] == 'technology']
        assert len(tech) >= 2
    
    def test_extract_action_items(self, suggestions_engine):
        """Test action item extraction."""
        text = "We need to implement authentication and should add tests for the API"
        
        action_items = suggestions_engine._extract_action_items(text)
        
        assert isinstance(action_items, list)
        assert len(action_items) > 0
        assert any("implement" in item for item in action_items)
    
    def test_extract_technologies(self, suggestions_engine):
        """Test technology extraction."""
        text = "Using Python with Django and PostgreSQL database"
        
        technologies = suggestions_engine._extract_technologies(text)
        
        assert isinstance(technologies, list)
        assert "Python" in technologies
        assert "Django" in technologies
        assert "PostgreSQL" in technologies
    
    def test_workflow_suggestions(self, suggestions_engine, memory_store):
        """Test workflow suggestions."""
        # Create some recent activity
        task = MemoryEntity(
            type="task",
            name="Recent task",
            content="A task created recently"
        )
        memory_store.save_entity(task)
        
        suggestions = suggestions_engine.get_workflow_suggestions()
        
        assert isinstance(suggestions, dict)
        assert 'next_actions' in suggestions
        assert 'efficiency_tips' in suggestions
        assert 'collaboration_opportunities' in suggestions


class TestNaturalQueryProcessor:
    """Test the natural query processor."""
    
    @pytest.fixture
    def memory_store(self, shared_memory_store):
        """Use the shared memory store."""
        return shared_memory_store
    
    @pytest.fixture
    def query_processor(self, memory_store):
        """Create a test query processor."""
        return NaturalQueryProcessor(memory_store)
    
    @pytest.fixture
    def sample_data(self, memory_store):
        """Create sample data for testing."""
        # Create various entities
        task = MemoryEntity(
            type="task",
            name="Database migration",
            content="Migrate from MySQL to PostgreSQL"
        )
        saved_task = memory_store.save_entity(task)
        
        conv = MemoryContext(
            type="handoff",
            content="Discussed database migration with Alice Johnson last week",
            summary="Migration discussion"
        )
        saved_conv = memory_store.save_context(conv)
        
        person = MemoryEntity(
            type="person",
            name="Alice Johnson",
            content="Database expert"
        )
        saved_person = memory_store.save_entity(person)
        
        return {
            'task': saved_task,
            'conversation': saved_conv,
            'person': saved_person
        }
    
    def test_parse_query_components(self, query_processor):
        """Test query component parsing."""
        query = "Show me all discussions about authentication in the last month"
        
        components = query_processor._parse_query_components(query)
        
        assert isinstance(components, dict)
        assert 'entity_types' in components
        assert 'time_range' in components
        assert 'keywords' in components
        
        # Should identify handoff entity type
        assert 'handoff' in components['entity_types']
        
        # Should identify time range
        assert components['time_range'] is not None
        
        # Should extract keywords
        assert 'authentication' in components['keywords']
    
    def test_build_search_strategy(self, query_processor):
        """Test search strategy building."""
        components = {
            'entity_types': ['handoff'],
            'keywords': ['authentication'],
            'time_range': {'start': datetime.now() - timedelta(days=30), 'end': datetime.now()}
        }
        
        strategy = query_processor._build_search_strategy(components)
        
        assert isinstance(strategy, dict)
        assert 'query' in strategy
        assert 'filters' in strategy
        assert 'time_range' in strategy
        
        # Should set entity type filter
        assert strategy['filters']['type'] == 'handoff'
    
    def test_process_query(self, query_processor, sample_data):
        """Test query processing."""
        query = "Find tasks related to database"
        
        result = query_processor.process_query(query)
        
        assert isinstance(result, dict)
        assert 'query' in result
        assert 'components' in result
        assert 'summary' in result
        assert 'results' in result
        assert 'suggestions' in result
        
        # Should find the database migration task
        if 'task' in result['results']:
            assert any('database' in t.get('name', '').lower() for t in result['results']['task'])
    
    def test_process_complex_query(self, query_processor, sample_data):
        """Test complex query processing."""
        query = "Find tasks about database and conversations with Alice"
        
        result = query_processor.process_complex_query(query)
        
        assert isinstance(result, dict)
        assert 'query' in result
        assert 'parts' in result
        assert 'part_results' in result
        assert 'combined_results' in result
        
        # Should split into parts
        assert len(result['parts']) > 1
    
    def test_format_response(self, query_processor):
        """Test response formatting."""
        results = [
            {'id': '1', 'type': 'task', 'name': 'Task 1'},
            {'id': '2', 'type': 'task', 'name': 'Task 2'},
            {'id': '3', 'type': 'handoff', 'name': 'Conversation 1'}
        ]
        
        components = {'keywords': ['test']}
        
        response = query_processor._format_response(results, components)
        
        assert isinstance(response, dict)
        assert 'results' in response
        assert 'summary' in response
        assert 'suggestions' in response
        
        # Should group by entity type
        assert 'task' in response['results']
        assert 'handoff' in response['results']
        assert len(response['results']['task']) == 2
        assert len(response['results']['handoff']) == 1


class TestIntelligentSearchMCPTools:
    """Test the MCP integration for intelligent search."""
    
    @pytest.fixture
    def memory_store(self, shared_memory_store):
        """Use the shared memory store."""
        return shared_memory_store
    
    @pytest.fixture
    def mcp_tools(self, memory_store):
        """Create test MCP tools."""
        return IntelligentSearchMCPTools(memory_store)
    
    @pytest.fixture
    def sample_data(self, memory_store):
        """Create sample data for testing."""
        # Create a project
        project = MemoryEntity(
            type="project",
            name="Test Project",
            content="A test project for intelligence features"
        )
        saved_project = memory_store.save_entity(project)
        
        # Create a person
        person = MemoryEntity(
            type="person",
            name="Test Person",
            content="A test person"
        )
        saved_person = memory_store.save_entity(person)
        
        return {
            'project': saved_project,
            'person': saved_person
        }
    
    def test_mcp_tools_initialization(self, mcp_tools):
        """Test MCP tools initialization."""
        assert mcp_tools.memory_store is not None
        assert mcp_tools.search_engine is not None
        assert mcp_tools.suggestions_engine is not None
        assert mcp_tools.query_processor is not None
    
    def test_create_expertise_map(self, mcp_tools, sample_data):
        """Test expertise map creation."""
        expertise_map = mcp_tools._create_expertise_map()
        
        assert isinstance(expertise_map, dict)
        # Should include the test person
        if sample_data['person'].id in expertise_map:
            person_data = expertise_map[sample_data['person'].id]
            assert 'name' in person_data
            assert 'expertise' in person_data
            assert 'projects' in person_data
    
    def test_get_cross_domain_insights(self, mcp_tools, sample_data):
        """Test cross-domain insights generation."""
        project_id = sample_data['project'].id
        insights = mcp_tools._get_cross_domain_insights(project_id)
        
        assert isinstance(insights, dict)
        assert 'entity' in insights
        assert 'related_content' in insights
        assert 'patterns' in insights
        assert 'recommendations' in insights
    
    def test_search_with_context(self, mcp_tools, sample_data):
        """Test contextual search."""
        query = "test"
        context = "Looking at project Test Project"
        
        results = mcp_tools._search_with_context(query, context)
        
        assert isinstance(results, dict)
        assert 'query' in results
        assert 'context' in results
        assert 'enhanced_query' in results
        assert 'results' in results
    
    def test_extract_technologies_from_text(self, mcp_tools):
        """Test technology extraction with confidence scores."""
        text = "Using Python and React for the project"
        
        tech_mentions = mcp_tools._extract_technologies_from_text(text)
        
        assert isinstance(tech_mentions, list)
        assert len(tech_mentions) >= 2
        
        for tech, confidence in tech_mentions:
            assert isinstance(tech, str)
            assert isinstance(confidence, float)
            assert 0 <= confidence <= 1
    
    def test_calculate_activity_score(self, mcp_tools):
        """Test activity score calculation."""
        conversations = [
            {'created_at': datetime.now() - timedelta(days=5)},
            {'created_at': datetime.now() - timedelta(days=10)}
        ]
        code_entities = [
            {'created_at': datetime.now() - timedelta(days=3)}
        ]
        
        score = mcp_tools._calculate_activity_score(conversations, code_entities)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
    
    def test_parse_entity_context(self, mcp_tools):
        """Test entity context parsing."""
        context = "Looking at task Database migration"
        
        context_info = mcp_tools._parse_entity_context(context)
        
        assert isinstance(context_info, dict)
        assert 'entity_type' in context_info
        assert 'keywords' in context_info
        
        assert context_info['entity_type'] == 'task'
        assert 'Database' in context_info['keywords']
        assert 'migration' in context_info['keywords']


class TestIntelligenceIntegration:
    """Integration tests for intelligence features."""
    
    @pytest.fixture
    def memory_store(self, shared_memory_store):
        """Use the shared memory store."""
        return shared_memory_store
    
    @pytest.fixture
    def search_engine(self, memory_store):
        """Create a test search engine."""
        return IntelligentSearchEngine(memory_store)
    
    @pytest.fixture
    def suggestions_engine(self, memory_store):
        """Create a test suggestions engine."""
        return SmartSuggestionsEngine(memory_store)
    
    @pytest.fixture
    def query_processor(self, memory_store):
        """Create a test query processor."""
        return NaturalQueryProcessor(memory_store)
    
    def test_end_to_end_intelligence_workflow(self, memory_store, search_engine, suggestions_engine, query_processor):
        """Test complete intelligence workflow."""
        # 1. Create sample data
        project = MemoryEntity(
            type="project",
            name="AI Integration Project",
            content="Integrating AI features into the application"
        )
        saved_project = memory_store.save_entity(project)
        
        task = MemoryEntity(
            type="task",
            name="Implement ML model",
            content="Add machine learning model for user recommendations",
            metadata={"status": "in_progress", "project_id": saved_project.id}
        )
        saved_task = memory_store.save_entity(task)
        
        person = MemoryEntity(
            type="person",
            name="Dr. Sarah Chen",
            content="ML specialist"
        )
        saved_person = memory_store.save_entity(person)
        
        conv = MemoryContext(
            type="handoff",
            content="Discussed ML implementation with Dr. Sarah Chen. Need to use Python with TensorFlow and integrate with PostgreSQL database.",
            summary="ML implementation discussion"
        )
        saved_conv = memory_store.save_context(conv)
        
        # 2. Test intelligent search
        search_results = search_engine.universal_search("machine learning")
        assert isinstance(search_results, dict)
        
        # 3. Test project intelligence
        intelligence = search_engine.get_project_intelligence(saved_project.id)
        assert isinstance(intelligence, dict)
        assert 'metrics' in intelligence
        
        # 4. Test smart suggestions
        context = {'type': 'task', 'id': saved_task.id}
        suggestions = suggestions_engine.get_contextual_suggestions(context)
        assert isinstance(suggestions, dict)
        assert 'follow_up_actions' in suggestions
        
        # 5. Test natural query processing
        query_result = query_processor.process_query("Find ML experts in the project")
        assert isinstance(query_result, dict)
        assert 'results' in query_result
        
        # 6. Test expertise finding
        experts = search_engine._find_expert_for_technology("Python")
        assert isinstance(experts, list)
        
        # 7. Test workflow suggestions
        workflow_suggestions = suggestions_engine.get_workflow_suggestions()
        assert isinstance(workflow_suggestions, dict)
        assert 'next_actions' in workflow_suggestions
    
    def test_performance_with_large_dataset(self, memory_store, search_engine):
        """Test performance with larger datasets."""
        # Create many entities
        for i in range(50):
            task = MemoryEntity(
                type="task",
                name=f"Task {i}",
                content=f"Content for task {i}"
            )
            memory_store.save_entity(task)
        
        # Test search performance
        start_time = datetime.now()
        results = search_engine.universal_search("task")
        end_time = datetime.now()
        
        # Should complete within reasonable time (less than 5 seconds)
        assert (end_time - start_time).total_seconds() < 5
        assert isinstance(results, dict)
    
    def test_error_handling(self, memory_store, search_engine, suggestions_engine, query_processor):
        """Test error handling in intelligence features."""
        # Test with invalid entity ID
        intelligence = search_engine.get_project_intelligence("invalid-id")
        assert isinstance(intelligence, dict)
        assert intelligence == {}  # Should return empty dict for invalid ID
        
        # Test with invalid context
        suggestions = suggestions_engine.get_contextual_suggestions({'type': 'invalid', 'id': 'invalid'})
        assert isinstance(suggestions, dict)
        assert 'related_content' in suggestions
        
        # Test with empty query
        query_result = query_processor.process_query("")
        assert isinstance(query_result, dict)
        assert 'results' in query_result 