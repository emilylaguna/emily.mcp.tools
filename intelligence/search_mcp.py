"""
MCP Integration for Intelligent Search & Cross-Domain Intelligence

This module provides MCP tool endpoints for the advanced search and
intelligence features.
"""

import logging
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime, timedelta
import re
from enum import Enum

try:
    from ..core import UnifiedMemoryStore
except ImportError:
    from core import UnifiedMemoryStore

from .search import IntelligentSearchEngine
from .smart_suggestions import SmartSuggestionsEngine
from .natural_query import NaturalQueryProcessor
from tools.common_types import SearchMode, AnalysisType

logger = logging.getLogger(__name__)


# Use common types where possible
SearchType = SearchMode
InsightType = AnalysisType


class SuggestionCategory(str, Enum):
    """Suggestion categories."""
    WORKFLOW = "workflow"
    TASK = "task"
    PROJECT = "project"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"


class IntelligentSearchMCPTools:
    """MCP tools for intelligent search and cross-domain intelligence."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory_store = memory_store
        self.search_engine = IntelligentSearchEngine(memory_store)
        self.suggestions_engine = SmartSuggestionsEngine(memory_store)
        self.query_processor = NaturalQueryProcessor(memory_store)
    
    def register_tools(self, mcp):
        """Register all intelligent search tools with MCP."""
        
        @mcp.tool(
            name="intelligent_search",
            description="Advanced semantic search with cross-domain intelligence for finding related information across all data types",
            tags={"search", "intelligence", "semantic", "cross-domain", "ai"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def intelligent_search(query: str, context: dict = None) -> dict:
            """Advanced semantic search with cross-domain intelligence."""
            try:
                return self.search_engine.universal_search(query, context_filters=context)
            except Exception as e:
                logger.error(f"Intelligent search failed: {e}")
                return {"error": str(e), "results": {}}
        
        @mcp.tool(
            name="natural_query",
            description="Process natural language queries with intelligent interpretation and context understanding",
            tags={"search", "natural-language", "ai", "query", "interpretation"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def natural_query(query: str) -> dict:
            """Process natural language queries with intelligent interpretation."""
            try:
                return self.query_processor.process_query(query)
            except Exception as e:
                logger.error(f"Natural query processing failed: {e}")
                return {"error": str(e), "results": {}}
        
        @mcp.tool(
            name="get_project_intelligence",
            description="Get comprehensive project intelligence including related tasks, people, technologies, and insights",
            tags={"intelligence", "project", "analytics", "insights", "comprehensive"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def get_project_intelligence(project_id: str) -> dict:
            """Get comprehensive project intelligence across all domains."""
            try:
                return self.search_engine.get_project_intelligence(project_id)
            except Exception as e:
                logger.error(f"Project intelligence failed: {e}")
                return {"error": str(e), "intelligence": {}}
        
        # @mcp.tool()
        # async def find_expertise(technology: str) -> list:
        #     """Find people with expertise in specific technology."""
        #     try:
        #         return self.search_engine.find_expert_for_technology(technology)
        #     except Exception as e:
        #         logger.error(f"Expertise search failed: {e}")
        #         return []
        
        @mcp.tool(
            name="get_smart_suggestions",
            description="Get contextual suggestions based on current entity and activity patterns using AI analysis",
            tags={"suggestions", "contextual", "ai", "smart", "recommendations"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def get_smart_suggestions(context: dict) -> dict:
            """Get contextual suggestions based on current entity."""
            try:
                return self.suggestions_engine.get_contextual_suggestions(context)
            except Exception as e:
                logger.error(f"Smart suggestions failed: {e}")
                return {"error": str(e), "suggestions": {}}
        
        @mcp.tool(
            name="intent_based_search",
            description="Understand search intent from natural language and provide contextual results with AI interpretation",
            tags={"search", "intent", "natural-language", "ai", "contextual"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def intent_based_search(natural_query: str) -> dict:
            """Understand search intent and provide contextual results."""
            try:
                return self.search_engine.intent_based_search(natural_query)
            except Exception as e:
                logger.error(f"Intent-based search failed: {e}")
                return {"error": str(e), "results": {}}
        
        @mcp.tool(
            name="get_workflow_suggestions",
            description="Get intelligent workflow suggestions based on user's current activity and historical patterns",
            tags={"workflow", "suggestions", "automation", "ai", "productivity"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def get_workflow_suggestions(user_context: dict = None) -> dict:
            """Get workflow suggestions based on user's current activity."""
            try:
                return self.suggestions_engine.get_workflow_suggestions(user_context or {})
            except Exception as e:
                logger.error(f"Workflow suggestions failed: {e}")
                return {"error": str(e), "suggestions": {}}
        
        @mcp.tool(
            name="complex_query",
            description="Process complex queries with multiple clauses and relationships using advanced AI parsing",
            tags={"search", "complex", "ai", "parsing", "relationships"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def complex_query(query: str) -> dict:
            """Process complex queries with multiple clauses and relationships."""
            try:
                return self.query_processor.process_complex_query(query)
            except Exception as e:
                logger.error(f"Complex query processing failed: {e}")
                return {"error": str(e), "results": {}}
        
        @mcp.tool(
            name="get_expertise_map",
            description="Create expertise map from conversation and code patterns to identify knowledge distribution",
            tags={"expertise", "mapping", "knowledge", "analysis", "ai"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": False
            }
        )
        async def get_expertise_map() -> dict:
            """Create expertise map from conversation and code patterns."""
            try:
                return self._create_expertise_map()
            except Exception as e:
                logger.error(f"Expertise map creation failed: {e}")
                return {"error": str(e), "expertise_map": {}}
        
        @mcp.tool(
            name="get_cross_domain_insights",
            description="Get cross-domain insights for a specific entity by analyzing relationships across different data types",
            tags={"insights", "cross-domain", "analysis", "relationships", "ai"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def get_cross_domain_insights(entity_id: str) -> dict:
            """Get cross-domain insights for a specific entity."""
            try:
                return self._get_cross_domain_insights(entity_id)
            except Exception as e:
                logger.error(f"Cross-domain insights failed: {e}")
                return {"error": str(e), "insights": {}}
        
        @mcp.tool(
            name="search_with_context",
            description="Search with additional context about the current entity for more accurate and relevant results",
            tags={"search", "contextual", "entity", "enhanced", "relevance"},
            annotations={
                "readOnlyHint": True,
                "idempotentHint": True
            }
        )
        async def search_with_context(query: str, entity_context: str = None) -> dict:
            """Search with additional context about the current entity."""
            try:
                return self._search_with_context(query, entity_context)
            except Exception as e:
                logger.error(f"Contextual search failed: {e}")
                return {"error": str(e), "results": {}}
    
    def _create_expertise_map(self) -> Dict[str, Any]:
        """Create expertise map from conversation and code patterns."""
        
        try:
            # Get all people
            people = self.memory_store.search("", filters={"type": "person"})
            
            expertise_map = {}
            
            for person in people:
                person_id = person['id']
                person_name = person['name']
                
                # Get conversations they're mentioned in
                conversations = self.memory_store.get_related(person_id, ["mentions", "involves"])
                conversation_content = " ".join([c.get('content', '') for c in conversations])
                
                # Get files/code they're associated with
                code_entities = self.memory_store.get_related(person_id, ["authored", "modified", "reviewed"])
                
                # Extract technologies from conversations
                tech_mentions = self._extract_technologies_from_text(conversation_content)
                
                # Get projects they're involved in
                projects = [e for e in self.memory_store.get_related(person_id) if e.get('type') == 'project']
                
                # Calculate expertise scores
                expertise_scores = {}
                for tech, confidence in tech_mentions:
                    expertise_scores[tech] = expertise_scores.get(tech, 0) + confidence
                
                # Add file-based expertise
                for code_entity in code_entities:
                    language = code_entity.get('metadata', {}).get('language')
                    if language:
                        expertise_scores[language] = expertise_scores.get(language, 0) + 0.8
                
                expertise_map[person_id] = {
                    'name': person_name,
                    'expertise': dict(sorted(expertise_scores.items(), 
                                           key=lambda x: x[1], reverse=True)[:10]),
                    'projects': [p['name'] for p in projects],
                    'conversation_count': len(conversations),
                    'code_contributions': len(code_entities),
                    'activity_score': self._calculate_activity_score(conversations, code_entities)
                }
            
            return expertise_map
            
        except Exception as e:
            logger.warning(f"Failed to create expertise map: {e}")
            return {}
    
    def _extract_technologies_from_text(self, text: str) -> List[tuple]:
        """Extract technologies from text with confidence scores."""
        
        tech_keywords = [
            ('Python', 0.9), ('JavaScript', 0.9), ('TypeScript', 0.9),
            ('React', 0.8), ('Vue', 0.8), ('Angular', 0.8),
            ('Node.js', 0.8), ('Django', 0.8), ('Flask', 0.8),
            ('FastAPI', 0.8), ('PostgreSQL', 0.7), ('MongoDB', 0.7),
            ('Redis', 0.7), ('Docker', 0.7), ('Kubernetes', 0.7),
            ('AWS', 0.6), ('Azure', 0.6), ('GCP', 0.6)
        ]
        
        found_tech = []
        text_lower = text.lower()
        
        for tech, base_confidence in tech_keywords:
            if tech.lower() in text_lower:
                # Boost confidence based on frequency
                frequency = text_lower.count(tech.lower())
                confidence = min(1.0, base_confidence + (frequency * 0.1))
                found_tech.append((tech, confidence))
        
        return found_tech
    
    def _calculate_activity_score(self, conversations: List, code_entities: List) -> float:
        """Calculate activity score based on recent activity."""
        
        try:
            # Get recent activity (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            
            recent_conversations = [c for c in conversations 
                                  if c.get('created_at') and c['created_at'] > cutoff_date]
            recent_code = [c for c in code_entities 
                          if c.get('created_at') and c['created_at'] > cutoff_date]
            
            # Calculate score based on activity volume and recency
            conversation_score = len(recent_conversations) * 0.3
            code_score = len(recent_code) * 0.5
            
            return min(1.0, conversation_score + code_score)
            
        except Exception as e:
            logger.warning(f"Failed to calculate activity score: {e}")
            return 0.0
    
    def _get_cross_domain_insights(self, entity_id: str) -> Dict[str, Any]:
        """Get cross-domain insights for a specific entity."""
        
        try:
            entity = self.memory_store.get_entity(entity_id)
            if not entity:
                return {"error": "Entity not found"}
            
            # Convert MemoryEntity to dict if needed
            if hasattr(entity, 'to_dict'):
                entity_dict = entity.to_dict()
            else:
                entity_dict = entity
            
            entity_type = entity_dict.get('type')
            insights = {
                'entity': entity_dict,
                'related_content': {},
                'patterns': {},
                'recommendations': []
            }
            
            # Get all related entities
            related_entities = self.memory_store.get_related(entity_id)
            
            # Convert related entities to dicts if needed
            related_entities_dicts = []
            for related in related_entities:
                if hasattr(related, 'to_dict'):
                    related_entities_dicts.append(related.to_dict())
                else:
                    related_entities_dicts.append(related)
            
            # Group by type
            for related in related_entities_dicts:
                rel_type = related.get('type')
                if rel_type not in insights['related_content']:
                    insights['related_content'][rel_type] = []
                insights['related_content'][rel_type].append(related)
            
            # Generate insights based on entity type
            if entity_type == 'task':
                insights.update(self._get_task_insights(entity_dict, related_entities_dicts))
            elif entity_type == 'project':
                insights.update(self._get_project_insights(entity_dict, related_entities_dicts))
            elif entity_type == 'handoff':
                insights.update(self._get_conversation_insights(entity_dict, related_entities_dicts))
            elif entity_type == 'person':
                insights.update(self._get_person_insights(entity_dict, related_entities_dicts))
            
            return insights
            
        except Exception as e:
            logger.warning(f"Failed to get cross-domain insights: {e}")
            return {"error": str(e)}
    
    def _get_task_insights(self, task: Dict, related_entities: List) -> Dict:
        """Get insights specific to tasks."""
        
        insights = {
            'patterns': {},
            'recommendations': []
        }
        
        # Analyze task patterns
        conversations = [e for e in related_entities if e.get('type') == 'handoff']
        people = [e for e in related_entities if e.get('type') == 'person']
        
        if len(conversations) > 3:
            insights['patterns']['high_communication'] = True
            insights['recommendations'].append("This task has high communication overhead - consider documentation")
        
        if len(people) > 2:
            insights['patterns']['multi_person_task'] = True
            insights['recommendations'].append("Multiple people involved - ensure clear ownership")
        
        # Check for similar tasks
        similar_tasks = self.memory_store.search(task['name'], filters={"type": "task"})
        if len(similar_tasks) > 1:
            insights['patterns']['recurring_task'] = True
            insights['recommendations'].append("Similar tasks exist - consider creating a template")
        
        return insights
    
    def _get_project_insights(self, project: Dict, related_entities: List) -> Dict:
        """Get insights specific to projects."""
        
        insights = {
            'patterns': {},
            'recommendations': []
        }
        
        tasks = [e for e in related_entities if e.get('type') == 'task']
        conversations = [e for e in related_entities if e.get('type') == 'handoff']
        files = [e for e in related_entities if e.get('type') in ['file', 'function']]
        
        # Project health indicators
        if tasks:
            completed_tasks = [t for t in tasks if t.get('metadata', {}).get('status') == 'completed']
            completion_rate = len(completed_tasks) / len(tasks)
            
            if completion_rate < 0.3:
                insights['patterns']['low_completion'] = True
                insights['recommendations'].append("Low task completion rate - review project scope")
            elif completion_rate > 0.8:
                insights['patterns']['high_completion'] = True
                insights['recommendations'].append("High completion rate - consider adding more tasks")
        
        if len(conversations) < 2:
            insights['patterns']['low_communication'] = True
            insights['recommendations'].append("Limited communication - schedule regular check-ins")
        
        if len(files) == 0:
            insights['patterns']['no_code'] = True
            insights['recommendations'].append("No code files yet - start implementation")
        
        return insights
    
    def _get_conversation_insights(self, conversation: Dict, related_entities: List) -> Dict:
        """Get insights specific to conversations."""
        
        insights = {
            'patterns': {},
            'recommendations': []
        }
        
        people = [e for e in related_entities if e.get('type') == 'person']
        tasks = [e for e in related_entities if e.get('type') == 'task']
        
        # Extract action items
        action_items = self._extract_action_items_from_text(conversation.get('content', ''))
        if action_items:
            insights['patterns']['has_action_items'] = True
            insights['recommendations'].extend([f"Create task: {action}" for action in action_items[:3]])
        
        if len(people) > 3:
            insights['patterns']['large_meeting'] = True
            insights['recommendations'].append("Large group discussion - consider smaller focused meetings")
        
        if not tasks:
            insights['patterns']['no_followup_tasks'] = True
            insights['recommendations'].append("No tasks created - review for action items")
        
        return insights
    
    def _get_person_insights(self, person: Dict, related_entities: List) -> Dict:
        """Get insights specific to people."""
        
        insights = {
            'patterns': {},
            'recommendations': []
        }
        
        projects = [e for e in related_entities if e.get('type') == 'project']
        conversations = [e for e in related_entities if e.get('type') == 'handoff']
        files = [e for e in related_entities if e.get('type') in ['file', 'function']]
        
        if len(projects) > 3:
            insights['patterns']['multi_project'] = True
            insights['recommendations'].append("Involved in many projects - check workload")
        
        if len(conversations) > 10:
            insights['patterns']['high_communication'] = True
            insights['recommendations'].append("High communication volume - consider async communication")
        
        if len(files) > 5:
            insights['patterns']['active_coder'] = True
            insights['recommendations'].append("Active code contributor - ensure code reviews")
        
        return insights
    
    def _extract_action_items_from_text(self, text: str) -> List[str]:
        """Extract action items from text."""
        
        action_items = []
        
        # Look for action-oriented phrases
        action_patterns = [
            r'need to (\w+)',
            r'should (\w+)',
            r'must (\w+)',
            r'will (\w+)',
            r'going to (\w+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                action_items.append(f"{match}")
        
        return action_items[:5]  # Limit to 5 items
    
    def _search_with_context(self, query: str, entity_context: str = None) -> Dict[str, Any]:
        """Search with additional context about the current entity."""
        
        try:
            # If entity context is provided, enhance the search
            if entity_context:
                # Parse the context to understand what entity we're looking at
                context_info = self._parse_entity_context(entity_context)
                
                # Enhance the search with context
                enhanced_query = f"{query} {context_info.get('keywords', '')}"
                
                # Get results
                results = self.search_engine.universal_search(enhanced_query)
                
                # Add context-specific filtering
                if context_info.get('entity_type'):
                    filtered_results = {}
                    for entity_type, entities in results.items():
                        if entity_type == context_info['entity_type']:
                            filtered_results[entity_type] = entities
                    
                    results = filtered_results
                
                return {
                    'query': query,
                    'context': context_info,
                    'enhanced_query': enhanced_query,
                    'results': results
                }
            else:
                # Regular search without context
                return self.search_engine.universal_search(query)
                
        except Exception as e:
            logger.warning(f"Contextual search failed: {e}")
            return {"error": str(e), "results": {}}
    
    def _parse_entity_context(self, context: str) -> Dict[str, Any]:
        """Parse entity context string to extract relevant information."""
        
        context_info = {
            'entity_type': None,
            'keywords': [],
            'entity_name': None
        }
        
        context_lower = context.lower()
        
        # Extract entity type
        if 'task' in context_lower:
            context_info['entity_type'] = 'task'
        elif 'project' in context_lower:
            context_info['entity_type'] = 'project'
        elif 'conversation' in context_lower or 'chat' in context_lower:
            context_info['entity_type'] = 'handoff'
        elif 'file' in context_lower or 'code' in context_lower:
            context_info['entity_type'] = 'file'
        elif 'person' in context_lower:
            context_info['entity_type'] = 'person'
        
        # Extract keywords
        words = context.split()
        for word in words:
            if len(word) > 3 and word.lower() not in ['task', 'project', 'conversation', 'file', 'person']:
                context_info['keywords'].append(word)
        
        return context_info 