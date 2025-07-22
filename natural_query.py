"""
Natural Language Query Processor

This module processes complex natural language queries and provides
intelligent results based on the unified memory system.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from core import UnifiedMemoryStore
from models import MemoryEntity, MemoryContext

logger = logging.getLogger(__name__)


class NaturalQueryProcessor:
    """Process complex natural language queries."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and return intelligent results."""
        
        # Example queries:
        # "Show me all discussions about authentication in the last month"
        # "Who has been working on the API project?"  
        # "What tasks are related to the database migration?"
        # "Find conversations where Alice mentioned React"
        
        # Parse query components
        query_components = self._parse_query_components(query)
        
        # Build search strategy
        search_strategy = self._build_search_strategy(query_components)
        
        # Execute search
        results = self._execute_search(search_strategy)
        
        # Format response
        return self._format_response(results, query_components)
    
    def _parse_query_components(self, query: str) -> Dict:
        """Extract components from natural language query."""
        
        components = {
            'entity_types': [],
            'people': [],
            'technologies': [],
            'time_range': None,
            'action': None,
            'relationships': [],
            'keywords': []
        }
        
        query_lower = query.lower()
        
        # Entity types
        if 'task' in query_lower or 'todo' in query_lower:
            components['entity_types'].append('task')
        if 'conversation' in query_lower or 'discussion' in query_lower or 'chat' in query_lower:
            components['entity_types'].append('handoff')
        if 'file' in query_lower or 'code' in query_lower:
            components['entity_types'].append('file')
        if 'project' in query_lower:
            components['entity_types'].append('project')
        if 'person' in query_lower or 'people' in query_lower or 'who' in query_lower:
            components['entity_types'].append('person')
        
        # Time ranges
        time_patterns = [
            (r'last (\d+) days?', lambda m: timedelta(days=int(m.group(1)))),
            (r'last week', lambda m: timedelta(weeks=1)),
            (r'last month', lambda m: timedelta(days=30)),
            (r'this year', lambda m: timedelta(days=365)),
            (r'today', lambda m: timedelta(days=1)),
            (r'yesterday', lambda m: timedelta(days=1)),
            (r'this week', lambda m: timedelta(weeks=1))
        ]
        
        for pattern, converter in time_patterns:
            match = re.search(pattern, query_lower)
            if match:
                time_delta = converter(match)
                components['time_range'] = {
                    'start': datetime.now() - time_delta,
                    'end': datetime.now()
                }
                break
        
        # People (capitalized names)
        people_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        potential_people = re.findall(people_pattern, query)
        components['people'] = potential_people
        
        # Technologies
        tech_keywords = [
            'React', 'Python', 'JavaScript', 'TypeScript', 'API', 'database', 
            'authentication', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker',
            'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'GitHub', 'GitLab'
        ]
        for tech in tech_keywords:
            if tech.lower() in query_lower:
                components['technologies'].append(tech)
        
        # Actions
        action_keywords = ['show', 'find', 'get', 'list', 'search', 'who', 'what', 'when', 'where']
        for action in action_keywords:
            if action in query_lower:
                components['action'] = action
                break
        
        # Keywords (important words that aren't captured above)
        words = query.split()
        for word in words:
            word_lower = word.lower()
            if (len(word) > 3 and 
                word_lower not in ['show', 'find', 'get', 'list', 'search', 'about', 'with', 'from', 'that', 'this', 'last', 'week', 'month', 'year']):
                components['keywords'].append(word)
        
        return components
    
    def _build_search_strategy(self, components: Dict) -> Dict:
        """Build search strategy based on parsed components."""
        
        strategy = {
            'query': ' '.join(components['keywords']),
            'filters': {},
            'limit': 20,
            'expand_relationships': False,
            'time_range': components.get('time_range')
        }
        
        # Add entity type filters
        if components['entity_types']:
            if len(components['entity_types']) == 1:
                strategy['filters']['type'] = components['entity_types'][0]
            else:
                # Multiple entity types - we'll filter after search
                strategy['entity_types'] = components['entity_types']
        
        # Add people filters
        if components.get('people'):
            strategy['people_filter'] = components['people']
        
        # Add technology filters
        if components.get('technologies'):
            strategy['technology_filter'] = components['technologies']
        
        # Determine if we should expand relationships
        if components.get('action') in ['find', 'search'] and components['keywords']:
            strategy['expand_relationships'] = True
        
        return strategy
    
    def _execute_search(self, strategy: Dict) -> List[Dict]:
        """Execute search based on parsed strategy."""
        
        results = []
        
        try:
            # Base search
            base_results = self.memory.search(
                strategy['query'],
                filters=strategy.get('filters', {}),
                limit=strategy.get('limit', 20)
            )
            results.extend(base_results)
            
            # Relationship-based expansion
            if strategy.get('expand_relationships'):
                for result in base_results[:5]:  # Expand top 5 results
                    try:
                        related = self.memory.get_related(result['id'])
                        results.extend(related)
                    except Exception as e:
                        logger.warning(f"Failed to expand relationships for {result['id']}: {e}")
            
            # Apply entity type filtering if multiple types specified
            if strategy.get('entity_types'):
                results = [r for r in results if r.get('type') in strategy['entity_types']]
            
            # Apply people filtering
            if strategy.get('people_filter'):
                people_filter = strategy['people_filter']
                filtered_results = []
                
                for result in results:
                    # Check if any of the people are mentioned in the result
                    result_text = f"{result.get('name', '')} {result.get('content', '')}".lower()
                    if any(person.lower() in result_text for person in people_filter):
                        filtered_results.append(result)
                    else:
                        # Check related entities for people
                        try:
                            related = self.memory.get_related(result['id'])
                            people = [r for r in related if r.get('type') == 'person']
                            if any(p.get('name', '').lower() in [person.lower() for person in people_filter] 
                                  for p in people):
                                filtered_results.append(result)
                        except Exception:
                            pass
                
                results = filtered_results
            
            # Apply technology filtering
            if strategy.get('technology_filter'):
                tech_filter = strategy['technology_filter']
                filtered_results = []
                
                for result in results:
                    result_text = f"{result.get('name', '')} {result.get('content', '')}".lower()
                    if any(tech.lower() in result_text for tech in tech_filter):
                        filtered_results.append(result)
                
                results = filtered_results
            
            # Time filtering
            if strategy.get('time_range'):
                time_range = strategy['time_range']
                results = [r for r in results 
                          if r.get('created_at') and 
                          time_range['start'] <= r['created_at'] <= time_range['end']]
            
            # Remove duplicates based on ID
            seen_ids = set()
            unique_results = []
            for result in results:
                if result['id'] not in seen_ids:
                    seen_ids.add(result['id'])
                    unique_results.append(result)
            
            return unique_results
            
        except Exception as e:
            logger.warning(f"Search execution failed: {e}")
            return []
    
    def _format_response(self, results: List[Dict], components: Dict) -> Dict[str, Any]:
        """Format search results into a structured response."""
        
        # Group results by entity type
        grouped_results = {}
        for result in results:
            entity_type = result.get('type', 'unknown')
            if entity_type not in grouped_results:
                grouped_results[entity_type] = []
            grouped_results[entity_type].append(result)
        
        # Create summary
        summary = self._create_summary(results, components)
        
        # Add suggestions
        suggestions = self._generate_suggestions(components, results)
        
        return {
            'query': ' '.join(components['keywords']),
            'components': components,
            'summary': summary,
            'results': grouped_results,
            'suggestions': suggestions,
            'total_results': len(results)
        }
    
    def _create_summary(self, results: List[Dict], components: Dict) -> Dict:
        """Create a summary of the search results."""
        
        summary = {
            'total_found': len(results),
            'entity_types': {},
            'time_range': components.get('time_range'),
            'key_insights': []
        }
        
        # Count by entity type
        for result in results:
            entity_type = result.get('type', 'unknown')
            summary['entity_types'][entity_type] = summary['entity_types'].get(entity_type, 0) + 1
        
        # Generate key insights
        if components.get('people'):
            people_found = [r for r in results if any(p.lower() in r.get('name', '').lower() 
                                                     for p in components['people'])]
            if people_found:
                summary['key_insights'].append(f"Found {len(people_found)} items related to {', '.join(components['people'])}")
        
        if components.get('technologies'):
            tech_found = [r for r in results if any(t.lower() in r.get('content', '').lower() 
                                                   for t in components['technologies'])]
            if tech_found:
                summary['key_insights'].append(f"Found {len(tech_found)} items mentioning {', '.join(components['technologies'])}")
        
        if components.get('time_range'):
            summary['key_insights'].append(f"Results from the last {self._format_time_range(components['time_range'])}")
        
        return summary
    
    def _format_time_range(self, time_range: Dict) -> str:
        """Format time range for display."""
        delta = time_range['end'] - time_range['start']
        
        if delta.days == 1:
            return "day"
        elif delta.days == 7:
            return "week"
        elif delta.days == 30:
            return "month"
        elif delta.days == 365:
            return "year"
        else:
            return f"{delta.days} days"
    
    def _generate_suggestions(self, components: Dict, results: List[Dict]) -> List[str]:
        """Generate suggestions based on search results and components."""
        
        suggestions = []
        
        # If no results, suggest broader search
        if not results:
            suggestions.append("Try a broader search term")
            if components.get('time_range'):
                suggestions.append("Try searching without time restrictions")
            if components.get('entity_types'):
                suggestions.append("Try searching across all content types")
        
        # If results found, suggest related searches
        else:
            # Suggest related entity types
            found_types = set(r.get('type') for r in results)
            all_types = {'task', 'handoff', 'file', 'project', 'person'}
            missing_types = all_types - found_types
            
            if missing_types:
                suggestions.append(f"Also search for: {', '.join(missing_types)}")
            
            # Suggest time-based refinements
            if not components.get('time_range'):
                suggestions.append("Filter by time: 'last week', 'last month'")
            
            # Suggest people-based refinements
            if not components.get('people'):
                people_in_results = []
                for result in results:
                    if result.get('type') == 'person':
                        people_in_results.append(result.get('name'))
                
                if people_in_results:
                    suggestions.append(f"Related people: {', '.join(people_in_results[:3])}")
        
        return suggestions[:5]
    
    def process_complex_query(self, query: str) -> Dict[str, Any]:
        """Process more complex queries with multiple clauses."""
        
        # Split complex queries into parts
        parts = self._split_complex_query(query)
        
        if len(parts) == 1:
            return self.process_query(query)
        
        # Process each part
        part_results = []
        for part in parts:
            part_result = self.process_query(part.strip())
            part_results.append(part_result)
        
        # Combine results
        combined_results = self._combine_part_results(part_results)
        
        return {
            'query': query,
            'parts': parts,
            'part_results': part_results,
            'combined_results': combined_results
        }
    
    def _split_complex_query(self, query: str) -> List[str]:
        """Split complex queries into simpler parts."""
        
        # Split on common conjunctions
        conjunctions = [' and ', ' or ', ' but ', ' also ', ' plus ']
        
        for conj in conjunctions:
            if conj in query.lower():
                parts = query.split(conj)
                return [part.strip() for part in parts if part.strip()]
        
        # If no conjunctions, try to split on punctuation
        if ';' in query:
            parts = query.split(';')
            return [part.strip() for part in parts if part.strip()]
        
        # Default: return as single part
        return [query]
    
    def _combine_part_results(self, part_results: List[Dict]) -> Dict[str, Any]:
        """Combine results from multiple query parts."""
        
        combined = {
            'total_results': 0,
            'entity_types': {},
            'all_results': [],
            'common_entities': []
        }
        
        # Collect all results
        all_results = []
        for part_result in part_results:
            all_results.extend(part_result.get('results', []))
            combined['total_results'] += part_result.get('total_results', 0)
        
        # Find common entities across parts
        entity_counts = {}
        for result in all_results:
            entity_id = result.get('id')
            if entity_id:
                entity_counts[entity_id] = entity_counts.get(entity_id, 0) + 1
        
        # Entities that appear in multiple parts are more relevant
        common_entities = [result for result in all_results 
                          if entity_counts.get(result.get('id'), 0) > 1]
        
        combined['all_results'] = all_results
        combined['common_entities'] = common_entities
        
        return combined 