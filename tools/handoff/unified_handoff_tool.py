"""
Unified Handoff Tool Wrapper
Phase 3.1: Handoff Tool Wrapper

Maintains backward compatibility with existing handoff tool API while using
the unified memory backend with enhanced AI features.
"""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from emily_common import BaseTool
from emily_core import UnifiedMemoryStore, MemoryEntity, MemoryContext



logger = logging.getLogger(__name__)


class UnifiedHandoffTool(BaseTool):
    """Enhanced handoff tool using unified memory backend with AI features."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.tool_name = "handoff"
        
    @property
    def name(self) -> str:
        return "handoff"
    
    @property
    def description(self) -> str:
        return "Save and retrieve chat context for handoff between sessions with AI enhancement."
    
    def get_capabilities(self) -> List[str]:
        return [
            "save_context",
            "get_latest_context",
            "list_contexts",
            "get_context",
            "search_contexts",
            "get_related_contexts",
            "get_context_insights",
            "suggest_followup_actions"
        ]
    
    def save_context(self, context: str) -> MemoryContext:
        """Save handoff context with AI enhancement (maintains original API)."""
        # Create MemoryContext for unified storage
        memory_context = MemoryContext(
            type="handoff",
            content=context,
            metadata={'tool': 'handoff'}
        )
        
        # Save with AI enhancement (entity extraction, etc.)
        try:
            saved_memory_context = self.memory.save_context_with_ai(memory_context)
            self.memory.update_context(saved_memory_context)
            
            return saved_memory_context
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, saving basic context: {e}")
            # Fallback to basic save without AI enhancement
            memory_context = MemoryContext(
                type="handoff",
                content=context,
                metadata={'tool': 'handoff'}
            )
            saved_memory_context = self.memory.save_context(memory_context)
            
            self.memory.update_context(saved_memory_context)
            
            return saved_memory_context
    
    def get_contexts(self) -> List[MemoryContext]:
        """Get all handoff contexts (maintains original API)."""
        # Search all handoff contexts using the contexts table
        memory_contexts = self.memory.search_contexts("", filters={"type": "handoff"})
        
        handoff_contexts = []
        for ctx in memory_contexts:
            handoff_contexts.append(ctx)
        
        # Sort by created_at (most recent first)
        return sorted(handoff_contexts, key=lambda x: x.created_at, reverse=True)
    
    def get_contexts_from_today(self) -> List[MemoryContext]:
        """Get all handoff contexts from today ordered by created_at in DESC order."""
        from datetime import date
        
        today = date.today()
        
        # Search all handoff contexts using the contexts table
        memory_contexts = self.memory.search_contexts("", filters={"type": "handoff"})
        
        handoff_contexts = []
        for ctx in memory_contexts:
            # Check if the context was created today
            if ctx.created_at.date() == today:
                handoff_contexts.append(ctx)
        
        # Sort by created_at (most recent first)
        return sorted(handoff_contexts, key=lambda x: x.created_at, reverse=True)
    
    def get_latest_context(self) -> Optional[MemoryContext]:
        """Get the most recent handoff context."""
        contexts = self.get_contexts()
        return contexts[0] if contexts else None
    
    def list_contexts(self, limit: int = 10) -> List[MemoryContext]:
        """List recent handoff contexts (maintains original API)."""
        contexts = self.get_contexts()
        return contexts[:limit]
    
    def get_context(self, context_id: str) -> Optional[MemoryContext]:
        """Get specific context by ID (maintains original API)."""
        
        # Get from unified memory using contexts table
        context_results = self.memory.search_contexts("", filters={
            "type": "handoff",
            "id": context_id
        })
        
        if not context_results:
            return None
        
        return context_results[0]
    
    def search_contexts(self, query: str, limit: int = 10) -> List[MemoryContext]:
        """Semantic search across handoff contexts."""
        # Use unified memory context search
        results = self.memory.search_contexts(query, filters={"type": "handoff"})
        
        contexts_with_scores = []
        for result in results:
            contexts_with_scores.append(result)
        
        return contexts_with_scores[:limit]
    
    def get_related_contexts(self, context_id: str) -> List[MemoryContext]:
        """Find contexts related to the given context through entities and topics."""
        
        # Get the context to understand its content and entities
        base_context = self.memory.search_contexts("", filters={"type": "handoff", "id": context_id})
        if not base_context:
            return []
        
        base_ctx = base_context[0].model_dump()
        
        # Find related contexts through:
        # 1. Shared entities
        related_by_entities = self._find_contexts_by_shared_entities(context_id)
        
        # 2. Similar topics/content
        related_by_content = self.memory.search_contexts(
            base_ctx['content'][:200],  # Use first 200 chars for similarity
            filters={"type": "handoff"}
        )
        # Convert to dict format for consistency
        related_by_content = [ctx.model_dump() for ctx in related_by_content[:5]]
        
        # 3. Temporal proximity (recent contexts)
        related_by_time = self._find_recent_contexts(base_ctx['created_at'])
        
        # Combine and deduplicate
        all_related = {}
        for ctx_list in [related_by_entities, related_by_content, related_by_time]:
            for ctx in ctx_list:
                if ctx['id'] != context_id:  # Exclude self
                    all_related[ctx['id']] = ctx
        
        related_contexts = []
        for ctx in list(all_related.values())[:10]:
            related_contexts.append(ctx)
        
        return related_contexts
    
    def _find_contexts_by_shared_entities(self, context_uuid: str) -> List[Dict]:
        """Find contexts that share entities with the given context."""
        # Get entities related to this context
        related_entities = self.memory.get_related(context_uuid, ["mentions", "relates_to"])
        
        if not related_entities:
            return []
        
        # Find other contexts that mention these entities
        related_contexts = []
        for entity in related_entities:
            # Find contexts that relate to this entity
            entity_contexts = self.memory.get_related(entity['id'], ["mentioned_by", "relates_to"])
            for ctx in entity_contexts:
                if ctx.get('type') == 'handoff':
                    related_contexts.append(ctx)
        
        return related_contexts
    
    def _find_recent_contexts(self, base_date: datetime, days: int = 7) -> List[Dict]:
        """Find contexts from around the same time period."""
        # This is a simplified implementation - would need proper date filtering
        recent_contexts = self.memory.search_contexts("", filters={"type": "handoff"})
        
        # Filter by date proximity
        filtered = []
        for ctx in recent_contexts:
            ctx_date = ctx.created_at
            if ctx_date and abs((ctx_date - base_date).days) <= days:
                filtered.append(ctx.model_dump())
        
        return filtered[:20]
    
    def get_context_insights(self, context_id: str) -> Dict[str, Any]:
        """Get AI-generated insights about a context."""
        
        # Get context and related data
        context_data = self.memory.search_contexts("", filters={"type": "handoff", "id": context_id})
        if not context_data:
            return {}
        
        ctx = context_data[0].model_dump()
        
        # Get related entities
        related_entities = self.memory.get_related(context_id)
        
        # Generate insights
        insights = {
            "summary": self.memory.generate_summary(ctx['content']),
            "key_topics": self.memory.extract_topics_from_text(ctx['content']),
            "action_items": self.memory.extract_action_items(ctx['content']),
            "mentioned_people": [e for e in related_entities if e.get('type') == 'person'],
            "technologies": [e for e in related_entities if e.get('type') == 'technology'],
            "related_files": [e for e in related_entities if e.get('type') == 'file'],
            "context_length": len(ctx['content']),
            "entity_count": len(related_entities),
            "creation_date": ctx['created_at']
        }
        
        return insights
    
    def suggest_followup_actions(self, context_id: str) -> List[str]:
        """Suggest follow-up actions based on context content."""
        
        context_data = self.memory.search_contexts("", filters={"type": "handoff", "id": context_id})
        if not context_data:
            return []
        
        ctx = context_data[0].model_dump()
        
        suggestions = []
        
        # Extract action items from content
        action_items = self.memory.extract_action_items(ctx['content'])
        for action in action_items[:3]:  # Top 3 actions
            suggestions.append(f"Create task: {action}")
        
        # Suggest based on mentioned entities
        related_entities = self.memory.get_related(context_id)
        
        # Suggest contacting people
        people = [e for e in related_entities if e.get('type') == 'person']
        if people:
            suggestions.append(f"Follow up with {people[0]['name']}")
        
        # Suggest code review if files mentioned
        files = [e for e in related_entities if e.get('type') == 'file']
        if files:
            suggestions.append(f"Review code in {files[0]['name']}")
        
        # Suggest documentation if technical topics found
        topics = self.memory.extract_topics_from_text(ctx['content'])
        tech_topics = [t for t in topics if t in ['api', 'database', 'authentication', 'deployment']]
        if tech_topics:
            suggestions.append(f"Document {tech_topics[0]} implementation")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def register(self, mcp):
        """Register MCP tools with enhanced capabilities."""
        
        @mcp.tool()
        async def handoff_save(context: str) -> MemoryContext:
            """Save chat context for handoff between sessions with AI enhancement."""
            return self.save_context(context)
        
        @mcp.tool()
        async def handoff_get() -> Optional[MemoryContext]:
            return self.get_latest_context()
            """Get all handoff contexts from today ordered by created_at in DESC order."""
            contexts = self.get_contexts_from_today()
            return [
                {
                    "id": c.id,
                    "context": c.context,
                    "created_at": c.created_at.isoformat(),
                    "summary": c.summary,
                    "topics": c.topics
                }
                for c in contexts
            ]
        
        @mcp.tool()
        async def handoff_list(limit: int = 10) -> list[MemoryContext]:
            """List recent saved chat contexts."""
            contexts = self.list_contexts(limit=limit)
            return contexts
        
        @mcp.tool()
        async def handoff_search(query: str, limit: int = 10) -> list[MemoryContext]:
            """Search handoff contexts by content using AI semantic search."""
            results = self.search_contexts(query, limit)
            return results
        
        @mcp.tool()
        async def handoff_related(context_id: str) -> list[MemoryContext]:
            """Get contexts related to the specified context through entities and topics."""
            results = self.get_related_contexts(context_id)
            return results
        
        @mcp.tool()
        async def handoff_insights(context_id: str) -> dict:
            """Get AI-generated insights about a handoff context."""
            return self.get_context_insights(context_id)
        
        @mcp.tool()
        async def handoff_suggest_actions(context_id: str) -> list:
            """Get suggested follow-up actions for a context."""
            return self.suggest_followup_actions(context_id)
        
        # @mcp.resource("resource://handoff/recent")
        def handoff_recent() -> str:
            """Returns the last 10 recent handoff contexts as JSON."""
            latest = self.get_latest_context()
            return json.dumps(latest.model_dump(mode='json') if latest else {}, indent=2)
        
        # @mcp.resource("resource://handoff/{context_id}")
        def handoff_by_id(context_id: str) -> dict:
            """Return a single handoff context by ID as a dict."""
            ctx = self.get_context(context_id)
            return ctx.model_dump(mode='json') if ctx else {}
        
        logger.info("Handoff MCP tools registered successfully")