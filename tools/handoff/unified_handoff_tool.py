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

from ...common.base_tool import BaseTool
try:
    from ...core import UnifiedMemoryStore
    from ...core.models import MemoryContext
except ImportError:
    from core import UnifiedMemoryStore
    from core.models import MemoryContext

logger = logging.getLogger(__name__)


class HandoffContext(BaseModel):
    """Backward compatible handoff context model."""
    id: Optional[int] = None
    context: str
    created_at: datetime = datetime.now()
    
    # Optional enhancement fields (not breaking changes)
    summary: Optional[str] = None
    topics: List[str] = []
    related_entities: List[str] = []


class UnifiedHandoffTool(BaseTool):
    """Enhanced handoff tool using unified memory backend with AI features."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.tool_name = "handoff"
        
        # Cache for numeric ID to UUID mapping
        self._id_cache: Dict[int, str] = {}
        self._reverse_cache: Dict[str, int] = {}
    
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
    
    def _extract_numeric_id(self, uuid_id: str) -> int:
        """Convert UUID to numeric ID for backward compatibility."""
        # Use hash to create consistent numeric ID
        return int(hashlib.md5(uuid_id.encode()).hexdigest()[:8], 16)
    
    def _get_uuid_from_numeric_id(self, numeric_id: int) -> Optional[str]:
        """Find UUID from numeric ID mapping."""
        # Check cache first
        if numeric_id in self._id_cache:
            return self._id_cache[numeric_id]
        
        # Search contexts with matching numeric ID in metadata
        contexts = self.memory.search_contexts("", filters={
            "type": "handoff", 
            "metadata.numeric_id": str(numeric_id)
        })
        
        if contexts:
            uuid_id = contexts[0].id
            # Cache the mapping
            self._id_cache[numeric_id] = uuid_id
            self._reverse_cache[uuid_id] = numeric_id
            return uuid_id
        
        return None
    
    def _memory_context_to_handoff_context(self, memory_context: Dict[str, Any]) -> HandoffContext:
        """Convert MemoryContext to HandoffContext for API compatibility."""
        numeric_id = self._extract_numeric_id(memory_context['id'])
        
        # Cache the mapping
        self._id_cache[numeric_id] = memory_context['id']
        self._reverse_cache[memory_context['id']] = numeric_id
        
        return HandoffContext(
            id=numeric_id,
            context=memory_context['content'],
            created_at=memory_context['created_at'],
            summary=memory_context.get('summary'),
            topics=memory_context.get('topics', []),
            related_entities=memory_context.get('entity_ids', [])
        )
    
    def save_context(self, context: str) -> HandoffContext:
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
            
            # Add numeric ID to metadata for quick lookup
            numeric_id = self._extract_numeric_id(saved_memory_context.id)
            saved_memory_context.metadata['numeric_id'] = str(numeric_id)
            
            # Update the context with the numeric ID
            self.memory.update_context(saved_memory_context)
            
            # Convert back to HandoffContext for API compatibility
            handoff_context = HandoffContext(
                id=numeric_id,
                context=saved_memory_context.content,
                created_at=saved_memory_context.created_at,
                summary=saved_memory_context.summary,
                topics=saved_memory_context.topics,
                related_entities=saved_memory_context.entity_ids
            )
            
            # Cache the mapping
            self._id_cache[numeric_id] = saved_memory_context.id
            self._reverse_cache[saved_memory_context.id] = numeric_id
            
            return handoff_context
            
        except Exception as e:
            logger.warning(f"AI enhancement failed, saving basic context: {e}")
            # Fallback to basic save without AI enhancement
            memory_context = MemoryContext(
                type="handoff",
                content=context,
                metadata={'tool': 'handoff'}
            )
            saved_memory_context = self.memory.save_context(memory_context)
            
            numeric_id = self._extract_numeric_id(saved_memory_context.id)
            saved_memory_context.metadata['numeric_id'] = str(numeric_id)
            self.memory.update_context(saved_memory_context)
            
            return HandoffContext(
                id=numeric_id,
                context=saved_memory_context.content,
                created_at=saved_memory_context.created_at
            )
    
    def get_contexts(self) -> List[HandoffContext]:
        """Get all handoff contexts (maintains original API)."""
        # Search all handoff contexts using the contexts table
        memory_contexts = self.memory.search_contexts("", filters={"type": "handoff"})
        
        # Convert to HandoffContext objects
        handoff_contexts = []
        for ctx in memory_contexts:
            handoff_context = self._memory_context_to_handoff_context(ctx.model_dump())
            handoff_contexts.append(handoff_context)
        
        # Sort by created_at (most recent first)
        return sorted(handoff_contexts, key=lambda x: x.created_at, reverse=True)
    
    def get_contexts_from_today(self) -> List[HandoffContext]:
        """Get all handoff contexts from today ordered by created_at in DESC order."""
        from datetime import date
        
        today = date.today()
        
        # Search all handoff contexts using the contexts table
        memory_contexts = self.memory.search_contexts("", filters={"type": "handoff"})
        
        # Convert to HandoffContext objects and filter by today
        handoff_contexts = []
        for ctx in memory_contexts:
            handoff_context = self._memory_context_to_handoff_context(ctx.model_dump())
            # Check if the context was created today
            if handoff_context.created_at.date() == today:
                handoff_contexts.append(handoff_context)
        
        # Sort by created_at (most recent first)
        return sorted(handoff_contexts, key=lambda x: x.created_at, reverse=True)
    
    def get_latest_context(self) -> Optional[HandoffContext]:
        """Get the most recent handoff context."""
        contexts = self.get_contexts()
        return contexts[0] if contexts else None
    
    def list_contexts(self, limit: int = 10) -> List[HandoffContext]:
        """List recent handoff contexts (maintains original API)."""
        contexts = self.get_contexts()
        return contexts[:limit]
    
    def get_context(self, context_id: int) -> Optional[HandoffContext]:
        """Get specific context by ID (maintains original API)."""
        # Find UUID from numeric ID
        uuid_id = self._get_uuid_from_numeric_id(context_id)
        
        if not uuid_id:
            return None
        
        # Get from unified memory using contexts table
        context_results = self.memory.search_contexts("", filters={
            "type": "handoff",
            "id": uuid_id
        })
        
        if not context_results:
            return None
        
        return self._memory_context_to_handoff_context(context_results[0].model_dump())
    
    def search_contexts(self, query: str, limit: int = 10) -> List[HandoffContext]:
        """Semantic search across handoff contexts."""
        # Use unified memory context search
        results = self.memory.search_contexts(query, filters={"type": "handoff"})
        
        # Convert to HandoffContext objects with relevance scores
        contexts_with_scores = []
        for result in results:
            handoff_context = self._memory_context_to_handoff_context(result.model_dump())
            
            # Add relevance score as metadata (not in original model)
            if hasattr(handoff_context, '__dict__'):
                handoff_context.__dict__['relevance_score'] = getattr(result, 'relevance', 0.0)
            
            contexts_with_scores.append(handoff_context)
        
        return contexts_with_scores[:limit]
    
    def get_related_contexts(self, context_id: int) -> List[HandoffContext]:
        """Find contexts related to the given context through entities and topics."""
        uuid_id = self._get_uuid_from_numeric_id(context_id)
        if not uuid_id:
            return []
        
        # Get the context to understand its content and entities
        base_context = self.memory.search_contexts("", filters={"type": "handoff", "id": uuid_id})
        if not base_context:
            return []
        
        base_ctx = base_context[0].model_dump()
        
        # Find related contexts through:
        # 1. Shared entities
        related_by_entities = self._find_contexts_by_shared_entities(uuid_id)
        
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
                if ctx['id'] != uuid_id:  # Exclude self
                    all_related[ctx['id']] = ctx
        
        # Convert to HandoffContext and limit results
        related_contexts = []
        for ctx in list(all_related.values())[:10]:
            handoff_context = self._memory_context_to_handoff_context(ctx)
            related_contexts.append(handoff_context)
        
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
    
    def get_context_insights(self, context_id: int) -> Dict[str, Any]:
        """Get AI-generated insights about a context."""
        uuid_id = self._get_uuid_from_numeric_id(context_id)
        if not uuid_id:
            return {}
        
        # Get context and related data
        context_data = self.memory.search_contexts("", filters={"type": "handoff", "id": uuid_id})
        if not context_data:
            return {}
        
        ctx = context_data[0].model_dump()
        
        # Get related entities
        related_entities = self.memory.get_related(uuid_id)
        
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
    
    def suggest_followup_actions(self, context_id: int) -> List[str]:
        """Suggest follow-up actions based on context content."""
        uuid_id = self._get_uuid_from_numeric_id(context_id)
        if not uuid_id:
            return []
        
        context_data = self.memory.search_contexts("", filters={"type": "handoff", "id": uuid_id})
        if not context_data:
            return []
        
        ctx = context_data[0].model_dump()
        
        suggestions = []
        
        # Extract action items from content
        action_items = self.memory.extract_action_items(ctx['content'])
        for action in action_items[:3]:  # Top 3 actions
            suggestions.append(f"Create task: {action}")
        
        # Suggest based on mentioned entities
        related_entities = self.memory.get_related(uuid_id)
        
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
        async def handoff_save(context: str) -> dict:
            """Save chat context for handoff between sessions with AI enhancement."""
            saved = self.save_context(context)
            return {
                "id": saved.id,
                "context": saved.context,
                "created_at": saved.created_at.isoformat(),
                "summary": saved.summary,
                "topics": saved.topics
            }
        
        @mcp.tool()
        async def handoff_get() -> list:
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
        async def handoff_list(limit: int = 10) -> list:
            """List recent saved chat contexts."""
            contexts = self.list_contexts(limit=limit)
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
        async def handoff_search(query: str, limit: int = 10) -> list:
            """Search handoff contexts by content using AI semantic search."""
            results = self.search_contexts(query, limit)
            return [
                {
                    "id": ctx.id,
                    "context": ctx.context[:200] + "..." if len(ctx.context) > 200 else ctx.context,
                    "created_at": ctx.created_at.isoformat(),
                    "relevance_score": getattr(ctx, 'relevance_score', 0.0),
                    "summary": ctx.summary,
                    "topics": ctx.topics
                }
                for ctx in results
            ]
        
        @mcp.tool()
        async def handoff_related(context_id: int) -> list:
            """Get contexts related to the specified context through entities and topics."""
            results = self.get_related_contexts(context_id)
            return [
                {
                    "id": ctx.id,
                    "context": ctx.context[:150] + "..." if len(ctx.context) > 150 else ctx.context,
                    "created_at": ctx.created_at.isoformat(),
                    "summary": ctx.summary,
                    "topics": ctx.topics
                }
                for ctx in results
            ]
        
        @mcp.tool()
        async def handoff_insights(context_id: int) -> dict:
            """Get AI-generated insights about a handoff context."""
            return self.get_context_insights(context_id)
        
        @mcp.tool()
        async def handoff_suggest_actions(context_id: int) -> list:
            """Get suggested follow-up actions for a context."""
            return self.suggest_followup_actions(context_id)
        
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
        
        logger.info("Handoff MCP tools registered successfully")