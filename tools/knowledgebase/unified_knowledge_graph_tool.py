"""
Unified Knowledge Graph Tool - Phase 3.3
Integrates knowledgebase and memory_graph functionality using UnifiedMemoryStore.
"""

import json
import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

try:
    from ...core import UnifiedMemoryStore
    from ...models import MemoryEntity, MemoryRelation, MemoryContext
    from ..base import BaseTool
except ImportError:
    try:
        from core import UnifiedMemoryStore
        from models import MemoryEntity, MemoryRelation, MemoryContext
        from tools.base import BaseTool
    except ImportError:
        from core import UnifiedMemoryStore
        from models import MemoryEntity, MemoryRelation, MemoryContext
        from base import BaseTool

logger = logging.getLogger(__name__)


class UnifiedKnowledgeGraphTool(BaseTool):
    """Knowledge & Memory Graph interface backed by UnifiedMemoryStore."""
    
    def __init__(self, memory_store: UnifiedMemoryStore, data_dir: Optional[Path] = None):
        # Initialize BaseTool with data_dir if provided
        if data_dir:
            super().__init__(data_dir)
        else:
            # Create a temporary data directory for testing
            import tempfile
            temp_dir = Path(tempfile.mkdtemp())
            super().__init__(temp_dir)
        
        self.memory = memory_store
        self.tool_name = "knowledge_graph"
        
        # ID mapping for backward compatibility
        self._id_mapping: Dict[int, str] = {}
        self._reverse_mapping: Dict[str, int] = {}
        self._next_numeric_id = 1
        
        # Cache for performance optimization
        self._relation_counts: Dict[str, int] = {}
        self._centrality_cache: Dict[str, float] = {}
        
    @property
    def name(self) -> str:
        return "knowledge_graph"
    
    @property
    def description(self) -> str:
        return "Unified knowledge graph for entities, relations, and codebase knowledge"
    
    def get_capabilities(self) -> List[str]:
        return [
            "create_entity",
            "create_relation", 
            "get_entity",
            "search_entities",
            "get_relations",
            "delete_entity",
            "delete_relation",
            "subgraph",
            "shortest_path",
            "find_clusters",
            "graph_search",
            "get_entity_centrality",
            "get_related_entities"
        ]
    
    def _get_numeric_id(self, uuid_id: str) -> int:
        """Map UUID to numeric ID for backward compatibility."""
        if uuid_id not in self._reverse_mapping:
            self._reverse_mapping[uuid_id] = self._next_numeric_id
            self._id_mapping[self._next_numeric_id] = uuid_id
            self._next_numeric_id += 1
        return self._reverse_mapping[uuid_id]
    
    def _get_uuid_id(self, numeric_id: int) -> Optional[str]:
        """Map numeric ID to UUID for backward compatibility."""
        return self._id_mapping.get(numeric_id)
    
    def _load_id_mapping(self) -> None:
        """Load existing ID mappings from the database."""
        try:
            entities = self.memory.search("", limit=1000)
            for entity in entities:
                if 'id' in entity:
                    numeric_id = entity.get('metadata', {}).get('legacy_id')
                    if numeric_id:
                        self._id_mapping[numeric_id] = entity['id']
                        self._reverse_mapping[entity['id']] = numeric_id
                        self._next_numeric_id = max(self._next_numeric_id, numeric_id + 1)
        except Exception as e:
            logger.warning(f"Failed to load ID mapping: {e}")
    
    def create_entity(self, entity: Union[MemoryEntity, Dict]) -> MemoryEntity:
        """Create a new entity in the knowledge graph."""
        if isinstance(entity, dict):
            # Handle legacy format
            entity_type = entity.get('type', 'note')
            name = entity.get('name', '')
            content = entity.get('content', '')
            metadata = entity.get('metadata', {})
            tags = entity.get('tags', [])
            
            # Preserve legacy ID if present
            if 'id' in entity and isinstance(entity['id'], int):
                metadata['legacy_id'] = entity['id']
            
            entity = MemoryEntity(
                type=entity_type,
                name=name,
                content=content,
                metadata=metadata,
                tags=tags
            )
        
        # Save to unified store
        saved_entity = self.memory.save_entity(entity)
        
        # Update ID mapping
        if 'legacy_id' in saved_entity.metadata:
            numeric_id = saved_entity.metadata['legacy_id']
            self._id_mapping[numeric_id] = saved_entity.id
            self._reverse_mapping[saved_entity.id] = numeric_id
        
        return saved_entity
    
    def create_relation(self, relation: Union[MemoryRelation, Dict]) -> MemoryRelation:
        """Create a new relation in the knowledge graph."""
        if isinstance(relation, dict):
            # Handle legacy format
            source_id = relation.get('from') or relation.get('source_id')
            target_id = relation.get('to') or relation.get('target_id')
            relation_type = relation.get('relationType') or relation.get('relation_type')
            metadata = relation.get('metadata', {})
            
            # Convert numeric IDs to UUIDs
            if isinstance(source_id, int):
                source_id = self._get_uuid_id(source_id)
            if isinstance(target_id, int):
                target_id = self._get_uuid_id(target_id)
            
            if not source_id or not target_id:
                raise ValueError("Invalid source or target ID")
            
            relation = MemoryRelation(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                metadata=metadata
            )
        
        # Save to unified store
        saved_relation = self.memory.save_relation(relation)
        
        # Invalidate caches
        self._relation_counts.clear()
        self._centrality_cache.clear()
        
        return saved_relation
    
    def get_entity(self, entity_id: Union[str, int]) -> Optional[MemoryEntity]:
        """Get an entity by ID."""
        if isinstance(entity_id, int):
            entity_id = self._get_uuid_id(entity_id)
            if not entity_id:
                return None
        
        return self.memory.get_entity(entity_id)
    
    def search_entities(self, query: str, filters: Optional[Dict] = None, limit: int = 20) -> List[Dict]:
        """Search entities using semantic and keyword search."""
        results = self.memory.search(query, filters, limit)
        
        # Convert to legacy format for backward compatibility
        legacy_results = []
        for result in results:
            legacy_result = {
                'id': self._get_numeric_id(result['id']),
                'type': result['type'],
                'name': result['name'],
                'content': result.get('content', ''),
                'metadata': result.get('metadata', {}),
                'tags': result.get('tags', []),
                'created_at': result.get('created_at'),
                'updated_at': result.get('updated_at'),
                'score': result.get('score', 0.0)
            }
            legacy_results.append(legacy_result)
        
        return legacy_results
    
    def get_relations(self, entity_id: Union[str, int], relation_types: Optional[List[str]] = None) -> List[MemoryRelation]:
        """Get relations for an entity."""
        if isinstance(entity_id, int):
            entity_id = self._get_uuid_id(entity_id)
            if not entity_id:
                return []
        
        related = self.memory.get_related(entity_id, relation_types)
        
        # Convert to MemoryRelation objects
        relations = []
        for rel_data in related:
            # The get_related method returns both relation and entity data
            # We need to determine which entity is the source and which is the target
            related_entity_id = rel_data.get('id')  # This is the related entity's ID
            
            # Determine source and target based on the relation direction
            # We need to check if the current entity is the source or target
            # For now, we'll assume the current entity is always the source
            # This is a simplification - in a real implementation we'd need to check the relation direction
            
            relation = MemoryRelation(
                id=rel_data.get('relation_id', str(uuid.uuid4())),
                source_id=entity_id,  # Current entity is source
                target_id=related_entity_id,  # Related entity is target
                relation_type=rel_data.get('relation_type', 'relates_to'),
                strength=rel_data.get('strength', 1.0),
                metadata=rel_data.get('relation_metadata', {}),
                created_at=rel_data.get('created_at', datetime.now(UTC))
            )
            relations.append(relation)
        
        return relations
    
    def delete_entity(self, entity_id: Union[str, int]) -> bool:
        """Delete an entity and its relations."""
        if isinstance(entity_id, int):
            entity_id = self._get_uuid_id(entity_id)
            if not entity_id:
                return False
        
        success = self.memory.delete_entity(entity_id)
        if success:
            # Clean up ID mapping
            if entity_id in self._reverse_mapping:
                numeric_id = self._reverse_mapping[entity_id]
                del self._id_mapping[numeric_id]
                del self._reverse_mapping[entity_id]
            
            # Invalidate caches
            self._relation_counts.clear()
            self._centrality_cache.clear()
        
        return success
    
    def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        success = self.memory.delete_relation(relation_id)
        if success:
            # Invalidate caches
            self._relation_counts.clear()
            self._centrality_cache.clear()
        
        return success
    
    def subgraph(self, root_id: Union[str, int], depth: int = 2) -> Dict:
        """Get a subgraph around a root entity."""
        if isinstance(root_id, int):
            root_id = self._get_uuid_id(root_id)
            if not root_id:
                return {'entities': [], 'relations': []}
        
        entities = []
        relations = []
        visited = set()
        seen_relations = set()  # Track seen relations to avoid duplicates
        queue = [(root_id, 0)]
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            # Get entity
            entity = self.memory.get_entity(current_id)
            if entity:
                entities.append(entity.to_dict())
            
            # Get relations and neighbors
            if current_depth < depth:
                entity_relations = self.memory.get_related(current_id)
                for rel_data in entity_relations:
                    # Determine source and target based on the relation direction
                    # We need to check if the current entity is the source or target
                    # by querying the relation directly
                    relation_id = rel_data.get('relation_id')
                    if relation_id:
                        # Get the actual relation to determine source/target
                        actual_relation = self.memory.get_relation_by_id(relation_id)
                        if actual_relation:
                            source_id = actual_relation.source_id
                            target_id = actual_relation.target_id
                        else:
                            # Fallback: assume current entity is source
                            source_id = current_id
                            target_id = rel_data.get('id')
                    else:
                        # Fallback: assume current entity is source
                        source_id = current_id
                        target_id = rel_data.get('id')
                    
                    # Create a relation dict for the subgraph
                    relation_dict = {
                        'id': relation_id,
                        'source_id': source_id,
                        'target_id': target_id,
                        'relation_type': rel_data.get('relation_type'),
                        'strength': rel_data.get('strength', 1.0),
                        'metadata': rel_data.get('relation_metadata', {})
                    }
                    
                    # Only add if we haven't seen this relation before
                    relation_key = f"{source_id}:{target_id}:{rel_data.get('relation_type')}"
                    if relation_key not in seen_relations:
                        relations.append(relation_dict)
                        seen_relations.add(relation_key)
                    
                    # Add neighbors to queue
                    neighbor_id = rel_data.get('id')
                    if neighbor_id and neighbor_id not in visited:
                        queue.append((neighbor_id, current_depth + 1))
        
        return {
            'entities': entities,
            'relations': relations,
            'root_id': root_id,
            'depth': depth
        }
    
    def shortest_path(self, source_id: Union[str, int], target_id: Union[str, int]) -> List[str]:
        """Find shortest path between two entities using BFS."""
        if isinstance(source_id, int):
            source_id = self._get_uuid_id(source_id)
        if isinstance(target_id, int):
            target_id = self._get_uuid_id(target_id)
        
        if not source_id or not target_id:
            return []
        
        if source_id == target_id:
            return [source_id]
        
        # BFS implementation
        queue = [(source_id, [source_id])]
        visited = {source_id}
        
        while queue:
            current_id, path = queue.pop(0)
            
            # Get neighbors
            relations = self.memory.get_related(current_id)
            for rel_data in relations:
                neighbor_id = rel_data.get('id')
                
                if neighbor_id == target_id:
                    return path + [neighbor_id]
                
                if neighbor_id and neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []
    
    def find_clusters(self, entity_type: Optional[str] = None) -> List[List[str]]:
        """Find clusters of related entities using connected components."""
        # Get all entities
        entities = self.memory.get_all_entities(entity_type, limit=1000)
        
        # Build adjacency list
        adjacency = {}
        for entity in entities:
            entity_id = entity['id']
            adjacency[entity_id] = []
            
            # Get relations
            relations = self.memory.get_related(entity_id)
            for rel_data in relations:
                neighbor_id = rel_data.get('id')
                if neighbor_id:
                    # If filtering by entity type, only include neighbors of the same type
                    if entity_type:
                        neighbor_entity = self.memory.get_entity(neighbor_id)
                        if neighbor_entity and neighbor_entity.type == entity_type:
                            adjacency[entity_id].append(neighbor_id)
                    else:
                        adjacency[entity_id].append(neighbor_id)
        
        # Find connected components
        visited = set()
        clusters = []
        
        def dfs(node: str, cluster: List[str]):
            if node in visited:
                return
            visited.add(node)
            cluster.append(node)
            
            for neighbor in adjacency.get(node, []):
                dfs(neighbor, cluster)
        
        for entity_id in adjacency:
            if entity_id not in visited:
                cluster = []
                dfs(entity_id, cluster)
                if len(cluster) > 1:  # Only include clusters with multiple entities
                    clusters.append(cluster)
        
        return clusters
    
    def get_entity_centrality(self, entity_id: Union[str, int]) -> float:
        """Calculate centrality score for an entity."""
        if isinstance(entity_id, int):
            entity_id = self._get_uuid_id(entity_id)
            if not entity_id:
                return 0.0
        
        # Check cache first
        if entity_id in self._centrality_cache:
            return self._centrality_cache[entity_id]
        
        # Calculate degree centrality
        relations = self.memory.get_related(entity_id)
        centrality = len(relations)
        
        # Cache the result
        self._centrality_cache[entity_id] = centrality
        
        return centrality
    
    def get_related_entities(self, entity_id: Union[str, int], relation_type: Optional[str] = None) -> List[Dict]:
        """Get related entities with optional relation type filter."""
        if isinstance(entity_id, int):
            entity_id = self._get_uuid_id(entity_id)
            if not entity_id:
                return []
        
        relation_types = [relation_type] if relation_type else None
        relations = self.memory.get_related(entity_id, relation_types)
        
        # Get the actual entities
        related_entities = []
        for rel_data in relations:
            # The get_related method already returns entity data
            entity_dict = {
                'id': rel_data.get('id'),
                'type': rel_data.get('type'),
                'name': rel_data.get('name'),
                'content': rel_data.get('content'),
                'metadata': rel_data.get('metadata', {}),
                'tags': rel_data.get('tags', []),
                'created_at': rel_data.get('created_at'),
                'updated_at': rel_data.get('updated_at'),
                'relation_type': rel_data.get('relation_type'),
                'relation_strength': rel_data.get('strength', 1.0)
            }
            related_entities.append(entity_dict)
        
        return related_entities
    
    def graph_search(self, query: str, entity_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Enhanced graph search with entity type filtering."""
        filters = {'type': entity_type} if entity_type else None
        return self.search_entities(query, filters, limit)
    
    # Backward compatibility methods for memory_graph tool
    def create_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy method for creating multiple entities."""
        created = []
        for entity_data in entities:
            entity = self.create_entity(entity_data)
            created.append(entity.to_dict())
        return created
    
    def create_relations(self, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy method for creating multiple relations."""
        created = []
        for relation_data in relations:
            relation = self.create_relation(relation_data)
            created.append(relation.to_dict())
        return created
    
    def add_observations(self, observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Legacy method for adding observations to entities."""
        updated = []
        for obs_data in observations:
            entity_name = obs_data.get('entityName')
            contents = obs_data.get('contents', [])
            
            # Find entity by name
            entities = self.memory.search(entity_name, limit=1)
            if entities:
                entity = self.memory.get_entity(entities[0]['id'])
                if entity:
                    # Add observations to metadata
                    entity.metadata.setdefault('observations', [])
                    for content in contents:
                        if content not in entity.metadata['observations']:
                            entity.metadata['observations'].append(content)
                    
                    updated_entity = self.memory.update_entity(entity)
                    updated.append(updated_entity.to_dict())
        
        return updated
    
    def delete_entities(self, entity_names: List[str]) -> None:
        """Legacy method for deleting entities by name."""
        for name in entity_names:
            entities = self.memory.search(name, limit=1)
            if entities:
                self.memory.delete_entity(entities[0]['id'])
    
    def delete_observations(self, deletions: List[Dict[str, Any]]) -> None:
        """Legacy method for deleting observations."""
        for deletion in deletions:
            entity_name = deletion.get('entityName')
            observations_to_remove = deletion.get('observations', [])
            
            entities = self.memory.search(entity_name, limit=1)
            if entities:
                entity = self.memory.get_entity(entities[0]['id'])
                if entity and 'observations' in entity.metadata:
                    entity.metadata['observations'] = [
                        obs for obs in entity.metadata['observations'] 
                        if obs not in observations_to_remove
                    ]
                    self.memory.update_entity(entity)
    
    def delete_relations(self, relations: List[Dict[str, Any]]) -> None:
        """Legacy method for deleting relations."""
        for relation_data in relations:
            source_id = relation_data.get('from')
            target_id = relation_data.get('to')
            relation_type = relation_data.get('relationType')
            
            # Find and delete the relation
            if isinstance(source_id, int):
                source_id = self._get_uuid_id(source_id)
            if isinstance(target_id, int):
                target_id = self._get_uuid_id(target_id)
            
            if source_id and target_id:
                relations = self.memory.get_related(source_id)
                for rel_data in relations:
                    if (rel_data['target_id'] == target_id and 
                        rel_data['relation_type'] == relation_type):
                        self.memory.delete_relation(rel_data['id'])
                        break
    
    def read_graph(self) -> List[Dict[str, Any]]:
        """Legacy method for reading the entire graph."""
        entities = self.memory.get_all_entities(limit=1000)
        relations = self.memory.get_relations_by_type("", limit=1000)
        
        graph = []
        
        # Add entities
        for entity in entities:
            graph.append({
                'type': 'entity',
                'id': self._get_numeric_id(entity['id']),
                'name': entity['name'],
                'content': entity.get('content', ''),
                'metadata': entity.get('metadata', {}),
                'tags': entity.get('tags', [])
            })
        
        # Add relations
        for relation in relations:
            graph.append({
                'type': 'relation',
                'from': self._get_numeric_id(relation.source_id),
                'to': self._get_numeric_id(relation.target_id),
                'relationType': relation.relation_type,
                'metadata': relation.metadata
            })
        
        return graph
    
    def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        """Legacy method for searching nodes."""
        return self.search_entities(query)
    
    def open_nodes(self, names: List[str]) -> List[Dict[str, Any]]:
        """Legacy method for opening nodes by name."""
        results = []
        for name in names:
            entities = self.memory.search(name, limit=1)
            if entities:
                results.append(entities[0])
        return results
    
    def register(self, mcp):
        """Register the tool with MCP server."""
        # Import here to avoid circular imports
        from .knowledge_graph_mcp_tools import register_knowledge_graph_tools
        register_knowledge_graph_tools(mcp, self.memory) 