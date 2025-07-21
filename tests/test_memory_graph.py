import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from tools.memory_graph.memory_graph import MemoryGraphTool


class TestMemoryGraphTool:
    """Test suite for MemoryGraphTool."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def memory_tool(self, temp_data_dir):
        """Create a MemoryGraphTool instance for testing."""
        return MemoryGraphTool(temp_data_dir)

    @pytest.fixture
    def sample_entities(self):
        """Sample entities for testing."""
        return [
            {"name": "Alice", "entityType": "person", "age": 30},
            {"name": "Bob", "entityType": "person", "age": 25},
            {"name": "Project Alpha", "entityType": "project", "status": "active"}
        ]

    @pytest.fixture
    def sample_relations(self):
        """Sample relations for testing."""
        return [
            {"from": "Alice", "to": "Bob", "relationType": "knows"},
            {"from": "Alice", "to": "Project Alpha", "relationType": "works_on"},
            {"from": "Bob", "to": "Project Alpha", "relationType": "contributes_to"}
        ]

    @pytest.fixture
    def sample_observations(self):
        """Sample observations for testing."""
        return [
            {"entityName": "Alice", "contents": ["Alice is a software engineer", "Alice likes coffee"]},
            {"entityName": "Bob", "contents": ["Bob is a designer", "Bob works remotely"]}
        ]

    def test_name_property(self, memory_tool):
        """Test that the tool name is correct."""
        assert memory_tool.name == "memory_graph"

    def test_description_property(self, memory_tool):
        """Test that the tool description is correct."""
        assert memory_tool.description == "Persistent memory graph for entities, relations, and observations."

    def test_get_capabilities(self, memory_tool):
        """Test that all expected capabilities are returned."""
        capabilities = memory_tool.get_capabilities()
        expected_capabilities = [
            "create_entities",
            "create_relations", 
            "add_observations",
            "delete_entities",
            "delete_observations",
            "delete_relations",
            "read_graph",
            "search_nodes",
            "open_nodes",
        ]
        assert set(capabilities) == set(expected_capabilities)

    def test_read_graph_empty_file(self, memory_tool):
        """Test reading an empty graph file."""
        result = memory_tool._read_graph()
        assert result == []

    def test_read_graph_with_data(self, memory_tool, sample_entities):
        """Test reading a graph file with existing data."""
        # Write some test data
        with open(memory_tool.data_file, 'w') as f:
            for entity in sample_entities:
                entity['type'] = 'entity'
                f.write(json.dumps(entity) + '\n')
        
        result = memory_tool._read_graph()
        assert len(result) == 3
        assert all('type' in entity for entity in result)
        assert all(entity['type'] == 'entity' for entity in result)

    def test_write_graph(self, memory_tool, sample_entities):
        """Test writing data to the graph file."""
        for entity in sample_entities:
            entity['type'] = 'entity'
        
        memory_tool._write_graph(sample_entities)
        
        # Verify the data was written correctly
        with open(memory_tool.data_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 3
        for i, line in enumerate(lines):
            entity = json.loads(line.strip())
            assert entity['name'] == sample_entities[i]['name']
            assert entity['type'] == 'entity'

    def test_create_entities_new(self, memory_tool, sample_entities):
        """Test creating new entities."""
        result = memory_tool.create_entities(sample_entities)
        assert result == sample_entities
        
        # Verify entities were written to file
        graph = memory_tool._read_graph()
        assert len(graph) == 3
        assert all(entity['type'] == 'entity' for entity in graph)

    def test_create_entities_duplicate(self, memory_tool, sample_entities):
        """Test creating entities with duplicates."""
        # Create entities first time
        memory_tool.create_entities(sample_entities)
        
        # Try to create the same entities again
        result = memory_tool.create_entities(sample_entities)
        assert result == []  # No new entities should be created
        
        # Verify only original entities exist
        graph = memory_tool._read_graph()
        assert len(graph) == 3

    def test_create_entities_partial_duplicate(self, memory_tool, sample_entities):
        """Test creating entities where some are duplicates."""
        # Create first two entities
        memory_tool.create_entities(sample_entities[:2])
        
        # Try to create all three entities
        result = memory_tool.create_entities(sample_entities)
        assert len(result) == 1  # Only the third entity should be new
        assert result[0]['name'] == "Project Alpha"

    def test_create_relations_new(self, memory_tool, sample_relations):
        """Test creating new relations."""
        result = memory_tool.create_relations(sample_relations)
        assert result == sample_relations
        
        # Verify relations were written to file
        graph = memory_tool._read_graph()
        assert len(graph) == 3
        assert all(relation['type'] == 'relation' for relation in graph)

    def test_create_relations_duplicate(self, memory_tool, sample_relations):
        """Test creating relations with duplicates."""
        # Create relations first time
        memory_tool.create_relations(sample_relations)
        
        # Try to create the same relations again
        result = memory_tool.create_relations(sample_relations)
        assert result == []  # No new relations should be created

    def test_add_observations_new(self, memory_tool, sample_entities, sample_observations):
        """Test adding observations to existing entities."""
        # First create entities
        memory_tool.create_entities(sample_entities[:2])  # Alice and Bob
        
        # Add observations
        result = memory_tool.add_observations(sample_observations)
        assert len(result) == 2
        
        # Verify observations were added
        graph = memory_tool._read_graph()
        alice = next(e for e in graph if e['name'] == 'Alice')
        bob = next(e for e in graph if e['name'] == 'Bob')
        
        assert 'observations' in alice
        assert len(alice['observations']) == 2
        assert 'Alice is a software engineer' in alice['observations']
        assert 'Alice likes coffee' in alice['observations']
        
        assert 'observations' in bob
        assert len(bob['observations']) == 2
        assert 'Bob is a designer' in bob['observations']
        assert 'Bob works remotely' in bob['observations']

    def test_add_observations_duplicate(self, memory_tool, sample_entities, sample_observations):
        """Test adding duplicate observations."""
        # First create entities and add observations
        memory_tool.create_entities(sample_entities[:2])
        memory_tool.add_observations(sample_observations)
        
        # Try to add the same observations again
        result = memory_tool.add_observations(sample_observations)
        assert len(result) == 2
        
        # Verify no duplicate observations were added
        graph = memory_tool._read_graph()
        alice = next(e for e in graph if e['name'] == 'Alice')
        assert len(alice['observations']) == 2  # Should still be 2, not 4

    def test_add_observations_nonexistent_entity(self, memory_tool, sample_observations):
        """Test adding observations to non-existent entities."""
        result = memory_tool.add_observations(sample_observations)
        assert result == []  # No entities to update

    def test_delete_entities(self, memory_tool, sample_entities, sample_relations):
        """Test deleting entities and their related relations."""
        # Create entities and relations
        memory_tool.create_entities(sample_entities)
        memory_tool.create_relations(sample_relations)
        
        # Delete Alice
        memory_tool.delete_entities(["Alice"])
        
        # Verify Alice and related relations are gone
        graph = memory_tool._read_graph()
        entity_names = [e['name'] for e in graph if e.get('type') == 'entity']
        assert "Alice" not in entity_names
        assert "Bob" in entity_names
        assert "Project Alpha" in entity_names
        
        # Verify relations involving Alice are gone
        relations = [r for r in graph if r.get('type') == 'relation']
        assert len(relations) == 1  # Only Bob -> Project Alpha should remain
        assert relations[0]['from'] == "Bob"
        assert relations[0]['to'] == "Project Alpha"

    def test_delete_observations(self, memory_tool, sample_entities, sample_observations):
        """Test deleting specific observations."""
        # Create entities and add observations
        memory_tool.create_entities(sample_entities[:2])
        memory_tool.add_observations(sample_observations)
        
        # Delete one observation from Alice
        deletions = [{"entityName": "Alice", "observations": ["Alice likes coffee"]}]
        memory_tool.delete_observations(deletions)
        
        # Verify the observation was deleted
        graph = memory_tool._read_graph()
        alice = next(e for e in graph if e['name'] == 'Alice')
        assert len(alice['observations']) == 1
        assert "Alice is a software engineer" in alice['observations']
        assert "Alice likes coffee" not in alice['observations']

    def test_delete_relations(self, memory_tool, sample_relations):
        """Test deleting specific relations."""
        # Create relations
        memory_tool.create_relations(sample_relations)
        
        # Delete one relation
        to_delete = [{"from": "Alice", "to": "Bob", "relationType": "knows"}]
        memory_tool.delete_relations(to_delete)
        
        # Verify the relation was deleted
        graph = memory_tool._read_graph()
        relations = [r for r in graph if r.get('type') == 'relation']
        assert len(relations) == 2  # Should have 2 remaining relations
        
        # Verify the specific relation is gone
        relation_tuples = [(r['from'], r['to'], r['relationType']) for r in relations]
        assert ("Alice", "Bob", "knows") not in relation_tuples

    def test_read_graph(self, memory_tool, sample_entities, sample_relations):
        """Test reading the entire graph."""
        # Create some data
        memory_tool.create_entities(sample_entities)
        memory_tool.create_relations(sample_relations)
        
        # Read the graph
        result = memory_tool.read_graph()
        assert len(result) == 6  # 3 entities + 3 relations
        
        # Verify entities and relations are present
        entities = [e for e in result if e.get('type') == 'entity']
        relations = [r for r in result if r.get('type') == 'relation']
        assert len(entities) == 3
        assert len(relations) == 3

    def test_search_nodes_by_name(self, memory_tool, sample_entities):
        """Test searching nodes by name."""
        memory_tool.create_entities(sample_entities)
        
        result = memory_tool.search_nodes("Alice")
        assert len(result) == 1
        assert result[0]['name'] == "Alice"

    def test_search_nodes_by_entity_type(self, memory_tool, sample_entities):
        """Test searching nodes by entity type."""
        memory_tool.create_entities(sample_entities)
        
        result = memory_tool.search_nodes("person")
        assert len(result) == 2  # Alice and Bob are both persons

    def test_search_nodes_by_observation(self, memory_tool, sample_entities, sample_observations):
        """Test searching nodes by observation content."""
        memory_tool.create_entities(sample_entities[:2])
        memory_tool.add_observations(sample_observations)
        
        result = memory_tool.search_nodes("software engineer")
        assert len(result) == 1
        assert result[0]['name'] == "Alice"

    def test_search_nodes_case_insensitive(self, memory_tool, sample_entities):
        """Test that search is case insensitive."""
        memory_tool.create_entities(sample_entities)
        
        result = memory_tool.search_nodes("alice")
        assert len(result) == 1
        assert result[0]['name'] == "Alice"

    def test_open_nodes_entities(self, memory_tool, sample_entities):
        """Test opening specific entity nodes."""
        memory_tool.create_entities(sample_entities)
        
        result = memory_tool.open_nodes(["Alice", "Bob"])
        assert len(result) == 2
        names = [e['name'] for e in result if e.get('type') == 'entity']
        assert "Alice" in names
        assert "Bob" in names

    def test_open_nodes_with_relations(self, memory_tool, sample_entities, sample_relations):
        """Test opening nodes including their relations."""
        memory_tool.create_entities(sample_entities)
        memory_tool.create_relations(sample_relations)
        
        result = memory_tool.open_nodes(["Alice"])
        assert len(result) == 3  # Alice entity + 2 relations involving Alice
        
        # Verify we get Alice and her relations
        alice_entity = next(e for e in result if e.get('type') == 'entity' and e['name'] == 'Alice')
        alice_relations = [r for r in result if r.get('type') == 'relation' and r['from'] == 'Alice']
        assert alice_entity is not None
        assert len(alice_relations) == 2

    def test_open_nodes_nonexistent(self, memory_tool):
        """Test opening non-existent nodes."""
        result = memory_tool.open_nodes(["Nonexistent"])
        assert result == []

    def test_register_tools(self, memory_tool):
        """Test that all tools are registered with MCP."""
        mock_mcp = Mock()
        # Mock the tool decorator to return a decorator that captures the function
        mock_decorator = Mock()
        mock_mcp.tool.return_value = mock_decorator
        
        memory_tool.register(mock_mcp)
        
        # Verify all expected tools were registered
        assert mock_mcp.tool.call_count == 9  # Number of tools in the class
        assert mock_decorator.call_count == 9  # Each tool function should be decorated
        
        # Get the registered tool names from the decorator calls
        registered_tools = []
        for call in mock_decorator.call_args_list:
            if call.args and hasattr(call.args[0], '__name__'):
                registered_tools.append(call.args[0].__name__)
        
        expected_tools = [
            'memory_create_entities',
            'memory_create_relations',
            'memory_add_observations',
            'memory_delete_entities',
            'memory_delete_observations',
            'memory_delete_relations',
            'memory_read_graph',
            'memory_search_nodes',
            'memory_open_nodes'
        ]
        
        # Verify all expected tools were registered
        for tool_name in expected_tools:
            assert tool_name in registered_tools

    def test_data_file_path(self, memory_tool, temp_data_dir):
        """Test that the data file path is correctly set."""
        expected_path = temp_data_dir / "memory_graph.jsonl"
        assert memory_tool.data_file == expected_path

    def test_corrupted_jsonl_file(self, memory_tool):
        """Test handling of corrupted JSONL file."""
        # Write corrupted data to the file
        with open(memory_tool.data_file, 'w') as f:
            f.write('{"valid": "json"}\n')
            f.write('invalid json line\n')
            f.write('{"another": "valid"}\n')
        
        # Should skip invalid lines and return valid ones
        result = memory_tool._read_graph()
        assert len(result) == 2
        assert result[0]['valid'] == 'json'
        assert result[1]['another'] == 'valid' 