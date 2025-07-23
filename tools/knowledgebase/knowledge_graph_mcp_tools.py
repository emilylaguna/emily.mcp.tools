"""
MCP Integration for Unified Knowledge Graph Tool - Phase 3.3
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from .unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool
except ImportError:
    from unified_knowledge_graph_tool import UnifiedKnowledgeGraphTool

logger = logging.getLogger(__name__)


def register_knowledge_graph_tools(mcp, memory_store):
    """Register all knowledge graph MCP tools."""
    
    # Initialize the unified knowledge graph tool
    graph_tool = UnifiedKnowledgeGraphTool(memory_store)
    
    @mcp.tool(
        name="graph_find_related",
        description="Find entities related to a given entity within a specified depth using graph traversal algorithms",
        tags={"graph", "relationships", "search", "traversal", "knowledge"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_find_related(entity_id: str, depth: int = 2, ctx: Optional[object] = None) -> dict:
        """Find entities related to a given entity within a specified depth."""
        try:
            # Handle both string and numeric IDs
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            subgraph = graph_tool.subgraph(entity_id, depth)
            
            # Convert to MCP-friendly format
            result = {
                "root_id": entity_id,
                "depth": depth,
                "entities": [],
                "relations": []
            }
            
            # Add entities
            for entity in subgraph['entities']:
                result['entities'].append({
                    "id": entity['id'],
                    "type": entity['type'],
                    "name": entity['name'],
                    "content": entity.get('content', ''),
                    "tags": entity.get('tags', [])
                })
            
            # Add relations
            for relation in subgraph['relations']:
                result['relations'].append({
                    "id": relation['id'],
                    "source_id": relation['source_id'],
                    "target_id": relation['target_id'],
                    "relation_type": relation['relation_type'],
                    "strength": relation.get('strength', 1.0)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in graph_find_related: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_search",
        description="Search for entities in the knowledge graph using semantic search with optional type filtering",
        tags={"graph", "search", "entities", "semantic", "filter"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_search(query: str, entity_type: Optional[str] = None, limit: int = 20, ctx: Optional[object] = None) -> list:
        """Search for entities in the knowledge graph."""
        try:
            results = graph_tool.graph_search(query, entity_type, limit)
            return results
        except Exception as e:
            logger.error(f"Error in graph_search: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool(
        name="graph_create_entity",
        description="Create a new entity in the knowledge graph with specified properties and metadata",
        tags={"graph", "entity", "create", "knowledge", "data"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def graph_create_entity(payload: dict, ctx: Optional[object] = None) -> dict:
        """Create a new entity in the knowledge graph."""
        try:
            entity = graph_tool.create_entity(payload)
            return {
                "id": entity.id,
                "type": entity.type,
                "name": entity.name,
                "content": entity.content,
                "tags": entity.tags,
                "created_at": entity.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error in graph_create_entity: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_create_relation",
        description="Create a new relation between two entities with specified type, strength, and metadata",
        tags={"graph", "relation", "create", "connection", "knowledge"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": False
        }
    )
    async def graph_create_relation(source_id: str, target_id: str, relation_type: str, 
                                  strength: float = 1.0, metadata: Optional[Dict[str, Any]] = None, ctx: Optional[object] = None) -> dict:
        """Create a new relation between two entities."""
        try:
            # Handle numeric IDs
            if source_id.isdigit():
                source_id = int(source_id)
            if target_id.isdigit():
                target_id = int(target_id)
            
            relation_data = {
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "strength": strength,
                "metadata": metadata or {}
            }
            
            relation = graph_tool.create_relation(relation_data)
            return {
                "id": relation.id,
                "source_id": relation.source_id,
                "target_id": relation.target_id,
                "relation_type": relation.relation_type,
                "strength": relation.strength,
                "created_at": relation.created_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error in graph_create_relation: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_get_entity",
        description="Get detailed information about a specific entity by its ID including properties and metadata",
        tags={"graph", "entity", "get", "details", "retrieve"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_get_entity(entity_id: str, ctx: Optional[object] = None) -> dict:
        """Get a specific entity by ID."""
        try:
            # Handle numeric IDs
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            entity = graph_tool.get_entity(entity_id)
            if entity:
                return {
                    "id": entity.id,
                    "type": entity.type,
                    "name": entity.name,
                    "content": entity.content,
                    "tags": entity.tags,
                    "metadata": entity.metadata,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                }
            else:
                return {"error": "Entity not found"}
        except Exception as e:
            logger.error(f"Error in graph_get_entity: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_get_relations",
        description="Get all relations for a specific entity with optional filtering by relation types",
        tags={"graph", "relations", "entity", "connections", "filter"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_get_relations(entity_id: str, relation_types: Optional[List[str]] = None, ctx: Optional[object] = None) -> list:
        """Get relations for a specific entity."""
        try:
            # Handle numeric IDs
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            relations = graph_tool.get_relations(entity_id, relation_types)
            return [
                {
                    "id": rel.id,
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "relation_type": rel.relation_type,
                    "strength": rel.strength,
                    "metadata": rel.metadata,
                    "created_at": rel.created_at.isoformat()
                }
                for rel in relations
            ]
        except Exception as e:
            logger.error(f"Error in graph_get_relations: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool(
        name="graph_shortest_path",
        description="Find the shortest path between two entities using graph algorithms for relationship discovery",
        tags={"graph", "path", "algorithm", "shortest", "connection"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_shortest_path(source_id: str, target_id: str, ctx: Optional[object] = None) -> dict:
        """Find the shortest path between two entities."""
        try:
            # Handle numeric IDs
            if source_id.isdigit():
                source_id = int(source_id)
            if target_id.isdigit():
                target_id = int(target_id)
            
            path = graph_tool.shortest_path(source_id, target_id)
            
            # Get entity details for the path
            path_entities = []
            for entity_id in path:
                entity = graph_tool.get_entity(entity_id)
                if entity:
                    path_entities.append({
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.type
                    })
            
            return {
                "source_id": source_id,
                "target_id": target_id,
                "path": path,
                "entities": path_entities,
                "length": len(path)
            }
        except Exception as e:
            logger.error(f"Error in graph_shortest_path: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_find_clusters",
        description="Find clusters of related entities using community detection algorithms for pattern discovery",
        tags={"graph", "clusters", "community", "detection", "patterns"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_find_clusters(entity_type: Optional[str] = None, ctx: Optional[object] = None) -> dict:
        """Find clusters of related entities."""
        try:
            clusters = graph_tool.find_clusters(entity_type)
            
            # Get entity details for each cluster
            cluster_details = []
            for cluster in clusters:
                cluster_entities = []
                for entity_id in cluster:
                    entity = graph_tool.get_entity(entity_id)
                    if entity:
                        cluster_entities.append({
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.type
                        })
                cluster_details.append({
                    "entities": cluster_entities,
                    "size": len(cluster)
                })
            
            return {
                "entity_type": entity_type,
                "clusters": cluster_details,
                "total_clusters": len(clusters)
            }
        except Exception as e:
            logger.error(f"Error in graph_find_clusters: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_get_centrality",
        description="Get centrality score for an entity to measure its importance and influence in the knowledge graph",
        tags={"graph", "centrality", "importance", "influence", "metrics"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True
        }
    )
    async def graph_get_centrality(entity_id: str, ctx: Optional[object] = None) -> dict:
        """Get centrality score for an entity."""
        try:
            # Handle numeric IDs
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            centrality = graph_tool.get_entity_centrality(entity_id)
            entity = graph_tool.get_entity(entity_id)
            
            return {
                "entity_id": entity_id,
                "entity_name": entity.name if entity else "Unknown",
                "centrality": centrality
            }
        except Exception as e:
            logger.error(f"Error in graph_get_centrality: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_delete_entity",
        description="Delete an entity and all its relations from the knowledge graph permanently",
        tags={"graph", "entity", "delete", "remove", "cleanup"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def graph_delete_entity(entity_id: str, ctx: Optional[object] = None) -> dict:
        """Delete an entity and its relations."""
        try:
            # Handle numeric IDs
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            success = graph_tool.delete_entity(entity_id)
            return {"success": success, "entity_id": entity_id}
        except Exception as e:
            logger.error(f"Error in graph_delete_entity: {e}")
            return {"error": str(e)}
    
    @mcp.tool(
        name="graph_delete_relation",
        description="Delete a specific relation between entities from the knowledge graph",
        tags={"graph", "relation", "delete", "remove", "connection"},
        annotations={
            "destructiveHint": True,
            "idempotentHint": True
        }
    )
    async def graph_delete_relation(relation_id: str, ctx: Optional[object] = None) -> dict:
        """Delete a specific relation."""
        try:
            success = graph_tool.delete_relation(relation_id)
            return {"success": success, "relation_id": relation_id}
        except Exception as e:
            logger.error(f"Error in graph_delete_relation: {e}")
            return {"error": str(e)}
    
    # Resources
    @mcp.resource("resource://knowledge_graph/entities")
    def resource_knowledge_graph_entities() -> list:
        """Resource for all entities in the knowledge graph."""
        try:
            entities = graph_tool.search_entities("", limit=100)
            return [
                {
                    "uri": f"resource://knowledge_graph/entity/{entity['id']}",
                    "name": entity['name'],
                    "description": f"{entity['type']}: {entity['name']}",
                    "mimeType": "application/json"
                }
                for entity in entities
            ]
        except Exception as e:
            logger.error(f"Error in resource_knowledge_graph_entities: {e}")
            return []
    
    @mcp.resource("resource://knowledge_graph/entity/{entity_id}")
    def resource_knowledge_graph_entity(entity_id: str) -> dict:
        """Resource for a specific entity."""
        try:
            if entity_id.isdigit():
                entity_id = int(entity_id)
            
            entity = graph_tool.get_entity(entity_id)
            if entity:
                return {
                    "id": entity.id,
                    "type": entity.type,
                    "name": entity.name,
                    "content": entity.content,
                    "tags": entity.tags,
                    "metadata": entity.metadata,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat()
                }
            else:
                return {"error": "Entity not found"}
        except Exception as e:
            logger.error(f"Error in resource_knowledge_graph_entity: {e}")
            return {"error": str(e)}
    
    logger.info("Knowledge Graph MCP tools registered successfully") 