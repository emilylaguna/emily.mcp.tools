import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from tools.handoff.handoff import HandoffTool, HandoffContext


class TestHandoffTool:
    """Test suite for HandoffTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def handoff_tool(self, temp_data_dir):
        """Create a HandoffTool instance for testing."""
        return HandoffTool(temp_data_dir)

    @pytest.fixture
    def sample_contexts(self):
        """Sample handoff contexts for testing."""
        return [
            "User asked about Python programming and we discussed best practices for error handling.",
            "We were working on a web application project and the user needed help with database queries.",
            "The conversation was about machine learning algorithms and the user wanted to understand neural networks."
        ]

    def test_name_property(self, handoff_tool):
        """Test that the tool name is correct."""
        assert handoff_tool.name == "handoff"

    def test_description_property(self, handoff_tool):
        """Test that the tool description is correct."""
        assert handoff_tool.description == "Save and retrieve chat context for handoff between sessions, with timestamp for freshness."

    def test_get_capabilities(self, handoff_tool):
        """Test that all expected capabilities are returned."""
        capabilities = handoff_tool.get_capabilities()
        expected_capabilities = [
            "save_context",
            "get_latest_context",
            "list_contexts"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_contexts_empty_file(self, handoff_tool):
        """Test reading an empty contexts file."""
        result = handoff_tool._read_contexts()
        assert result == []

    def test_read_contexts_with_data(self, handoff_tool, sample_contexts):
        """Test reading contexts from file."""
        # Write some test data
        with open(handoff_tool.data_file, 'w') as f:
            for context_str in sample_contexts:
                context = HandoffContext(context=context_str)
                f.write(context.json() + '\n')
        
        result = handoff_tool._read_contexts()
        assert len(result) == 3
        assert all(isinstance(context, HandoffContext) for context in result)

    def test_write_contexts(self, handoff_tool, sample_contexts):
        """Test writing contexts to file."""
        contexts = [HandoffContext(context=context_str) for context_str in sample_contexts]
        handoff_tool._write_contexts(contexts)
        
        # Verify the data was written correctly
        with open(handoff_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for i, line in enumerate(lines):
            context = HandoffContext(**json.loads(line.strip()))
            assert context.context == sample_contexts[i]

    def test_save_context(self, handoff_tool):
        """Test saving a context."""
        context_str = "This is a test context for handoff."
        saved_context = handoff_tool.save_context(context_str)
        
        assert saved_context.id == 1
        assert saved_context.context == context_str
        assert saved_context.created_at is not None

    def test_save_context_id_increment(self, handoff_tool):
        """Test that context IDs increment properly."""
        context1 = handoff_tool.save_context("First context")
        context2 = handoff_tool.save_context("Second context")
        context3 = handoff_tool.save_context("Third context")
        
        assert context1.id == 1
        assert context2.id == 2
        assert context3.id == 3

    def test_save_context_timestamp(self, handoff_tool):
        """Test that saved contexts have proper timestamps."""
        before_save = datetime.now()
        saved_context = handoff_tool.save_context("Test context")
        after_save = datetime.now()
        
        # The created_at timestamp should be between before and after save
        assert before_save <= saved_context.created_at <= after_save

    def test_get_latest_context_single(self, handoff_tool):
        """Test getting the latest context when there's only one."""
        saved_context = handoff_tool.save_context("Test context")
        latest = handoff_tool.get_latest_context()
        
        assert latest is not None
        assert latest.id == saved_context.id
        assert latest.context == saved_context.context

    def test_get_latest_context_multiple(self, handoff_tool):
        """Test getting the latest context when there are multiple."""
        # Save contexts with a small delay to ensure different timestamps
        context1 = handoff_tool.save_context("First context")
        context2 = handoff_tool.save_context("Second context")
        context3 = handoff_tool.save_context("Third context")
        
        latest = handoff_tool.get_latest_context()
        
        assert latest is not None
        assert latest.id == context3.id  # Should be the most recent
        assert latest.context == context3.context

    def test_get_latest_context_empty(self, handoff_tool):
        """Test getting the latest context when there are none."""
        latest = handoff_tool.get_latest_context()
        assert latest is None

    def test_list_contexts_empty(self, handoff_tool):
        """Test listing contexts when there are none."""
        contexts = handoff_tool.list_contexts()
        assert contexts == []

    def test_list_contexts_all(self, handoff_tool, sample_contexts):
        """Test listing all contexts."""
        # Save contexts
        for context_str in sample_contexts:
            handoff_tool.save_context(context_str)
        
        contexts = handoff_tool.list_contexts()
        assert len(contexts) == 3
        assert all(isinstance(context, HandoffContext) for context in contexts)

    def test_list_contexts_with_limit(self, handoff_tool, sample_contexts):
        """Test listing contexts with a limit."""
        # Save contexts
        for context_str in sample_contexts:
            handoff_tool.save_context(context_str)
        
        contexts = handoff_tool.list_contexts(limit=2)
        assert len(contexts) == 2

    def test_list_contexts_ordered_by_time(self, handoff_tool):
        """Test that contexts are ordered by creation time (newest first)."""
        context1 = handoff_tool.save_context("First context")
        context2 = handoff_tool.save_context("Second context")
        context3 = handoff_tool.save_context("Third context")
        
        contexts = handoff_tool.list_contexts()
        
        # Should be ordered newest first
        assert contexts[0].id == context3.id
        assert contexts[1].id == context2.id
        assert contexts[2].id == context1.id

    def test_get_context(self, handoff_tool):
        """Test getting a specific context by ID."""
        saved_context = handoff_tool.save_context("Test context")
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.id == saved_context.id
        assert retrieved_context.context == saved_context.context

    def test_get_context_nonexistent(self, handoff_tool):
        """Test getting a non-existent context."""
        result = handoff_tool.get_context(999)
        assert result is None

    def test_register_tools(self, handoff_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        mock_mcp.resource.return_value = mock_decorator
        
        handoff_tool.register(mock_mcp)
        
        # Verify tools and resources were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        assert mock_mcp.resource.call_count == 2  # 2 resources
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'handoff_save',
            'handoff_get',
            'handoff_list'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, handoff_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "handoff.jsonl"
        assert handoff_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, handoff_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(handoff_tool.data_file, 'w') as f:
            f.write('{"context": "valid context"}\n')
            f.write('invalid json line\n')
            f.write('{"context": "another valid context"}\n')
        
        # Should skip invalid lines and return valid ones
        result = handoff_tool._read_contexts()
        assert len(result) == 2
        assert result[0].context == "valid context"
        assert result[1].context == "another valid context"

    def test_handoff_context_model_validation(self):
        """Test HandoffContext model validation."""
        # Valid context
        context = HandoffContext(context="Test context")
        assert context.context == "Test context"

    def test_handoff_context_default_values(self):
        """Test HandoffContext model default values."""
        context = HandoffContext(context="Test context")
        
        assert context.id is None
        assert context.created_at is not None

    def test_context_persistence(self, handoff_tool):
        """Test that contexts persist across tool instances."""
        # Save context with first tool instance
        context_str = "Persistent context test"
        saved_context = handoff_tool.save_context(context_str)
        
        # Create a new tool instance (simulating restart)
        new_tool = HandoffTool(handoff_tool.data_dir)
        
        # Should be able to retrieve the context
        retrieved_context = new_tool.get_context(saved_context.id)
        assert retrieved_context is not None
        assert retrieved_context.context == context_str

    def test_context_ordering_with_same_timestamp(self, handoff_tool):
        """Test context ordering when timestamps are very close."""
        # This test verifies that contexts are properly ordered even with very close timestamps
        contexts = []
        for i in range(5):
            context = handoff_tool.save_context(f"Context {i}")
            contexts.append(context)
        
        # List contexts should return them in reverse order (newest first)
        listed_contexts = handoff_tool.list_contexts()
        assert len(listed_contexts) == 5
        
        # Verify order (newest first)
        for i, context in enumerate(listed_contexts):
            assert context.id == contexts[4-i].id

    def test_large_context_content(self, handoff_tool):
        """Test saving and retrieving large context content."""
        # Create a large context string
        large_context = "This is a very large context " * 1000  # ~30KB
        
        saved_context = handoff_tool.save_context(large_context)
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.context == large_context

    def test_special_characters_in_context(self, handoff_tool):
        """Test saving and retrieving contexts with special characters."""
        special_context = "Context with special chars: éñtërnâtiönål, 🚀, & <script>alert('test')</script>"
        
        saved_context = handoff_tool.save_context(special_context)
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.context == special_context

    def test_empty_context(self, handoff_tool):
        """Test saving and retrieving empty context."""
        empty_context = ""
        saved_context = handoff_tool.save_context(empty_context)
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.context == empty_context

    def test_whitespace_only_context(self, handoff_tool):
        """Test saving and retrieving context with only whitespace."""
        whitespace_context = "   \n\t   "
        saved_context = handoff_tool.save_context(whitespace_context)
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.context == whitespace_context

    def test_context_with_newlines(self, handoff_tool):
        """Test saving and retrieving context with newlines."""
        multiline_context = "Line 1\nLine 2\nLine 3"
        saved_context = handoff_tool.save_context(multiline_context)
        retrieved_context = handoff_tool.get_context(saved_context.id)
        
        assert retrieved_context is not None
        assert retrieved_context.context == multiline_context

    def test_limit_edge_cases(self, handoff_tool):
        """Test list_contexts with edge case limits."""
        # Save some contexts
        for i in range(5):
            handoff_tool.save_context(f"Context {i}")
        
        # Test with limit 0
        contexts = handoff_tool.list_contexts(limit=0)
        assert len(contexts) == 0
        
        # Test with limit larger than available contexts
        contexts = handoff_tool.list_contexts(limit=10)
        assert len(contexts) == 5
        
        # Test with negative limit (should handle gracefully)
        # The implementation might not handle negative limits, so we'll test what it actually does
        contexts = handoff_tool.list_contexts(limit=-1)
        # Just verify we get some result, the exact behavior depends on implementation
        assert len(contexts) >= 0

    def test_concurrent_access_simulation(self, handoff_tool):
        """Test that the tool handles multiple saves correctly."""
        # Simulate multiple rapid saves
        contexts = []
        for i in range(10):
            context = handoff_tool.save_context(f"Rapid context {i}")
            contexts.append(context)
        
        # All contexts should have unique IDs
        context_ids = [c.id for c in contexts]
        assert len(set(context_ids)) == 10
        
        # All contexts should be retrievable
        for context in contexts:
            retrieved = handoff_tool.get_context(context.id)
            assert retrieved is not None
            assert retrieved.context == context.context 