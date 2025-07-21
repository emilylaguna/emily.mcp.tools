"""
Handoff tool for Emily Tools MCP server.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..base import BaseTool
import json

class HandoffContext(BaseModel):
    id: Optional[int] = None
    context: str
    created_at: datetime = datetime.now()

class HandoffTool(BaseTool):
    """Tool for saving and retrieving chat context for handoff between sessions."""

    @property
    def name(self) -> str:
        return "handoff"

    @property
    def description(self) -> str:
        return "Save and retrieve chat context for handoff between sessions, with timestamp for freshness."

    def get_capabilities(self) -> List[str]:
        return [
            "save_context",
            "get_latest_context",
            "list_contexts"
        ]

    def _read_contexts(self) -> List[HandoffContext]:
        if not self.data_file.exists():
            return []
        contexts = []
        with open(self.data_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        contexts.append(HandoffContext(**json.loads(line)))
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
        return contexts

    def _write_contexts(self, contexts: List[HandoffContext]):
        with open(self.data_file, 'w') as f:
            for ctx in contexts:
                f.write(ctx.json() + '\n')

    def save_context(self, context: str) -> HandoffContext:
        contexts = self._read_contexts()
        new_id = max([c.id for c in contexts if c.id is not None] + [0]) + 1
        ctx = HandoffContext(
            id=new_id,
            context=context,
            created_at=datetime.now(),
        )
        with open(self.data_file, 'a') as f:
            f.write(ctx.json() + '\n')
        return ctx

    def get_latest_context(self) -> Optional[HandoffContext]:
        contexts = self._read_contexts()
        if not contexts:
            return None
        return max(contexts, key=lambda c: c.created_at)

    def list_contexts(self, limit: int = 10) -> List[HandoffContext]:
        contexts = self._read_contexts()
        return sorted(contexts, key=lambda c: c.created_at, reverse=True)[:limit]

    def get_context(self, context_id: int) -> Optional[HandoffContext]:
        contexts = self._read_contexts()
        for ctx in contexts:
            if ctx.id == context_id:
                return ctx
        return None

    def register(self, mcp):
        @mcp.tool()
        async def handoff_save(context: str) -> dict:
            """Save chat context for handoff between sessions."""
            saved = self.save_context(context)
            return {
                "id": saved.id,
                "context": saved.context,
                "created_at": saved.created_at.isoformat(),
            }

        @mcp.tool()
        async def handoff_get() -> dict:
            """Get the latest saved chat context."""
            latest = self.get_latest_context()
            if latest:
                return {
                    "id": latest.id,
                    "context": latest.context,
                    "created_at": latest.created_at.isoformat(),
                }
            return {}

        @mcp.tool()
        async def handoff_list(limit: int = 10) -> list:
            """List recent saved chat contexts."""
            contexts = self.list_contexts(limit=limit)
            return [
                {
                    "id": c.id,
                    "context": c.context,
                    "created_at": c.created_at.isoformat(),
                }
                for c in contexts
            ]

        @mcp.resource("resource://handoff/recent")
        def handoff_recent() -> str:
            """Returns the last 10 recent handoff contexts as JSON."""
            latest = self.get_latest_context()
            return json.dumps(latest.model_dump(mode='json') if latest else {}, indent=2)

        @mcp.resource("resource://handoff/{context_id}")
        def handoff_by_id(context_id: int) -> dict:
            """Return a single handoff context by ID as a dict."""
            ctx = self.get_context(context_id)
            return ctx.model_dump(mode='json') if ctx else {}
