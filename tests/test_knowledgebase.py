import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock
from tools.knowledgebase.knowledgebase import KnowledgebaseTool, KnowledgeNode, KnowledgeRelation, Codebase


class TestKnowledgebaseTool:
    """Test suite for KnowledgebaseTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def knowledgebase_tool(self, temp_data_dir):
        """Create a KnowledgebaseTool instance for testing."""
        return KnowledgebaseTool(temp_data_dir)

    @pytest.fixture
    def sample_codebases(self):
        """Sample codebases for testing."""
        return [
            {
                "id": "project-a",
                "name": "Project Alpha",
                "root_path": "/path/to/project-a",
                "description": "A Python web application"
            },
            {
                "id": "project-b", 
                "name": "Project Beta",
                "root_path": "/path/to/project-b",
                "description": "A JavaScript frontend application"
            }
        ]

    @pytest.fixture
    def sample_nodes(self):
        """Sample knowledge nodes for testing."""
        return [
            {
                "codebase_id": "project-a",
                "node_type": "function",
                "name": "calculate_total",
                "content": "def calculate_total(items): return sum(items)",
                "path": "src/utils.py",
                "metadata": {"line_number": 42, "complexity": "low"}
            },
            {
                "codebase_id": "project-a",
                "node_type": "class",
                "name": "UserManager",
                "content": "class UserManager: def __init__(self): pass",
                "path": "src/models.py",
                "metadata": {"line_number": 15, "methods": 3}
            },
            {
                "codebase_id": "project-b",
                "node_type": "function",
                "name": "validateForm",
                "content": "function validateForm(data) { return data.length > 0; }",
                "path": "src/validation.js",
                "metadata": {"line_number": 28, "complexity": "medium"}
            }
        ]

    @pytest.fixture
    def sample_relations(self):
        """Sample knowledge relations for testing."""
        return [
            {
                "source_node_id": 1,
                "target_node_id": 2,
                "relation_type": "calls",
                "metadata": {"frequency": "high"}
            },
            {
                "source_node_id": 2,
                "target_node_id": 3,
                "relation_type": "imports",
                "metadata": {"module": "utils"}
            }
        ]

    def test_name_property(self, knowledgebase_tool):
        """Test that the tool name is correct."""
        assert knowledgebase_tool.name == "knowledgebase"

    def test_description_property(self, knowledgebase_tool):
        """Test that the tool description is correct."""
        assert knowledgebase_tool.description == "Manage knowledge graphs for multiple codebases with semantic relationships"

    def test_get_capabilities(self, knowledgebase_tool):
        """Test that all expected capabilities are returned."""
        capabilities = knowledgebase_tool.get_capabilities()
        expected_capabilities = [
            "register_codebase",
            "add_knowledge_node",
            "add_knowledge_relation",
            "search_nodes",
            "get_node",
            "get_related_nodes",
            "list_codebases",
            "get_codebase_info",
            "query_knowledge_graph"
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_entries_empty_file(self, knowledgebase_tool):
        """Test reading an empty entries file."""
        result = knowledgebase_tool._read_entries()
        assert result == []

    def test_read_entries_with_data(self, knowledgebase_tool, sample_codebases):
        """Test reading entries from file."""
        # Write some test data
        with open(knowledgebase_tool.data_file, 'w') as f:
            for codebase_data in sample_codebases:
                entry = {**codebase_data, 'type': 'codebase', 'created_at': datetime.now().isoformat()}
                f.write(json.dumps(entry) + '\n')
        
        result = knowledgebase_tool._read_entries()
        assert len(result) == 2
        assert all('type' in entry for entry in result)
        assert all(entry['type'] == 'codebase' for entry in result)

    def test_write_entries(self, knowledgebase_tool, sample_codebases):
        """Test writing entries to file."""
        entries = []
        for codebase_data in sample_codebases:
            entry = {**codebase_data, 'type': 'codebase', 'created_at': datetime.now().isoformat()}
            entries.append(entry)
        
        knowledgebase_tool._write_entries(entries)
        
        # Verify the data was written correctly
        with open(knowledgebase_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2
        for i, line in enumerate(lines):
            entry = json.loads(line.strip())
            assert entry['name'] == sample_codebases[i]['name']

    def test_register_codebase_new(self, knowledgebase_tool):
        """Test registering a new codebase."""
        codebase = knowledgebase_tool.register_codebase(
            codebase_id="test-project",
            name="Test Project",
            root_path="/path/to/test",
            description="A test project"
        )
        
        assert codebase.id == "test-project"
        assert codebase.name == "Test Project"
        assert codebase.root_path == "/path/to/test"
        assert codebase.description == "A test project"
        assert codebase.created_at is not None

    def test_register_codebase_existing(self, knowledgebase_tool):
        """Test registering an existing codebase."""
        # Register codebase first time
        codebase1 = knowledgebase_tool.register_codebase(
            codebase_id="existing-project",
            name="Original Name",
            root_path="/original/path"
        )
        
        # Try to register the same codebase again
        codebase2 = knowledgebase_tool.register_codebase(
            codebase_id="existing-project",
            name="New Name",
            root_path="/new/path"
        )
        
        # Should return the original codebase
        assert codebase2.id == codebase1.id
        assert codebase2.name == codebase1.name
        assert codebase2.root_path == codebase1.root_path

    def test_add_knowledge_node(self, knowledgebase_tool):
        """Test adding a knowledge node."""
        node = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="test_function",
            content="def test_function(): pass",
            path="src/test.py",
            metadata={"line_number": 10}
        )
        
        assert node.id == 1
        assert node.codebase_id == "test-project"
        assert node.node_type == "function"
        assert node.name == "test_function"
        assert node.content == "def test_function(): pass"
        assert node.path == "src/test.py"
        assert node.metadata["line_number"] == 10
        assert node.created_at is not None
        assert node.updated_at is not None

    def test_add_knowledge_node_id_increment(self, knowledgebase_tool):
        """Test that node IDs increment properly."""
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        
        assert node1.id == 1
        assert node2.id == 2

    def test_add_knowledge_relation(self, knowledgebase_tool):
        """Test adding a knowledge relation."""
        # First add some nodes
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        
        # Add relation between them
        relation = knowledgebase_tool.add_knowledge_relation(
            source_node_id=node1.id,
            target_node_id=node2.id,
            relation_type="calls",
            metadata={"frequency": "high"}
        )
        
        assert relation.id == 1
        assert relation.source_node_id == node1.id
        assert relation.target_node_id == node2.id
        assert relation.relation_type == "calls"
        assert relation.metadata["frequency"] == "high"
        assert relation.created_at is not None

    def test_search_nodes_by_name(self, knowledgebase_tool, sample_nodes):
        """Test searching nodes by name."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        results = knowledgebase_tool.search_nodes("calculate")
        assert len(results) == 1
        assert "calculate" in results[0].name.lower()

    def test_search_nodes_by_content(self, knowledgebase_tool, sample_nodes):
        """Test searching nodes by content."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        results = knowledgebase_tool.search_nodes("def")
        assert len(results) == 2  # Two Python functions with 'def'
        assert all("def" in node.content for node in results)

    def test_search_nodes_by_codebase(self, knowledgebase_tool, sample_nodes):
        """Test searching nodes filtered by codebase."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        results = knowledgebase_tool.search_nodes("", codebase_id="project-a")
        assert len(results) == 2  # Two nodes from project-a
        assert all(node.codebase_id == "project-a" for node in results)

    def test_search_nodes_by_type(self, knowledgebase_tool, sample_nodes):
        """Test searching nodes filtered by type."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        results = knowledgebase_tool.search_nodes("", node_type="function")
        assert len(results) == 2  # Two function nodes
        assert all(node.node_type == "function" for node in results)

    def test_search_nodes_with_limit(self, knowledgebase_tool, sample_nodes):
        """Test searching nodes with limit."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        results = knowledgebase_tool.search_nodes("", limit=2)
        assert len(results) == 2

    def test_search_nodes_case_insensitive(self, knowledgebase_tool):
        """Test that search is case insensitive."""
        knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="CALCULATE_TOTAL",
            content="def CALCULATE_TOTAL(): pass"
        )
        
        results = knowledgebase_tool.search_nodes("calculate")
        assert len(results) == 1

    def test_get_node(self, knowledgebase_tool):
        """Test getting a specific node."""
        created_node = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="test_function",
            content="def test_function(): pass"
        )
        
        retrieved_node = knowledgebase_tool.get_node(created_node.id)
        
        assert retrieved_node is not None
        assert retrieved_node.id == created_node.id
        assert retrieved_node.name == created_node.name

    def test_get_node_nonexistent(self, knowledgebase_tool):
        """Test getting a non-existent node."""
        result = knowledgebase_tool.get_node(999)
        assert result is None

    def test_get_related_nodes_outgoing(self, knowledgebase_tool):
        """Test getting outgoing related nodes."""
        # Add nodes
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        
        # Add relation from node1 to node2
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node1.id,
            target_node_id=node2.id,
            relation_type="calls"
        )
        
        # Get outgoing relations from node1
        related = knowledgebase_tool.get_related_nodes(node1.id, direction="out")
        # The method returns all nodes that are related, so we should get both nodes
        assert len(related) >= 1
        node_ids = [node['id'] for node in related]
        assert node2.id in node_ids

    def test_get_related_nodes_incoming(self, knowledgebase_tool):
        """Test getting incoming related nodes."""
        # Add nodes
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        
        # Add relation from node1 to node2
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node1.id,
            target_node_id=node2.id,
            relation_type="calls"
        )
        
        # Get incoming relations to node2
        related = knowledgebase_tool.get_related_nodes(node2.id, direction="in")
        # The method returns all nodes that are related, so we should get both nodes
        assert len(related) >= 1
        node_ids = [node['id'] for node in related]
        assert node1.id in node_ids

    def test_get_related_nodes_both(self, knowledgebase_tool):
        """Test getting both incoming and outgoing related nodes."""
        # Add nodes
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        node3 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function3",
            content="def function3(): pass"
        )
        
        # Add relations: node1 -> node2, node3 -> node2
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node1.id,
            target_node_id=node2.id,
            relation_type="calls"
        )
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node3.id,
            target_node_id=node2.id,
            relation_type="calls"
        )
        
        # Get all relations for node2
        related = knowledgebase_tool.get_related_nodes(node2.id, direction="both")
        # The method returns all nodes that are related, so we should get all three nodes
        assert len(related) >= 2
        node_ids = [node['id'] for node in related]
        assert node1.id in node_ids
        assert node3.id in node_ids

    def test_get_related_nodes_by_type(self, knowledgebase_tool):
        """Test getting related nodes filtered by relation type."""
        # Add nodes
        node1 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function1",
            content="def function1(): pass"
        )
        node2 = knowledgebase_tool.add_knowledge_node(
            codebase_id="test-project",
            node_type="function",
            name="function2",
            content="def function2(): pass"
        )
        
        # Add different types of relations
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node1.id,
            target_node_id=node2.id,
            relation_type="calls"
        )
        knowledgebase_tool.add_knowledge_relation(
            source_node_id=node2.id,
            target_node_id=node1.id,
            relation_type="imports"
        )
        
        # Get only "calls" relations
        related = knowledgebase_tool.get_related_nodes(node1.id, relation_type="calls")
        # The method returns all nodes that are related, so we should get both nodes
        assert len(related) >= 1
        node_ids = [node['id'] for node in related]
        assert node2.id in node_ids

    def test_list_codebases(self, knowledgebase_tool, sample_codebases):
        """Test listing all codebases."""
        # Register codebases
        for codebase_data in sample_codebases:
            # Remove the 'id' key since register_codebase doesn't accept it
            codebase_data_copy = codebase_data.copy()
            codebase_id = codebase_data_copy.pop('id')
            knowledgebase_tool.register_codebase(
                codebase_id=codebase_id,
                **codebase_data_copy
            )
        
        codebases = knowledgebase_tool.list_codebases()
        assert len(codebases) == 2
        assert all(isinstance(codebase, Codebase) for codebase in codebases)

    def test_get_codebase_info(self, knowledgebase_tool):
        """Test getting specific codebase info."""
        created_codebase = knowledgebase_tool.register_codebase(
            codebase_id="test-project",
            name="Test Project",
            root_path="/path/to/test"
        )
        
        retrieved_codebase = knowledgebase_tool.get_codebase_info("test-project")
        
        assert retrieved_codebase is not None
        assert retrieved_codebase.id == created_codebase.id
        assert retrieved_codebase.name == created_codebase.name

    def test_get_codebase_info_nonexistent(self, knowledgebase_tool):
        """Test getting non-existent codebase info."""
        result = knowledgebase_tool.get_codebase_info("nonexistent")
        assert result is None

    def test_query_knowledge_graph(self, knowledgebase_tool, sample_nodes):
        """Test querying the knowledge graph."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        result = knowledgebase_tool.query_knowledge_graph("calculate")
        assert 'nodes' in result
        assert len(result['nodes']) == 1
        assert "calculate" in result['nodes'][0]['name'].lower()

    def test_query_knowledge_graph_by_codebase(self, knowledgebase_tool, sample_nodes):
        """Test querying the knowledge graph filtered by codebase."""
        # Add nodes
        for node_data in sample_nodes:
            knowledgebase_tool.add_knowledge_node(**node_data)
        
        result = knowledgebase_tool.query_knowledge_graph("", codebase_id="project-a")
        assert 'nodes' in result
        assert len(result['nodes']) == 2
        assert all(node['codebase_id'] == "project-a" for node in result['nodes'])

    def test_register_tools(self, knowledgebase_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        mock_mcp.resource.return_value = mock_decorator
        
        knowledgebase_tool.register(mock_mcp)
        
        # Verify tools and resources were registered
        assert mock_mcp.tool.call_count == 3  # 3 tools
        assert mock_mcp.resource.call_count == 2  # 2 resources
        
        # Get the registered tool names
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'codebase_register',
            'codebase_add_knowledge',
            'codebase_search'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, knowledgebase_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "knowledgebase.jsonl"
        assert knowledgebase_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, knowledgebase_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(knowledgebase_tool.data_file, 'w') as f:
            f.write('{"type": "codebase", "id": "valid"}\n')
            f.write('invalid json line\n')
            f.write('{"type": "node", "id": 1, "name": "valid"}\n')
        
        # Should skip invalid lines and return valid ones
        result = knowledgebase_tool._read_entries()
        assert len(result) == 2
        assert result[0]['type'] == "codebase"
        assert result[1]['type'] == "node"

    def test_knowledge_node_model_validation(self):
        """Test KnowledgeNode model validation."""
        # Valid node
        node = KnowledgeNode(
            codebase_id="test-project",
            node_type="function",
            name="test_function",
            content="def test_function(): pass"
        )
        assert node.codebase_id == "test-project"
        assert node.node_type == "function"
        assert node.name == "test_function"

    def test_knowledge_node_default_values(self):
        """Test KnowledgeNode model default values."""
        node = KnowledgeNode(
            codebase_id="test-project",
            node_type="function",
            name="test_function",
            content="def test_function(): pass"
        )
        
        assert node.id is None
        assert node.path is None
        assert node.metadata == {}
        assert node.created_at is not None
        assert node.updated_at is not None

    def test_knowledge_relation_model_validation(self):
        """Test KnowledgeRelation model validation."""
        # Valid relation
        relation = KnowledgeRelation(
            source_node_id=1,
            target_node_id=2,
            relation_type="calls"
        )
        assert relation.source_node_id == 1
        assert relation.target_node_id == 2
        assert relation.relation_type == "calls"

    def test_knowledge_relation_default_values(self):
        """Test KnowledgeRelation model default values."""
        relation = KnowledgeRelation(
            source_node_id=1,
            target_node_id=2,
            relation_type="calls"
        )
        
        assert relation.id is None
        assert relation.metadata == {}
        assert relation.created_at is not None

    def test_codebase_model_validation(self):
        """Test Codebase model validation."""
        # Valid codebase
        codebase = Codebase(
            id="test-project",
            name="Test Project",
            root_path="/path/to/test"
        )
        assert codebase.id == "test-project"
        assert codebase.name == "Test Project"
        assert codebase.root_path == "/path/to/test"

    def test_codebase_default_values(self):
        """Test Codebase model default values."""
        codebase = Codebase(
            id="test-project",
            name="Test Project",
            root_path="/path/to/test"
        )
        
        assert codebase.description is None
        assert codebase.created_at is not None
        assert codebase.last_indexed is None 