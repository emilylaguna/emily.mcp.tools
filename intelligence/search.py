"""
Intelligent Search Engine with Cross-Domain Intelligence

This module provides advanced semantic search and cross-domain intelligence
features that leverage the unified memory system to provide insights across
all tool types.
"""

import re
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from emily_core import UnifiedMemoryStore, MemoryEntity, MemoryContext

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result with enhanced metadata."""
    id: str
    type: str
    name: str
    content: str
    relevance_score: float
    search_matches: int = 1
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    cross_references: List[str] = None


class IntelligentSearchEngine:
    """Advanced search engine with cross-domain intelligence."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.search_cache = {}  # Cache for performance
        
    def universal_search(self, query: str, 
                        entity_types: List[str] = None,
                        time_range: Dict = None,
                        context_filters: Dict = None) -> Dict[str, List]:
        """Search across all entity types with intelligent ranking."""
        
        # 1. Semantic vector search
        vector_results = self._semantic_search(query, entity_types)
        
        # 2. Full-text search for exact matches
        fts_results = self._fulltext_search(query, entity_types)
        
        # 3. Entity relationship search (only if no entity type filter)
        relationship_results = []
        if not entity_types:
            relationship_results = self._relationship_search(query)
        
        # 4. Context-aware search (only if no entity type filter)
        contextual_results = []
        if not entity_types:
            contextual_results = self._contextual_search(query, context_filters)
        
        # 5. Combine and rank intelligently
        combined_results = self._intelligent_ranking(
            vector_results, fts_results, relationship_results, contextual_results
        )
        
        # 6. Filter by entity types if specified
        if entity_types:
            combined_results = [
                result for result in combined_results 
                if result.get('type') in entity_types
            ]
        
        # 7. Group by entity type with cross-references
        return self._group_with_cross_references(combined_results)
    
    def intent_based_search(self, natural_query: str) -> Dict[str, Any]:
        """Understand search intent and provide contextual results."""
        
        # Parse search intent
        intent = self._parse_search_intent(natural_query)
        
        # Execute appropriate search strategy
        if intent['type'] == 'find_related':
            return self._find_related_content(intent)
        elif intent['type'] == 'timeline':
            return self._create_timeline_view(intent)
        elif intent['type'] == 'expertise_lookup':
            return self._find_expertise(intent)
        elif intent['type'] == 'project_status':
            return self._get_project_status(intent)
        else:
            return self.universal_search(natural_query)
    
    def _semantic_search(self, query: str, entity_types: List[str] = None) -> List[Dict]:
        """Perform semantic vector search."""
        try:
            filters = {"type": entity_types[0]} if entity_types and len(entity_types) == 1 else {}
            results = self.memory.search(query, filters=filters, limit=20)
            return [self._enhance_result(r, 0.8) for r in results]
        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            return []
    
    def _fulltext_search(self, query: str, entity_types: List[str] = None) -> List[Dict]:
        """Perform full-text search for exact matches."""
        try:
            filters = {"type": entity_types[0]} if entity_types and len(entity_types) == 1 else {}
            # Use SQLite FTS for exact matches
            results = self.memory.search(query, filters=filters, limit=20)
            return [self._enhance_result(r, 0.9) for r in results]
        except Exception as e:
            logger.warning(f"Full-text search failed: {e}")
            return []
    
    def _relationship_search(self, query: str) -> List[Dict]:
        """Search through entity relationships."""
        try:
            # Find entities that match the query
            matching_entities = self.memory.search(query, limit=10)
            relationship_results = []
            
            for entity in matching_entities:
                # Get related entities
                related = self.memory.get_related(entity['id'])
                for rel in related:
                    rel_result = self._enhance_result(rel, 0.6)
                    rel_result['related_to'] = entity['id']
                    relationship_results.append(rel_result)
            
            return relationship_results
        except Exception as e:
            logger.warning(f"Relationship search failed: {e}")
            return []
    
    def _contextual_search(self, query: str, context_filters: Dict = None) -> List[Dict]:
        """Search with context awareness."""
        try:
            # Search contexts first
            context_results = self.memory.search(query, filters={"type": "handoff"}, limit=10)
            contextual_results = []
            
            for context in context_results:
                # Get entities mentioned in this context
                related_entities = self.memory.get_related(context['id'])
                for entity in related_entities:
                    entity_result = self._enhance_result(entity, 0.7)
                    entity_result['context_id'] = context['id']
                    contextual_results.append(entity_result)
            
            return contextual_results
        except Exception as e:
            logger.warning(f"Contextual search failed: {e}")
            return []
    
    def _parse_search_intent(self, query: str) -> Dict[str, Any]:
        """Parse natural language search intent."""
        query_lower = query.lower()
        
        # Timeline queries
        if any(word in query_lower for word in ['timeline', 'history', 'progress', 'over time']):
            # Look for "project X" pattern
            project_match = re.search(r'project\s+([a-zA-Z0-9_-]+)', query_lower)
            if project_match:
                return {
                    'type': 'timeline',
                    'project': project_match.group(1),
                    'query': query
                }
            # Look for "for X" pattern
            for_match = re.search(r'for\s+([a-zA-Z0-9_-]+)', query_lower)
            if for_match:
                return {
                    'type': 'timeline',
                    'project': for_match.group(1),
                    'query': query
                }
            return {
                'type': 'timeline',
                'project': None,
                'query': query
            }
        
        # Expertise/people queries
        if any(word in query_lower for word in ['who knows', 'expert in', 'worked on', 'familiar with']):
            # Look for "about X" pattern
            about_match = re.search(r'about\s+([a-zA-Z0-9_-]+)', query_lower)
            if about_match:
                return {
                    'type': 'expertise_lookup', 
                    'technology': about_match.group(1),
                    'query': query
                }
            # Look for "expert in X" pattern
            expert_match = re.search(r'expert in\s+([a-zA-Z0-9_-]+)', query_lower)
            if expert_match:
                return {
                    'type': 'expertise_lookup', 
                    'technology': expert_match.group(1),
                    'query': query
                }
            return {
                'type': 'expertise_lookup', 
                'technology': None,
                'query': query
            }
        
        # Related content queries
        if any(word in query_lower for word in ['related to', 'similar to', 'connected to']):
            return {
                'type': 'find_related',
                'query': query
            }
        
        # Project status queries
        if any(word in query_lower for word in ['status of', 'how is', 'progress on']):
            # Look for "status of project X" pattern
            status_match = re.search(r'status of\s+project\s+([a-zA-Z0-9_-]+)', query_lower)
            if status_match:
                return {
                    'type': 'project_status',
                    'project': status_match.group(1),
                    'query': query
                }
            # Look for "how is project X" pattern
            how_match = re.search(r'how is\s+project\s+([a-zA-Z0-9_-]+)', query_lower)
            if how_match:
                return {
                    'type': 'project_status',
                    'project': how_match.group(1),
                    'query': query
                }
            return {
                'type': 'project_status',
                'project': None,
                'query': query
            }
        
        # Default to universal search
        return {
            'type': 'universal',
            'query': query
        }
    
    def _intelligent_ranking(self, *result_sets) -> List[Dict]:
        """Combine multiple search result sets with intelligent ranking."""
        
        # Combine all results
        all_results = {}
        for result_set in result_sets:
            for result in result_set:
                entity_id = result['id']
                
                if entity_id in all_results:
                    # Boost score for entities found in multiple searches
                    all_results[entity_id]['relevance_score'] += result.get('relevance_score', 0.5)
                    all_results[entity_id]['search_matches'] += 1
                else:
                    all_results[entity_id] = {
                        **result,
                        'search_matches': 1,
                        'relevance_score': result.get('relevance_score', 0.5)
                    }
        
        # Apply intelligent boosting
        for entity_id, result in all_results.items():
            entity_type = result.get('type')
            
            # Boost recent items
            if result.get('created_at'):
                try:
                    # Handle both datetime objects and string timestamps
                    if isinstance(result['created_at'], str):
                        created_at = datetime.fromisoformat(result['created_at'].replace('Z', '+00:00'))
                    else:
                        created_at = result['created_at']
                    
                    age_days = (datetime.now(timezone.utc) - created_at).days
                    recency_boost = max(0.1, 1.0 - (age_days / 30))  # Boost recent items
                    result['relevance_score'] *= (1 + recency_boost * 0.2)
                except Exception:
                    # Skip recency boosting if date parsing fails
                    pass
            
            # Boost based on entity relationships
            try:
                relationship_count = len(self.memory.get_related(entity_id))
                relationship_boost = min(0.3, relationship_count * 0.05)
                result['relevance_score'] *= (1 + relationship_boost)
            except Exception:
                pass
            
            # Type-specific boosting
            type_boosts = {
                'task': 1.1,      # Slightly boost tasks (actionable)
                'person': 1.2,    # Boost people (important for collaboration)
                'project': 1.3,   # Boost projects (high-level context)
                'handoff': 1.1    # Boost conversations (context-rich)
            }
            result['relevance_score'] *= type_boosts.get(entity_type, 1.0)
        
        # Sort by enhanced relevance score
        return sorted(all_results.values(), 
                     key=lambda x: x['relevance_score'], 
                     reverse=True)
    
    def _group_with_cross_references(self, results: List[Dict]) -> Dict[str, List]:
        """Group results by entity type with cross-references."""
        grouped = {}
        
        for result in results:
            entity_type = result.get('type', 'unknown')
            if entity_type not in grouped:
                grouped[entity_type] = []
            
            # Add cross-references
            cross_refs = []
            try:
                related = self.memory.get_related(result['id'])
                cross_refs = [r['id'] for r in related[:5]]  # Limit to 5 cross-refs
            except Exception:
                pass
            
            result['cross_references'] = cross_refs
            grouped[entity_type].append(result)
        
        return grouped
    
    def _enhance_result(self, result: Dict, base_score: float) -> Dict:
        """Enhance a search result with additional metadata."""
        return {
            **result,
            'relevance_score': base_score,
            'search_matches': 1
        }
    
    def _find_related_content(self, intent: Dict) -> Dict[str, Any]:
        """Find content related to the query."""
        query = intent['query']
        results = self.universal_search(query)
        
        return {
            'intent': 'find_related',
            'query': query,
            'results': results,
            'suggestions': self._generate_related_suggestions(query)
        }
    
    def _create_timeline_view(self, intent: Dict) -> Dict[str, Any]:
        """Create a timeline view for a project or entity."""
        project_name = intent.get('project')
        
        if project_name:
            # Search for the project
            project_results = self.memory.search(project_name, filters={"type": "project"})
            if project_results:
                project_id = project_results[0]['id']
                timeline = self._get_project_timeline(project_id)
                return {
                    'intent': 'timeline',
                    'project': project_name,
                    'timeline': timeline
                }
        
        # Fallback to general timeline
        return {
            'intent': 'timeline',
            'timeline': self._get_general_timeline()
        }
    
    def _find_expertise(self, intent: Dict) -> Dict[str, Any]:
        """Find people with expertise in specific technology."""
        technology = intent.get('technology')
        
        if technology:
            experts = self._find_expert_for_technology(technology)
            return {
                'intent': 'expertise_lookup',
                'technology': technology,
                'experts': experts
            }
        
        return {
            'intent': 'expertise_lookup',
            'experts': []
        }
    
    def _get_project_status(self, intent: Dict) -> Dict[str, Any]:
        """Get comprehensive project status."""
        project_name = intent.get('project')
        
        if project_name:
            project_results = self.memory.search(project_name, filters={"type": "project"})
            if project_results:
                project_id = project_results[0]['id']
                intelligence = self.get_project_intelligence(project_id)
                return {
                    'intent': 'project_status',
                    'project': project_name,
                    'intelligence': intelligence
                }
        
        return {
            'intent': 'project_status',
            'intelligence': {}
        }
    
    def _generate_related_suggestions(self, query: str) -> List[str]:
        """Generate suggestions for related content."""
        suggestions = []
        
        # Extract potential entities from query
        words = query.split()
        for word in words:
            if len(word) > 3:  # Only consider substantial words
                suggestions.append(f"Find more about {word}")
        
        suggestions.append("Show related conversations")
        suggestions.append("Find similar tasks")
        suggestions.append("Show project timeline")
        
        return suggestions[:5]
    
    def _get_project_timeline(self, project_id: str) -> List[Dict]:
        """Get timeline for a specific project."""
        try:
            # Get all related entities
            related = self.memory.get_related(project_id)
            
            # Filter by date and sort
            timeline_items = []
            for entity in related:
                if entity.get('created_at'):
                    timeline_items.append({
                        'date': entity['created_at'],
                        'type': entity.get('type'),
                        'name': entity.get('name'),
                        'content': entity.get('content', '')[:100]
                    })
            
            # Sort by date
            timeline_items.sort(key=lambda x: x['date'], reverse=True)
            return timeline_items[:20]  # Limit to 20 items
            
        except Exception as e:
            logger.warning(f"Failed to get project timeline: {e}")
            return []
    
    def _get_general_timeline(self) -> List[Dict]:
        """Get general timeline of recent activity."""
        try:
            # Get recent entities
            recent_entities = self.memory.search("", limit=50)
            
            timeline_items = []
            for entity in recent_entities:
                if entity.get('created_at'):
                    timeline_items.append({
                        'date': entity['created_at'],
                        'type': entity.get('type'),
                        'name': entity.get('name'),
                        'content': entity.get('content', '')[:100]
                    })
            
            # Sort by date
            timeline_items.sort(key=lambda x: x['date'], reverse=True)
            return timeline_items[:20]
            
        except Exception as e:
            logger.warning(f"Failed to get general timeline: {e}")
            return []
    
    def _find_expert_for_technology(self, technology: str) -> List[Dict]:
        """Find people with expertise in specific technology."""
        try:
            # Search conversations mentioning the technology
            tech_conversations = self.memory.search(technology, filters={"type": "handoff"})
            
            # Find people mentioned in these conversations
            experts = {}
            
            for conv in tech_conversations:
                related_people = self.memory.get_related(conv['id'], ["mentions"])
                people = [p for p in related_people if p.get('type') == 'person']
                
                for person in people:
                    person_id = person['id']
                    if person_id not in experts:
                        experts[person_id] = {
                            'name': person['name'],
                            'mentions': 0,
                            'conversations': [],
                            'relevance_score': 0
                        }
                    
                    experts[person_id]['mentions'] += 1
                    experts[person_id]['conversations'].append(conv['id'])
                    
                    # Score based on conversation context
                    if technology.lower() in conv.get('content', '').lower():
                        context_relevance = conv.get('content', '').lower().count(technology.lower())
                        experts[person_id]['relevance_score'] += context_relevance
            
            # Also check code files
            code_files = self.memory.search(technology, filters={"type": "file"})
            for file in code_files:
                file_people = self.memory.get_related(file['id'], ["authored", "modified"])
                for person in file_people:
                    person_id = person['id']
                    if person_id in experts:
                        experts[person_id]['relevance_score'] += 5  # Boost for code involvement
            
            # Sort by relevance
            expert_list = sorted(experts.values(), 
                                key=lambda x: x['relevance_score'], 
                                reverse=True)
            
            return expert_list[:10]
            
        except Exception as e:
            logger.warning(f"Failed to find experts: {e}")
            return []
    
    def get_project_intelligence(self, project_id: str) -> Dict[str, Any]:
        """Comprehensive project intelligence across all domains."""
        try:
            # Get basic project info
            project = self.memory.get_entity(project_id)
            if not project:
                return {}
            
            # Get all related entities
            related_entities = self.memory.get_related(project_id)
            
            # Categorize related content
            tasks = [e for e in related_entities if e.get('type') == 'task']
            conversations = [e for e in related_entities if e.get('type') == 'handoff']
            files = [e for e in related_entities if e.get('type') in ['file', 'function']]
            people = [e for e in related_entities if e.get('type') == 'person']
            
            # Calculate project metrics
            task_completion = self._calculate_task_completion(tasks)
            conversation_insights = self._analyze_conversation_patterns(conversations)
            code_activity = self._analyze_code_activity(files)
            team_dynamics = self._analyze_team_dynamics(people, conversations)
            
            # AI-generated insights
            project_health = self._assess_project_health(tasks, conversations, files)
            blockers = self._identify_blockers(tasks, conversations)
            recommendations = self._generate_recommendations(project_id, tasks, conversations)
            
            return {
                'project': project,
                'metrics': {
                    'task_completion': task_completion,
                    'conversation_volume': len(conversations),
                    'code_files': len(files),
                    'team_size': len(people)
                },
                'insights': {
                    'conversation_patterns': conversation_insights,
                    'code_activity': code_activity,
                    'team_dynamics': team_dynamics
                },
                'ai_analysis': {
                    'health_score': project_health,
                    'identified_blockers': blockers,
                    'recommendations': recommendations
                },
                'timeline': self._get_project_timeline(project_id),
                'related_projects': self._find_similar_projects(project_id)
            }
            
        except Exception as e:
            logger.warning(f"Failed to get project intelligence: {e}")
            return {}
    
    def _calculate_task_completion(self, tasks: List) -> Dict:
        """Calculate task completion metrics."""
        if not tasks:
            return {'completion_rate': 0, 'total_tasks': 0, 'completed_tasks': 0}
        
        completed_tasks = [t for t in tasks if t.get('metadata', {}).get('status') == 'completed']
        completion_rate = len(completed_tasks) / len(tasks)
        
        return {
            'completion_rate': completion_rate,
            'total_tasks': len(tasks),
            'completed_tasks': len(completed_tasks)
        }
    
    def _analyze_conversation_patterns(self, conversations: List) -> Dict:
        """Analyze conversation patterns."""
        if not conversations:
            return {'total_conversations': 0, 'recent_activity': False}
        
        # Check recent activity
        latest_conversation = max(conversations, key=lambda c: c.get('created_at', datetime.min))
        days_since_discussion = (datetime.now() - latest_conversation['created_at']).days
        
        return {
            'total_conversations': len(conversations),
            'recent_activity': days_since_discussion < 7,
            'days_since_last_discussion': days_since_discussion
        }
    
    def _analyze_code_activity(self, files: List) -> Dict:
        """Analyze code activity patterns."""
        if not files:
            return {'total_files': 0, 'recent_activity': False}
        
        recent_files = [f for f in files 
                       if (datetime.now() - f.get('created_at', datetime.min)).days < 7]
        
        return {
            'total_files': len(files),
            'recent_activity': len(recent_files) > 0,
            'recent_files_count': len(recent_files)
        }
    
    def _analyze_team_dynamics(self, people: List, conversations: List) -> Dict:
        """Analyze team dynamics."""
        return {
            'team_size': len(people),
            'active_participants': len(set([p['id'] for p in people])),
            'conversation_participation': len(conversations)
        }
    
    def _assess_project_health(self, tasks: List, conversations: List, files: List) -> Dict:
        """AI assessment of project health."""
        health_score = 1.0
        issues = []
        
        # Task completion rate
        if tasks:
            completed_tasks = [t for t in tasks if t.get('metadata', {}).get('status') == 'completed']
            completion_rate = len(completed_tasks) / len(tasks)
            
            if completion_rate < 0.3:
                health_score *= 0.7
                issues.append("Low task completion rate")
            elif completion_rate > 0.8:
                health_score *= 1.1
        
        # Conversation recency
        if conversations:
            latest_conversation = max(conversations, key=lambda c: c.get('created_at', datetime.min))
            days_since_discussion = (datetime.now() - latest_conversation['created_at']).days
            
            if days_since_discussion > 14:
                health_score *= 0.8
                issues.append("No recent discussions")
            elif days_since_discussion < 3:
                health_score *= 1.05
        
        # Code activity
        if files:
            recent_files = [f for f in files 
                           if (datetime.now() - f.get('created_at', datetime.min)).days < 7]
            if not recent_files and len(files) > 0:
                health_score *= 0.9
                issues.append("No recent code activity")
        
        return {
            'score': min(1.0, health_score),
            'status': 'healthy' if health_score > 0.8 else 'at_risk' if health_score > 0.6 else 'concerning',
            'issues': issues
        }
    
    def _identify_blockers(self, tasks: List, conversations: List) -> List[str]:
        """Identify potential project blockers."""
        blockers = []
        
        # Check for overdue tasks
        overdue_tasks = [t for t in tasks 
                        if t.get('metadata', {}).get('due_date') and 
                        datetime.now() > t['metadata']['due_date']]
        
        if overdue_tasks:
            blockers.append(f"{len(overdue_tasks)} overdue tasks")
        
        # Check for tasks without assignees
        unassigned_tasks = [t for t in tasks 
                           if not t.get('metadata', {}).get('assigned_to')]
        
        if unassigned_tasks:
            blockers.append(f"{len(unassigned_tasks)} unassigned tasks")
        
        return blockers
    
    def _generate_recommendations(self, project_id: str, tasks: List, conversations: List) -> List[str]:
        """Generate AI recommendations for the project."""
        recommendations = []
        
        if not conversations:
            recommendations.append("Schedule a project kickoff meeting")
        
        if len(tasks) < 3:
            recommendations.append("Break down project into smaller tasks")
        
        overdue_tasks = [t for t in tasks 
                        if t.get('metadata', {}).get('due_date') and 
                        datetime.now() > t['metadata']['due_date']]
        
        if overdue_tasks:
            recommendations.append("Review and update overdue task deadlines")
        
        return recommendations
    
    def _find_similar_projects(self, project_id: str) -> List[Dict]:
        """Find projects similar to the given project."""
        try:
            project = self.memory.get_entity(project_id)
            if not project:
                return []
            
            # Search for projects with similar content
            similar_projects = self.memory.search(
                project.get('content', '')[:100], 
                filters={"type": "project"},
                limit=5
            )
            
            # Filter out the current project
            similar_projects = [p for p in similar_projects if p['id'] != project_id]
            
            return similar_projects[:3]
            
        except Exception as e:
            logger.warning(f"Failed to find similar projects: {e}")
            return [] 