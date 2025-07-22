"""
Codebase Knowledgebase tool for Emily Tools MCP server.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseTool

logger = logging.getLogger(__name__)


class KnowledgeNode(BaseModel):
    id: Optional[int] = None
    codebase_id: str
    node_type: str  # file, function, class, variable, etc.
    name: str
    content: str
    path: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class KnowledgeRelation(BaseModel):
    id: Optional[int] = None
    source_node_id: int
    target_node_id: int
    relation_type: str  # imports, calls, inherits, contains, etc.
    metadata: Dict[str, Any] = {}
    created_at: datetime = datetime.now()


class Codebase(BaseModel):
    id: str
    name: str
    root_path:  str
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    last_indexed: Optional[datetime] = None


class KnowledgebaseTool(BaseTool):
    """Codebase knowledge graph management tool using JSONL."""
    
    @property
    def name(self) -> str:
        return "knowledgebase"
    
    @property
    def description(self) -> str:
        return "Manage knowledge graphs for multiple codebases with semantic relationships"
    
    def get_capabilities(self) -> List[str]:
        return [
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
    
    def _read_entries(self) -> List[Dict[str, Any]]:
        if not self.data_file.exists():
            return []
        entries = []
        with open(self.data_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
        return entries

    def _write_entries(self, entries: List[Dict[str, Any]]):
        with open(self.data_file, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')

    def register_codebase(self, codebase_id: str, name: str, root_path: str, 
                         description: Optional[str] = None) -> Codebase:
        entries = self._read_entries()
        for entry in entries:
            if entry.get('type') == 'codebase' and entry['id'] == codebase_id:
                return Codebase(**entry)
        codebase = Codebase(
            id=codebase_id,
            name=name,
            root_path=root_path,
            description=description,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(json.dumps({**codebase.model_dump(mode='json'), 'type': 'codebase'}) + '\n')
        return codebase

    def add_knowledge_node(self, codebase_id: str, node_type: str, name: str, 
                          content: str, path: Optional[str] = None,
                          metadata: Dict[str, Any] = {}) -> KnowledgeNode:
        entries = self._read_entries()
        new_id = max([e.get('id', 0) for e in entries if e.get('type') == 'node'] + [0]) + 1
        node = KnowledgeNode(
            id=new_id,
            codebase_id=codebase_id,
            node_type=node_type,
            name=name,
            content=content,
            path=path,
            metadata=metadata,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(json.dumps({**node.model_dump(mode='json'), 'type': 'node'}) + '\n')
        return node

    def add_knowledge_relation(self, source_node_id: int, target_node_id: int,
                              relation_type: str, metadata: Dict[str, Any] = {}) -> KnowledgeRelation:
        entries = self._read_entries()
        new_id = max([e.get('id', 0) for e in entries if e.get('type') == 'relation'] + [0]) + 1
        relation = KnowledgeRelation(
            id=new_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            metadata=metadata,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(json.dumps({**relation.model_dump(mode='json'), 'type': 'relation'}) + '\n')
        return relation

    def search_nodes(self, query: str, codebase_id: Optional[str] = None, node_type: Optional[str] = None, limit: int = 50) -> List[KnowledgeNode]:
        entries = self._read_entries()
        nodes = [e for e in entries if e.get('type') == 'node']
        if codebase_id:
            nodes = [n for n in nodes if n['codebase_id'] == codebase_id]
        if node_type:
            nodes = [n for n in nodes if n['node_type'] == node_type]
        results = [n for n in nodes if query.lower() in n['name'].lower() or query.lower() in n['content'].lower()]
        return [KnowledgeNode(**n) for n in results[:limit]]

    def get_node(self, node_id: int) -> Optional[KnowledgeNode]:
        entries = self._read_entries()
        for n in entries:
            if n.get('type') == 'node' and n['id'] == node_id:
                return KnowledgeNode(**n)
        return None

    def get_related_nodes(self, node_id: int, relation_type: Optional[str] = None, direction: str = "both") -> List[Dict[str, Any]]:
        entries = self._read_entries()
        relations = [e for e in entries if e.get('type') == 'relation']
        if relation_type:
            relations = [r for r in relations if r['relation_type'] == relation_type]
        if direction == "out":
            rels = [r for r in relations if r['source_node_id'] == node_id]
        elif direction == "in":
            rels = [r for r in relations if r['target_node_id'] == node_id]
        else:
            rels = [r for r in relations if r['source_node_id'] == node_id or r['target_node_id'] == node_id]
        node_ids = set([r['source_node_id'] for r in rels] + [r['target_node_id'] for r in rels])
        nodes = [n for n in entries if n.get('type') == 'node' and n['id'] in node_ids]
        return nodes

    def list_codebases(self) -> List[Codebase]:
        entries = self._read_entries()
        return [Codebase(**e) for e in entries if e.get('type') == 'codebase']

    def get_codebase_info(self, codebase_id: str) -> Optional[Codebase]:
        entries = self._read_entries()
        for e in entries:
            if e.get('type') == 'codebase' and e['id'] == codebase_id:
                return Codebase(**e)
        return None

    def query_knowledge_graph(self, query: str, codebase_id: Optional[str] = None) -> Dict[str, Any]:
        # Simple search for demonstration
        nodes = self.search_nodes(query, codebase_id)
        return {'nodes': [n.model_dump(mode='json') for n in nodes]} 

    def register(self, mcp):
        @mcp.tool()
        async def codebase_register(codebase_id: str, name: str, root_path: str, 
                                    description: str = None, ctx: object = None) -> dict:
            """Register a new codebase in the knowledgebase."""
            codebase = self.register_codebase(
                codebase_id=codebase_id,
                name=name,
                root_path=root_path,
                description=description
            )
            return {
                "id": codebase.id,
                "name": codebase.name,
                "root_path": codebase.root_path,
                "description": codebase.description,
                "created_at": codebase.created_at.isoformat()
            }

        @mcp.tool()
        async def codebase_add_knowledge(codebase_id: str, node_type: str, name: str, content: str,
                                         path: str = None, metadata: dict = None, ctx: object = None) -> dict:
            """Add a knowledge node to the codebase."""
            if metadata is None:
                metadata = {}
            node = self.add_knowledge_node(
                codebase_id=codebase_id,
                node_type=node_type,
                name=name,
                content=content,
                path=path,
                metadata=metadata
            )
            return {
                "id": node.id,
                "codebase_id": node.codebase_id,
                "node_type": node.node_type,
                "name": node.name,
                "content": node.content,
                "path": node.path,
                "metadata": node.metadata
            }

        @mcp.tool()
        async def codebase_search(query: str, codebase_id: str = None, 
                                 node_type: str = None, limit: int = 50, ctx: object = None) -> list:
            """Search for knowledge nodes."""
            nodes = self.search_nodes(
                query=query,
                codebase_id=codebase_id,
                node_type=node_type,
                limit=limit
            )
            return [
                {
                    "id": node.id,
                    "codebase_id": node.codebase_id,
                    "node_type": node.node_type,
                    "name": node.name,
                    "content": node.content,
                    "path": node.path,
                    "metadata": node.metadata
                }
                for node in nodes
            ]

        @mcp.resource("resource://knowledgebase/all")
        def resource_knowledgebase_all() -> list:
            """Return all knowledgebase nodes as a list of dicts."""
            # Use empty query to get all nodes (limit 100 for safety)
            return [node.model_dump(mode='json') for node in self.search_nodes(query="", limit=100)]

        @mcp.resource("resource://knowledgebase/{node_id}")
        def resource_knowledgebase_by_id(node_id: int) -> dict:
            """Return a single knowledgebase node by ID as a dict."""
            node = self.get_node(node_id)
            return node.model_dump(mode='json') if node else {}
        
        logger.info("Knowledgebase MCP tools registered successfully")