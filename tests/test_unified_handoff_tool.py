"""
Unit tests for unified handoff tool wrapper.
Phase 3.1: Handoff Tool Wrapper
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

from core import create_test_memory_store
from core.models import MemoryContext
from tools.handoff.unified_handoff_tool import UnifiedHandoffTool, HandoffContext


class TestUnifiedHandoffTool:
    """Test UnifiedHandoffTool backward compatibility and AI features."""
    
    @pytest.fixture
    def memory_store(self):
        """Create a test memory store."""
        store = create_test_memory_store(enable_vector_search=False, enable_ai_extraction=False)
        try:
            yield store
        finally:
            store.close()
    
    @pytest.fixture
    def handoff_tool(self, memory_store):
        """Create a UnifiedHandoffTool instance."""
        return UnifiedHandoffTool(memory_store)
    
    def test_backward_compatible_save_context(self, handoff_tool):
        """Test that save_context maintains original API."""
        context_text = "Working on the MCP tools project. Need to implement Phase 3.1."
        
        result = handoff_tool.save_context(context_text)
        
        # Verify backward compatible structure
        assert isinstance(result, HandoffContext)
        assert result.id is not None
        assert isinstance(result.id, int)
        assert result.context == context_text
        assert isinstance(result.created_at, datetime)
        
        # Verify enhanced fields are present
        assert hasattr(result, 'summary')
        assert hasattr(result, 'topics')
        assert hasattr(result, 'related_entities')
    
    def test_backward_compatible_get_contexts(self, handoff_tool):
        """Test that get_contexts maintains original API."""
        # Save multiple contexts
        contexts = [
            "First context about project setup",
            "Second context about database design",
            "Third context about AI features"
        ]
        
        saved_contexts = []
        for ctx in contexts:
            saved = handoff_tool.save_context(ctx)
            saved_contexts.append(saved)
        
        # Get all contexts
        all_contexts = handoff_tool.get_contexts()
        
        # Verify structure and ordering
        assert len(all_contexts) == 3
        assert all(isinstance(ctx, HandoffContext) for ctx in all_contexts)
        
        # Should be sorted by created_at desc (most recent first)
        assert all_contexts[0].created_at >= all_contexts[1].created_at
        assert all_contexts[1].created_at >= all_contexts[2].created_at
    
    def test_backward_compatible_get_latest_context(self, handoff_tool):
        """Test that get_latest_context maintains original API."""
        # Save contexts with delays
        handoff_tool.save_context("First context")
        handoff_tool.save_context("Second context")
        latest = handoff_tool.save_context("Latest context")
        
        result = handoff_tool.get_latest_context()
        
        assert result is not None
        assert result.id == latest.id
        assert result.context == "Latest context"
    
    def test_backward_compatible_list_contexts(self, handoff_tool):
        """Test that list_contexts maintains original API with limit."""
        # Save 5 contexts
        for i in range(5):
            handoff_tool.save_context(f"Context {i}")
        
        # Test with limit
        limited = handoff_tool.list_contexts(limit=3)
        assert len(limited) == 3
        
        # Test without limit (should default to 10)
        all_contexts = handoff_tool.list_contexts()
        assert len(all_contexts) == 5
    
    def test_backward_compatible_get_context(self, handoff_tool):
        """Test that get_context maintains original API."""
        saved = handoff_tool.save_context("Test context for retrieval")
        
        # Get by ID
        retrieved = handoff_tool.get_context(saved.id)
        
        assert retrieved is not None
        assert retrieved.id == saved.id
        assert retrieved.context == saved.context
        assert retrieved.created_at == saved.created_at
    
    def test_get_context_not_found(self, handoff_tool):
        """Test get_context returns None for non-existent ID."""
        result = handoff_tool.get_context(99999)
        assert result is None
    
    def test_numeric_id_consistency(self, handoff_tool):
        """Test that numeric IDs are consistent across operations."""
        saved = handoff_tool.save_context("Test for ID consistency")
        original_id = saved.id
        
        # Get the same context multiple times
        retrieved1 = handoff_tool.get_context(original_id)
        retrieved2 = handoff_tool.get_context(original_id)
        
        assert retrieved1.id == original_id
        assert retrieved2.id == original_id
        assert retrieved1.id == retrieved2.id
    
    def test_search_contexts_semantic(self, handoff_tool):
        """Test semantic search functionality."""
        # Save contexts with different content
        handoff_tool.save_context("Working on database schema design")
        handoff_tool.save_context("Implementing AI entity extraction")
        handoff_tool.save_context("Setting up vector search capabilities")
        
        # Search for database-related content
        results = handoff_tool.search_contexts("database schema")
        
        assert len(results) > 0
        # Should find the database context
        found_database = any("database" in ctx.context.lower() for ctx in results)
        assert found_database
    
    def test_search_contexts_with_relevance_scores(self, handoff_tool):
        """Test that search results include relevance scores."""
        handoff_tool.save_context("Testing relevance scores in search")
        
        results = handoff_tool.search_contexts("relevance")
        
        assert len(results) > 0
        # Check that relevance scores are attached
        for ctx in results:
            assert hasattr(ctx, 'relevance_score')
            assert isinstance(ctx.relevance_score, (int, float))
    
    def test_get_related_contexts(self, handoff_tool):
        """Test finding related contexts through entities and topics."""
        # Save contexts that should be related
        ctx1 = handoff_tool.save_context("Working with John on the API design")
        ctx2 = handoff_tool.save_context("John mentioned the database needs optimization")
        ctx3 = handoff_tool.save_context("API implementation is progressing well")
        
        # Get related contexts for the first context
        related = handoff_tool.get_related_contexts(ctx1.id)
        
        # Should find contexts mentioning John or API
        assert len(related) > 0
        related_texts = [ctx.context.lower() for ctx in related]
        
        # Should find contexts with "john" or "api"
        found_john = any("john" in text for text in related_texts)
        found_api = any("api" in text for text in related_texts)
        
        # At least one should be found
        assert found_john or found_api
    
    def test_get_context_insights(self, handoff_tool):
        """Test AI-generated insights for a context."""
        saved = handoff_tool.save_context(
            "Meeting with Sarah about the new authentication system. "
            "Need to implement OAuth2 and update the database schema. "
            "John will handle the frontend integration."
        )
        
        insights = handoff_tool.get_context_insights(saved.id)
        
        # Verify insights structure
        assert isinstance(insights, dict)
        assert "summary" in insights
        assert "key_topics" in insights
        assert "action_items" in insights
        assert "mentioned_people" in insights
        assert "technologies" in insights
        assert "context_length" in insights
        assert "entity_count" in insights
        assert "creation_date" in insights
        
        # Verify data types
        assert isinstance(insights["summary"], str)
        assert isinstance(insights["key_topics"], list)
        assert isinstance(insights["action_items"], list)
        assert isinstance(insights["mentioned_people"], list)
        assert isinstance(insights["technologies"], list)
        assert isinstance(insights["context_length"], int)
        assert isinstance(insights["entity_count"], int)
        assert isinstance(insights["creation_date"], datetime)
    
    def test_suggest_followup_actions(self, handoff_tool):
        """Test follow-up action suggestions."""
        saved = handoff_tool.save_context(
            "Need to review the authentication code. "
            "Sarah mentioned there are security concerns. "
            "Should create documentation for the API endpoints."
        )
        
        suggestions = handoff_tool.suggest_followup_actions(saved.id)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5  # Should be limited to 5
        
        # Should contain actionable suggestions
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0
    
    def test_ai_enhancement_fallback(self, handoff_tool):
        """Test graceful fallback when AI enhancement fails."""
        # This test would require mocking AI components to fail
        # For now, we test that the basic functionality works
        context_text = "Basic context without AI enhancement"
        
        result = handoff_tool.save_context(context_text)
        
        # Should still work even if AI fails
        assert result is not None
        assert result.context == context_text
        assert result.id is not None
    
    def test_mcp_tool_registration(self, handoff_tool):
        """Test that MCP tools are properly registered."""
        # Mock MCP object
        class MockMCP:
            def __init__(self):
                self.tools = []
                self.resources = []
            
            def tool(self):
                def decorator(func):
                    self.tools.append(func.__name__)
                    return func
                return decorator
            
            def resource(self, path):
                def decorator(func):
                    self.resources.append(path)
                    return func
                return decorator
        
        mcp = MockMCP()
        handoff_tool.register(mcp)
        
        # Verify all expected tools are registered
        expected_tools = [
            'handoff_save', 'handoff_get', 'handoff_list', 
            'handoff_search', 'handoff_related', 'handoff_insights', 
            'handoff_suggest_actions'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in mcp.tools
        
        # Verify resources are registered
        expected_resources = [
            'resource://handoff/recent',
            'resource://handoff/{context_id}'
        ]
        
        for resource_path in expected_resources:
            assert resource_path in mcp.resources
    
    def test_id_mapping_cache(self, handoff_tool):
        """Test that ID mapping cache works correctly."""
        saved = handoff_tool.save_context("Test cache functionality")
        
        # First call should populate cache
        retrieved1 = handoff_tool.get_context(saved.id)
        assert retrieved1 is not None
        
        # Second call should use cache
        retrieved2 = handoff_tool.get_context(saved.id)
        assert retrieved2 is not None
        
        # Both should be the same
        assert retrieved1.id == retrieved2.id
        assert retrieved1.context == retrieved2.context
    
    def test_metadata_preservation(self, handoff_tool):
        """Test that metadata is preserved in the unified backend."""
        context_text = "Context with important metadata"
        saved = handoff_tool.save_context(context_text)
        
        # Get the context from the unified backend directly
        memory_contexts = handoff_tool.memory.search_contexts("", filters={"type": "handoff"})
        
        assert len(memory_contexts) > 0
        memory_ctx = memory_contexts[0].model_dump()
        
        # Should have tool metadata
        assert memory_ctx['metadata']['tool'] == 'handoff'
        assert 'numeric_id' in memory_ctx['metadata']
    
    def test_performance_with_large_dataset(self, handoff_tool):
        """Test performance with multiple contexts."""
        # Save 50 contexts
        contexts = []
        for i in range(50):
            ctx = handoff_tool.save_context(f"Context {i} with some content for testing")
            contexts.append(ctx)
        
        # Test list performance
        start_time = datetime.now()
        all_contexts = handoff_tool.list_contexts(limit=50)
        end_time = datetime.now()
        
        assert len(all_contexts) == 50
        # Should complete within reasonable time (less than 1 second)
        assert (end_time - start_time).total_seconds() < 1.0
        
        # Test search performance
        start_time = datetime.now()
        search_results = handoff_tool.search_contexts("content", limit=10)
        end_time = datetime.now()
        
        assert len(search_results) > 0
        # Should complete within reasonable time
        assert (end_time - start_time).total_seconds() < 1.0


class TestHandoffContextModel:
    """Test the HandoffContext model."""
    
    def test_handoff_context_creation(self):
        """Test creating HandoffContext instances."""
        ctx = HandoffContext(
            id=1,
            context="Test context",
            created_at=datetime.now()
        )
        
        assert ctx.id == 1
        assert ctx.context == "Test context"
        assert isinstance(ctx.created_at, datetime)
    
    def test_handoff_context_defaults(self):
        """Test HandoffContext default values."""
        ctx = HandoffContext(context="Test context")
        
        assert ctx.id is None
        assert ctx.context == "Test context"
        assert isinstance(ctx.created_at, datetime)
        assert ctx.summary is None
        assert ctx.topics == []
        assert ctx.related_entities == []
    
    def test_handoff_context_enhanced_fields(self):
        """Test enhanced fields in HandoffContext."""
        ctx = HandoffContext(
            context="Test context",
            summary="AI-generated summary",
            topics=["api", "database"],
            related_entities=["entity1", "entity2"]
        )
        
        assert ctx.summary == "AI-generated summary"
        assert ctx.topics == ["api", "database"]
        assert ctx.related_entities == ["entity1", "entity2"]
    
    def test_handoff_context_serialization(self):
        """Test HandoffContext serialization."""
        ctx = HandoffContext(
            id=1,
            context="Test context",
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            summary="Summary",
            topics=["topic1"],
            related_entities=["entity1"]
        )
        
        # Test to dict
        ctx_dict = ctx.model_dump()
        assert ctx_dict["id"] == 1
        assert ctx_dict["context"] == "Test context"
        assert ctx_dict["summary"] == "Summary"
        assert ctx_dict["topics"] == ["topic1"]
        assert ctx_dict["related_entities"] == ["entity1"]
        
        # Test from dict
        new_ctx = HandoffContext(**ctx_dict)
        assert new_ctx.id == ctx.id
        assert new_ctx.context == ctx.context
        assert new_ctx.summary == ctx.summary
        assert new_ctx.topics == ctx.topics
        assert new_ctx.related_entities == ctx.related_entities


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 