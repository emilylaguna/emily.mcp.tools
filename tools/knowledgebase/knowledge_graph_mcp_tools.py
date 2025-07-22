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
    
    @mcp.tool()
    async def graph_find_related(entity_id: str, depth: int = 2, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_search(query: str, entity_type: str = None, limit: int = 20, ctx: object = None) -> list:
        """Search for entities in the knowledge graph."""
        try:
            results = graph_tool.graph_search(query, entity_type, limit)
            return results
        except Exception as e:
            logger.error(f"Error in graph_search: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def graph_create_entity(payload: dict, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_create_relation(source_id: str, target_id: str, relation_type: str, 
                                  strength: float = 1.0, metadata: dict = None, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_get_entity(entity_id: str, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_get_relations(entity_id: str, relation_types: list = None, ctx: object = None) -> list:
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
    
    @mcp.tool()
    async def graph_shortest_path(source_id: str, target_id: str, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_find_clusters(entity_type: str = None, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_get_centrality(entity_id: str, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_delete_entity(entity_id: str, ctx: object = None) -> dict:
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
    
    @mcp.tool()
    async def graph_delete_relation(relation_id: str, ctx: object = None) -> dict:
        """Delete a specific relation."""
        try:
            success = graph_tool.delete_relation(relation_id)
            return {"success": success, "relation_id": relation_id}
        except Exception as e:
            logger.error(f"Error in graph_delete_relation: {e}")
            return {"error": str(e)}
    
    # Backward compatibility endpoints for memory_graph tool
    @mcp.tool()
    async def memory_create_entities(entities: list, ctx: object = None) -> list:
        """Legacy endpoint for creating multiple entities."""
        try:
            return graph_tool.create_entities(entities)
        except Exception as e:
            logger.error(f"Error in memory_create_entities: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def memory_create_relations(relations: list, ctx: object = None) -> list:
        """Legacy endpoint for creating multiple relations."""
        try:
            return graph_tool.create_relations(relations)
        except Exception as e:
            logger.error(f"Error in memory_create_relations: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def memory_add_observations(observations: list, ctx: object = None) -> list:
        """Legacy endpoint for adding observations."""
        try:
            return graph_tool.add_observations(observations)
        except Exception as e:
            logger.error(f"Error in memory_add_observations: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def memory_delete_entities(entity_names: list, ctx: object = None) -> None:
        """Legacy endpoint for deleting entities by name."""
        try:
            graph_tool.delete_entities(entity_names)
        except Exception as e:
            logger.error(f"Error in memory_delete_entities: {e}")
    
    @mcp.tool()
    async def memory_delete_observations(deletions: list, ctx: object = None) -> None:
        """Legacy endpoint for deleting observations."""
        try:
            graph_tool.delete_observations(deletions)
        except Exception as e:
            logger.error(f"Error in memory_delete_observations: {e}")
    
    @mcp.tool()
    async def memory_delete_relations(relations: list, ctx: object = None) -> None:
        """Legacy endpoint for deleting relations."""
        try:
            graph_tool.delete_relations(relations)
        except Exception as e:
            logger.error(f"Error in memory_delete_relations: {e}")
    
    @mcp.tool()
    async def memory_read_graph(ctx: object = None) -> list:
        """Legacy endpoint for reading the entire graph."""
        try:
            return graph_tool.read_graph()
        except Exception as e:
            logger.error(f"Error in memory_read_graph: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def memory_search_nodes(query: str, ctx: object = None) -> list:
        """Legacy endpoint for searching nodes."""
        try:
            return graph_tool.search_nodes(query)
        except Exception as e:
            logger.error(f"Error in memory_search_nodes: {e}")
            return [{"error": str(e)}]
    
    @mcp.tool()
    async def memory_open_nodes(names: list, ctx: object = None) -> list:
        """Legacy endpoint for opening nodes by name."""
        try:
            return graph_tool.open_nodes(names)
        except Exception as e:
            logger.error(f"Error in memory_open_nodes: {e}")
            return [{"error": str(e)}]
    
    # Backward compatibility endpoints for knowledgebase tool
    @mcp.tool()
    async def codebase_register(codebase_id: str, name: str, root_path: str, 
                               description: str = None, ctx: object = None) -> dict:
        """Legacy endpoint for registering a codebase."""
        try:
            entity = graph_tool.create_entity({
                "type": "project",
                "name": name,
                "content": description or f"Codebase: {name}",
                "metadata": {
                    "codebase_id": codebase_id,
                    "root_path": root_path,
                    "legacy_type": "codebase"
                }
            })
            return {
                "id": entity.id,
                "codebase_id": codebase_id,
                "name": name,
                "root_path": root_path,
                "description": description
            }
        except Exception as e:
            logger.error(f"Error in codebase_register: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    async def codebase_add_knowledge(codebase_id: str, node_type: str, name: str, content: str,
                                   path: str = None, metadata: dict = None, ctx: object = None) -> dict:
        """Legacy endpoint for adding knowledge nodes."""
        try:
            # Find the codebase entity
            codebases = graph_tool.search_entities(codebase_id, {"type": "project"}, 1)
            if not codebases:
                return {"error": "Codebase not found"}
            
            codebase_entity = codebases[0]
            
            # Create the knowledge node
            entity = graph_tool.create_entity({
                "type": node_type,
                "name": name,
                "content": content,
                "metadata": {
                    "codebase_id": codebase_id,
                    "path": path,
                    **(metadata or {})
                }
            })
            
            # Create relation to codebase
            graph_tool.create_relation({
                "source_id": codebase_entity['id'],
                "target_id": entity.id,
                "relation_type": "contains"
            })
            
            return {
                "id": entity.id,
                "codebase_id": codebase_id,
                "node_type": node_type,
                "name": name,
                "content": content,
                "path": path
            }
        except Exception as e:
            logger.error(f"Error in codebase_add_knowledge: {e}")
            return {"error": str(e)}
    
    @mcp.tool()
    async def codebase_search(query: str, codebase_id: str = None, 
                             node_type: str = None, limit: int = 50, ctx: object = None) -> list:
        """Legacy endpoint for searching codebase knowledge."""
        try:
            filters = {}
            if node_type:
                filters["type"] = node_type
            
            results = graph_tool.search_entities(query, filters, limit)
            
            # Filter by codebase if specified
            if codebase_id:
                filtered_results = []
                for result in results:
                    if result.get('metadata', {}).get('codebase_id') == codebase_id:
                        filtered_results.append(result)
                results = filtered_results
            
            return results
        except Exception as e:
            logger.error(f"Error in codebase_search: {e}")
            return [{"error": str(e)}]
    
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