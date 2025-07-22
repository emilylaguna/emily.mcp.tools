"""
Tests for Unified Knowledge Graph Tool - Phase 3.3
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List

try:
    from core import create_test_memory_store
    from models import MemoryEntity, MemoryRelation
    from tools.knowledgebase.unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool
    from tools.knowledgebase.graph_algorithms import GraphAlgorithms
except ImportError:
    try:
        from core import create_test_memory_store
        from models import MemoryEntity, MemoryRelation
        from unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool
        from graph_algorithms import GraphAlgorithms
    except ImportError:
        from core import create_test_memory_store
        from models import MemoryEntity, MemoryRelation
        from tools.knowledgebase.unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool
        from tools.knowledgebase.graph_algorithms import GraphAlgorithms


class TestUnifiedKnowledgeGraphTool(unittest.TestCase):
    """Test cases for UnifiedKnowledgeGraphTool."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory_store = create_test_memory_store()
        
        # The UnifiedMemoryStore should have already initialized the schema in __init__
        # Just verify it's working correctly
        if not self.memory_store.db_manager.verify_schema():
            raise RuntimeError("Schema initialization failed in UnifiedMemoryStore")
        
        self.graph_tool = UnifiedKnowledgeGraphTool(self.memory_store)
        
        # Create some test entities
        self.alice = MemoryEntity(
            type="person",
            name="Alice",
            content="Software engineer working on the project",
            tags=["engineer", "frontend"]
        )
        
        self.bob = MemoryEntity(
            type="person", 
            name="Bob",
            content="Product manager for the project",
            tags=["manager", "product"]
        )
        
        self.project = MemoryEntity(
            type="project",
            name="Web App Project",
            content="A modern web application",
            tags=["web", "app"]
        )
        
        self.file1 = MemoryEntity(
            type="file",
            name="main.py",
            content="Main application file",
            tags=["python", "main"]
        )
        
        self.file2 = MemoryEntity(
            type="file",
            name="utils.py", 
            content="Utility functions",
            tags=["python", "utils"]
        )
    
    def tearDown(self):
        """Clean up test environment."""
        self.memory_store.close()
    
    def test_create_entity(self):
        """Test creating entities."""
        # Test with MemoryEntity object
        saved_entity = self.graph_tool.create_entity(self.alice)
        self.assertIsNotNone(saved_entity.id)
        self.assertEqual(saved_entity.name, "Alice")
        self.assertEqual(saved_entity.type, "person")
        
        # Test with dict
        entity_dict = {
            "type": "task",
            "name": "Fix bug",
            "content": "Fix the login bug",
            "tags": ["bug", "login"]
        }
        saved_entity2 = self.graph_tool.create_entity(entity_dict)
        self.assertIsNotNone(saved_entity2.id)
        self.assertEqual(saved_entity2.name, "Fix bug")
        self.assertEqual(saved_entity2.type, "task")
    
    def test_create_entity_with_legacy_id(self):
        """Test creating entity with legacy numeric ID."""
        entity_dict = {
            "id": 123,
            "type": "note",
            "name": "Test Note",
            "content": "Test content"
        }
        
        saved_entity = self.graph_tool.create_entity(entity_dict)
        self.assertEqual(saved_entity.metadata.get("legacy_id"), 123)
        
        # Test ID mapping
        numeric_id = self.graph_tool._get_numeric_id(saved_entity.id)
        self.assertEqual(numeric_id, 123)
        
        uuid_id = self.graph_tool._get_uuid_id(123)
        self.assertEqual(uuid_id, saved_entity.id)
    
    def test_create_relation(self):
        """Test creating relations."""
        # Create entities first
        alice = self.graph_tool.create_entity(self.alice)
        project = self.graph_tool.create_entity(self.project)
        
        # Test with MemoryRelation object
        relation = MemoryRelation(
            source_id=alice.id,
            target_id=project.id,
            relation_type="assigned_to"
        )
        saved_relation = self.graph_tool.create_relation(relation)
        self.assertIsNotNone(saved_relation.id)
        self.assertEqual(saved_relation.relation_type, "assigned_to")
        
        # Test with dict
        relation_dict = {
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "created_by"
        }
        saved_relation2 = self.graph_tool.create_relation(relation_dict)
        self.assertIsNotNone(saved_relation2.id)
        self.assertEqual(saved_relation2.relation_type, "created_by")
    
    def test_create_relation_with_legacy_ids(self):
        """Test creating relation with legacy numeric IDs."""
        # Create entities with legacy IDs
        alice = self.graph_tool.create_entity({"id": 1, "type": "person", "name": "Alice"})
        bob = self.graph_tool.create_entity({"id": 2, "type": "person", "name": "Bob"})
        
        # Create relation using numeric IDs
        relation_dict = {
            "from": 1,
            "to": 2,
            "relationType": "relates_to"
        }
        
        saved_relation = self.graph_tool.create_relation(relation_dict)
        self.assertEqual(saved_relation.source_id, alice.id)
        self.assertEqual(saved_relation.target_id, bob.id)
        self.assertEqual(saved_relation.relation_type, "relates_to")
    
    def test_get_entity(self):
        """Test getting entities by ID."""
        saved_entity = self.graph_tool.create_entity(self.alice)
        
        # Test with UUID
        retrieved_entity = self.graph_tool.get_entity(saved_entity.id)
        self.assertIsNotNone(retrieved_entity)
        self.assertEqual(retrieved_entity.name, "Alice")
        
        # Test with numeric ID
        numeric_id = self.graph_tool._get_numeric_id(saved_entity.id)
        retrieved_entity2 = self.graph_tool.get_entity(numeric_id)
        self.assertIsNotNone(retrieved_entity2)
        self.assertEqual(retrieved_entity2.name, "Alice")
        
        # Test non-existent entity
        non_existent = self.graph_tool.get_entity("non-existent-id")
        self.assertIsNone(non_existent)
    
    def test_search_entities(self):
        """Test searching entities."""
        # Create test entities
        self.graph_tool.create_entity(self.alice)
        self.graph_tool.create_entity(self.bob)
        self.graph_tool.create_entity(self.project)
        
        # Test basic search
        results = self.graph_tool.search_entities("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")
        
        # Test search with filters
        results = self.graph_tool.search_entities("", {"type": "person"})
        self.assertEqual(len(results), 2)
        
        # Test search with tags
        results = self.graph_tool.search_entities("engineer")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")
    
    def test_get_relations(self):
        """Test getting relations for an entity."""
        # Create entities and relations
        alice = self.graph_tool.create_entity(self.alice)
        bob = self.graph_tool.create_entity(self.bob)
        project = self.graph_tool.create_entity(self.project)
        
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "assigned_to"
        })
        
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": bob.id,
            "relation_type": "relates_to"
        })
        
        # Test getting all relations
        relations = self.graph_tool.get_relations(alice.id)
        self.assertEqual(len(relations), 2)
        
        # Test getting relations by type
        work_relations = self.graph_tool.get_relations(alice.id, ["assigned_to"])
        self.assertEqual(len(work_relations), 1)
        self.assertEqual(work_relations[0].relation_type, "assigned_to")
    
    def test_delete_entity(self):
        """Test deleting entities."""
        saved_entity = self.graph_tool.create_entity(self.alice)
        
        # Test successful deletion
        success = self.graph_tool.delete_entity(saved_entity.id)
        self.assertTrue(success)
        
        # Verify entity is gone
        retrieved_entity = self.graph_tool.get_entity(saved_entity.id)
        self.assertIsNone(retrieved_entity)
        
        # Test deletion with numeric ID
        entity2 = self.graph_tool.create_entity({"id": 999, "type": "note", "name": "Test"})
        numeric_id = self.graph_tool._get_numeric_id(entity2.id)
        success = self.graph_tool.delete_entity(numeric_id)
        self.assertTrue(success)
    
    def test_delete_relation(self):
        """Test deleting relations."""
        alice = self.graph_tool.create_entity(self.alice)
        bob = self.graph_tool.create_entity(self.bob)
        
        relation = self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": bob.id,
            "relation_type": "relates_to"
        })
        
        # Test successful deletion
        success = self.graph_tool.delete_relation(relation.id)
        self.assertTrue(success)
        
        # Verify relation is gone
        relations = self.graph_tool.get_relations(alice.id)
        self.assertEqual(len(relations), 0)
    
    def test_subgraph(self):
        """Test getting subgraph around an entity."""
        # Create a small graph
        alice = self.graph_tool.create_entity(self.alice)
        bob = self.graph_tool.create_entity(self.bob)
        project = self.graph_tool.create_entity(self.project)
        file1 = self.graph_tool.create_entity(self.file1)
        
        # Create relations
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "assigned_to"
        })
        
        self.graph_tool.create_relation({
            "source_id": bob.id,
            "target_id": project.id,
            "relation_type": "created_by"
        })
        
        self.graph_tool.create_relation({
            "source_id": project.id,
            "target_id": file1.id,
            "relation_type": "contains"
        })
        
        # Test subgraph with depth 1
        subgraph = self.graph_tool.subgraph(alice.id, depth=1)
        self.assertEqual(len(subgraph["entities"]), 2)  # Alice and project
        self.assertEqual(len(subgraph["relations"]), 1)  # Alice -> project
        
        # Test subgraph with depth 2
        subgraph = self.graph_tool.subgraph(alice.id, depth=2)
        self.assertEqual(len(subgraph["entities"]), 4)  # All entities
        self.assertEqual(len(subgraph["relations"]), 3)  # All relations
    
    def test_shortest_path(self):
        """Test finding shortest path between entities."""
        # Create a chain: alice -> project -> file1 -> file2
        alice = self.graph_tool.create_entity(self.alice)
        project = self.graph_tool.create_entity(self.project)
        file1 = self.graph_tool.create_entity(self.file1)
        file2 = self.graph_tool.create_entity(self.file2)
        
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "assigned_to"
        })
        
        self.graph_tool.create_relation({
            "source_id": project.id,
            "target_id": file1.id,
            "relation_type": "contains"
        })
        
        self.graph_tool.create_relation({
            "source_id": file1.id,
            "target_id": file2.id,
            "relation_type": "depends_on"
        })
        
        # Test shortest path
        path = self.graph_tool.shortest_path(alice.id, file2.id)
        self.assertEqual(len(path), 4)
        self.assertEqual(path[0], alice.id)
        self.assertEqual(path[-1], file2.id)
        
        # Test path to self
        path = self.graph_tool.shortest_path(alice.id, alice.id)
        self.assertEqual(path, [alice.id])
        
        # Test non-existent path
        path = self.graph_tool.shortest_path(alice.id, "non-existent")
        self.assertEqual(path, [])
    
    def test_find_clusters(self):
        """Test finding clusters of related entities."""
        # Create two separate clusters
        alice = self.graph_tool.create_entity(self.alice)
        bob = self.graph_tool.create_entity(self.bob)
        project = self.graph_tool.create_entity(self.project)
        
        # Cluster 1: Alice -> Project
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "assigned_to"
        })
        
        # Cluster 2: Bob (isolated)
        
        clusters = self.graph_tool.find_clusters()
        self.assertEqual(len(clusters), 1)  # Only Alice-Project cluster (size > 1)
        
        # Test clusters by type
        person_clusters = self.graph_tool.find_clusters("person")
        self.assertEqual(len(person_clusters), 0)  # No person-person connections
    
    def test_get_entity_centrality(self):
        """Test calculating entity centrality."""
        # Create a star graph
        center = self.graph_tool.create_entity({
            "type": "person",
            "name": "Center",
            "content": "Central person"
        })
        
        for i in range(3):
            node = self.graph_tool.create_entity({
                "type": "person",
                "name": f"Node{i}",
                "content": f"Node {i}"
            })
            
            self.graph_tool.create_relation({
                "source_id": center.id,
                "target_id": node.id,
                "relation_type": "relates_to"
            })
        
        # Test centrality
        center_centrality = self.graph_tool.get_entity_centrality(center.id)
        self.assertEqual(center_centrality, 3)
        
        node_centrality = self.graph_tool.get_entity_centrality(center.id)
        self.assertEqual(node_centrality, 3)  # Should be cached
    
    def test_get_related_entities(self):
        """Test getting related entities."""
        alice = self.graph_tool.create_entity(self.alice)
        bob = self.graph_tool.create_entity(self.bob)
        project = self.graph_tool.create_entity(self.project)
        
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": project.id,
            "relation_type": "assigned_to"
        })
        
        self.graph_tool.create_relation({
            "source_id": alice.id,
            "target_id": bob.id,
            "relation_type": "relates_to"
        })
        
        # Test getting all related entities
        related = self.graph_tool.get_related_entities(alice.id)
        self.assertEqual(len(related), 2)
        
        # Test filtering by relation type
        work_related = self.graph_tool.get_related_entities(alice.id, "assigned_to")
        self.assertEqual(len(work_related), 1)
        self.assertEqual(work_related[0]["name"], "Web App Project")
    
    def test_graph_search(self):
        """Test enhanced graph search."""
        self.graph_tool.create_entity(self.alice)
        self.graph_tool.create_entity(self.bob)
        self.graph_tool.create_entity(self.project)
        
        # Test search with entity type filter
        results = self.graph_tool.graph_search("", "person")
        self.assertEqual(len(results), 2)
        
        # Test search with query and type
        results = self.graph_tool.graph_search("engineer", "person")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")
    
    def test_backward_compatibility_memory_graph(self):
        """Test backward compatibility with memory_graph tool."""
        # Test create_entities
        entities = [
            {"name": "Test1", "type": "note", "content": "Test content 1"},
            {"name": "Test2", "type": "note", "content": "Test content 2"}
        ]
        created = self.graph_tool.create_entities(entities)
        self.assertEqual(len(created), 2)
        
        # Test create_relations
        relations = [
            {"from": created[0]["id"], "to": created[1]["id"], "relationType": "relates_to"}
        ]
        created_relations = self.graph_tool.create_relations(relations)
        self.assertEqual(len(created_relations), 1)
        
        # Test add_observations
        observations = [
            {"entityName": "Test1", "contents": ["Observation 1", "Observation 2"]}
        ]
        updated = self.graph_tool.add_observations(observations)
        self.assertEqual(len(updated), 1)
        
        # Test read_graph
        graph = self.graph_tool.read_graph()
        self.assertGreater(len(graph), 0)
        
        # Test search_nodes
        results = self.graph_tool.search_nodes("Test1")
        self.assertEqual(len(results), 1)
        
        # Test open_nodes
        results = self.graph_tool.open_nodes(["Test1"])
        self.assertEqual(len(results), 1)
    
    def test_backward_compatibility_knowledgebase(self):
        """Test backward compatibility with knowledgebase tool."""
        # Test codebase registration
        codebase = self.graph_tool.create_entity({
            "type": "project",
            "name": "Test Codebase",
            "content": "A test codebase",
            "metadata": {
                "codebase_id": "test-123",
                "root_path": "/test/path",
                "legacy_type": "codebase"
            }
        })
        
        # Test adding knowledge nodes
        knowledge_node = self.graph_tool.create_entity({
            "type": "file",
            "name": "test_function",
            "content": "def test_function(): pass",
            "metadata": {
                "codebase_id": "test-123",
                "path": "/test/file.py"
            }
        })
        
        # Create relation to codebase
        self.graph_tool.create_relation({
            "source_id": codebase.id,
            "target_id": knowledge_node.id,
            "relation_type": "contains"
        })
        
        # Test searching codebase knowledge
        results = self.graph_tool.search_entities("test_function", {"type": "file"})
        self.assertEqual(len(results), 1)
    
    def test_performance_optimizations(self):
        """Test performance optimizations."""
        # Create many entities and relations
        entities = []
        for i in range(10):
            entity = self.graph_tool.create_entity({
                "type": "person",
                "name": f"Person{i}",
                "content": f"Person {i} description"
            })
            entities.append(entity)
        
        # Create relations in a chain
        for i in range(len(entities) - 1):
            self.graph_tool.create_relation({
                "source_id": entities[i].id,
                "target_id": entities[i + 1].id,
                "relation_type": "relates_to"
            })
        
        # Test that centrality caching works
        centrality1 = self.graph_tool.get_entity_centrality(entities[0].id)
        centrality2 = self.graph_tool.get_entity_centrality(entities[0].id)
        self.assertEqual(centrality1, centrality2)
        
        # Test that cache is invalidated on relation deletion
        relations = self.graph_tool.get_relations(entities[0].id)
        if relations:
            self.graph_tool.delete_relation(relations[0].id)
            centrality3 = self.graph_tool.get_entity_centrality(entities[0].id)
            self.assertNotEqual(centrality1, centrality3)


class TestGraphAlgorithms(unittest.TestCase):
    """Test cases for GraphAlgorithms."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a simple test graph
        self.adjacency = {
            "A": ["B", "C"],
            "B": ["A", "D"],
            "C": ["A", "D"],
            "D": ["B", "C", "E"],
            "E": ["D"],
            "F": ["G"],
            "G": ["F"]
        }
    
    def test_breadth_first_search(self):
        """Test breadth-first search."""
        visited = GraphAlgorithms.breadth_first_search(self.adjacency, "A", max_depth=2)
        
        self.assertIn("A", visited)
        self.assertIn("B", visited)
        self.assertIn("C", visited)
        self.assertIn("D", visited)
        self.assertNotIn("E", visited)  # Beyond depth 2
        self.assertNotIn("F", visited)  # Disconnected component
        
        self.assertEqual(visited["A"], 0)
        self.assertEqual(visited["B"], 1)
        self.assertEqual(visited["C"], 1)
        self.assertEqual(visited["D"], 2)
    
    def test_shortest_path_bfs(self):
        """Test shortest path finding."""
        # Test path exists
        path = GraphAlgorithms.shortest_path_bfs(self.adjacency, "A", "E")
        self.assertEqual(path, ["A", "B", "D", "E"])
        
        # Test path to self
        path = GraphAlgorithms.shortest_path_bfs(self.adjacency, "A", "A")
        self.assertEqual(path, ["A"])
        
        # Test no path exists
        path = GraphAlgorithms.shortest_path_bfs(self.adjacency, "A", "F")
        self.assertEqual(path, [])
    
    def test_find_connected_components(self):
        """Test finding connected components."""
        components = GraphAlgorithms.find_connected_components(self.adjacency)
        
        # Should find 2 components: A-B-C-D-E and F-G
        self.assertEqual(len(components), 2)
        
        # Check component sizes
        component_sizes = [len(comp) for comp in components]
        self.assertIn(5, component_sizes)  # A-B-C-D-E
        self.assertIn(2, component_sizes)  # F-G
    
    def test_find_clusters_by_type(self):
        """Test finding clusters by type."""
        node_types = {
            "A": "person",
            "B": "person", 
            "C": "person",
            "D": "project",
            "E": "project",
            "F": "person",
            "G": "person"
        }
        
        # Test clusters of people
        person_clusters = GraphAlgorithms.find_clusters_by_type(
            self.adjacency, node_types, "person"
        )
        self.assertEqual(len(person_clusters), 2)  # A-B-C and F-G
        
        # Test clusters of projects
        project_clusters = GraphAlgorithms.find_clusters_by_type(
            self.adjacency, node_types, "project"
        )
        self.assertEqual(len(project_clusters), 1)  # D-E
    
    def test_calculate_degree_centrality(self):
        """Test degree centrality calculation."""
        centrality = GraphAlgorithms.calculate_degree_centrality(self.adjacency)
        
        # D has the most connections (3)
        self.assertEqual(centrality["D"], 3.0 / 6.0)  # 3 connections / (7-1) nodes
        
        # A, B, C have 2 connections each
        self.assertEqual(centrality["A"], 2.0 / 6.0)
        self.assertEqual(centrality["B"], 2.0 / 6.0)
        self.assertEqual(centrality["C"], 2.0 / 6.0)
        
        # E, F, G have 1 connection each
        self.assertEqual(centrality["E"], 1.0 / 6.0)
        self.assertEqual(centrality["F"], 1.0 / 6.0)
        self.assertEqual(centrality["G"], 1.0 / 6.0)
    
    def test_calculate_graph_metrics(self):
        """Test graph metrics calculation."""
        metrics = GraphAlgorithms.calculate_graph_metrics(self.adjacency)
        
        self.assertEqual(metrics["num_nodes"], 7)
        self.assertEqual(metrics["num_edges"], 6)
        self.assertEqual(metrics["num_components"], 2)
        self.assertEqual(metrics["largest_component_size"], 5)
        self.assertGreater(metrics["avg_degree"], 0)
        self.assertGreater(metrics["density"], 0)
        self.assertGreater(metrics["avg_path_length"], 0)


if __name__ == "__main__":
    unittest.main() 