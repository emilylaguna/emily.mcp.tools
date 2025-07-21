import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from ..base import BaseTool

class MemoryGraphTool(BaseTool):
    """Memory graph tool using JSONL for persistent storage of entities, relations, and observations."""

    @property
    def name(self) -> str:
        return "memory_graph"

    @property
    def description(self) -> str:
        return "Persistent memory graph for entities, relations, and observations."

    def get_capabilities(self) -> list:
        return [
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

    def _read_graph(self) -> List[Dict[str, Any]]:
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

    def _write_graph(self, entries: List[Dict[str, Any]]):
        with open(self.data_file, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + '\n')

    def create_entities(self, entities: List[Dict[str, Any]]):
        graph = self._read_graph()
        existing_names = {e['name'] for e in graph if e.get('type') == 'entity'}
        new_entities = [e for e in entities if e['name'] not in existing_names]
        for entity in new_entities:
            entity['type'] = 'entity'
        with open(self.data_file, 'a') as f:
            for entity in new_entities:
                f.write(json.dumps(entity) + '\n')
        return new_entities

    def create_relations(self, relations: List[Dict[str, Any]]):
        graph = self._read_graph()
        existing = {(r['from'], r['to'], r['relationType']) for r in graph if r.get('type') == 'relation'}
        new_relations = [r for r in relations if (r['from'], r['to'], r['relationType']) not in existing]
        for rel in new_relations:
            rel['type'] = 'relation'
        with open(self.data_file, 'a') as f:
            for rel in new_relations:
                f.write(json.dumps(rel) + '\n')
        return new_relations

    def add_observations(self, observations: List[Dict[str, Any]]):
        graph = self._read_graph()
        updated = []
        for obs in observations:
            for entry in graph:
                if entry.get('type') == 'entity' and entry['name'] == obs['entityName']:
                    entry.setdefault('observations', [])
                    for o in obs['contents']:
                        if o not in entry['observations']:
                            entry['observations'].append(o)
                    updated.append(entry)
        self._write_graph(graph)
        return updated

    def delete_entities(self, entity_names: List[str]):
        graph = self._read_graph()
        new_graph = [e for e in graph if not (e.get('type') == 'entity' and e['name'] in entity_names)]
        new_graph = [e for e in new_graph if not (e.get('type') == 'relation' and (e['from'] in entity_names or e['to'] in entity_names))]
        self._write_graph(new_graph)

    def delete_observations(self, deletions: List[Dict[str, Any]]):
        graph = self._read_graph()
        for deletion in deletions:
            for entry in graph:
                if entry.get('type') == 'entity' and entry['name'] == deletion['entityName']:
                    entry['observations'] = [o for o in entry.get('observations', []) if o not in deletion['observations']]
        self._write_graph(graph)

    def delete_relations(self, relations: List[Dict[str, Any]]):
        graph = self._read_graph()
        to_delete = {(r['from'], r['to'], r['relationType']) for r in relations}
        new_graph = [e for e in graph if not (e.get('type') == 'relation' and (e['from'], e['to'], e['relationType']) in to_delete)]
        self._write_graph(new_graph)

    def read_graph(self) -> List[Dict[str, Any]]:
        return self._read_graph()

    def search_nodes(self, query: str) -> List[Dict[str, Any]]:
        graph = self._read_graph()
        results = []
        for entry in graph:
            if entry.get('type') == 'entity':
                if query.lower() in entry['name'].lower() or \
                   query.lower() in entry.get('entityType', '').lower() or \
                   any(query.lower() in o.lower() for o in entry.get('observations', [])):
                    results.append(entry)
        return results

    def open_nodes(self, names: List[str]) -> List[Dict[str, Any]]:
        graph = self._read_graph()
        nodes = [e for e in graph if e.get('type') == 'entity' and e['name'] in names]
        relations = [e for e in graph if e.get('type') == 'relation' and (e['from'] in names or e['to'] in names)]
        return nodes + relations

    def register(self, mcp):
        @mcp.tool()
        async def memory_create_entities(entities: list, ctx: object = None) -> list:
            """Create entities in the memory graph."""
            return self.create_entities(entities)

        @mcp.tool()
        async def memory_create_relations(relations: list, ctx: object = None) -> list:
            """Create relations in the memory graph."""
            return self.create_relations(relations)

        @mcp.tool()
        async def memory_add_observations(observations: list, ctx: object = None) -> list:
            """Add observations to entities in the memory graph."""
            return self.add_observations(observations)

        @mcp.tool()
        async def memory_delete_entities(entity_names: list, ctx: object = None) -> None:
            """Delete entities from the memory graph."""
            self.delete_entities(entity_names)

        @mcp.tool()
        async def memory_delete_observations(deletions: list, ctx: object = None) -> None:
            """Delete observations from entities in the memory graph."""
            self.delete_observations(deletions)

        @mcp.tool()
        async def memory_delete_relations(relations: list, ctx: object = None) -> None:
            """Delete relations from the memory graph."""
            self.delete_relations(relations)

        @mcp.tool()
        async def memory_read_graph(ctx: object = None) -> list:
            """Read the entire memory graph."""
            return self.read_graph()

        @mcp.tool()
        async def memory_search_nodes(query: str, ctx: object = None) -> list:
            """Search for nodes in the memory graph."""
            return self.search_nodes(query)

        @mcp.tool()
        async def memory_open_nodes(names: list, ctx: object = None) -> list:
            """Open specific nodes in the memory graph."""
            return self.open_nodes(names)