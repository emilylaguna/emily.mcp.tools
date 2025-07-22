"""
Smart Suggestions Engine

This module provides contextual suggestions based on current user context
and cross-domain intelligence.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

try:
    from ..core import UnifiedMemoryStore
    from ..core.models import MemoryEntity, MemoryContext
except ImportError:
    from core import UnifiedMemoryStore
    from core.models import MemoryEntity, MemoryContext

logger = logging.getLogger(__name__)


class SmartSuggestionsEngine:
    """Provides contextual suggestions across all domains."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
    
    def get_contextual_suggestions(self, current_context: Dict) -> Dict[str, List]:
        """Get suggestions based on current user context."""
        
        suggestions = {
            'related_content': [],
            'follow_up_actions': [],
            'relevant_people': [],
            'similar_projects': [],
            'learning_resources': []
        }
        
        entity_type = current_context.get('type')
        entity_id = current_context.get('id')
        
        if entity_type == 'task':
            suggestions.update(self._task_suggestions(entity_id))
        elif entity_type == 'handoff':
            suggestions.update(self._conversation_suggestions(entity_id))
        elif entity_type == 'project':
            suggestions.update(self._project_suggestions(entity_id))
        elif entity_type == 'file':
            suggestions.update(self._code_suggestions(entity_id))
        elif entity_type == 'person':
            suggestions.update(self._person_suggestions(entity_id))
        
        return suggestions
    
    def _task_suggestions(self, task_id: str) -> Dict[str, List]:
        """Suggestions when viewing a task."""
        
        try:
            task = self.memory.get_entity(task_id)
            if not task:
                return {}
            
            # Convert MemoryEntity to dict for compatibility
            task_dict = task.to_dict()
            
            related_entities = self.memory.get_related(task_id)
            related_contexts = self.memory.get_related_contexts(task_id)
            
            suggestions = {}
            
            # Related conversations about this task
            related_convs = [e for e in related_entities if e.get('type') == 'handoff']
            related_convs.extend([c for c in related_contexts if c.get('type') == 'handoff'])
            suggestions['related_content'] = related_convs
            
            # People to involve
            task_content = f"{task_dict['name']} {task_dict.get('content', '')}"
            extracted_entities = self._extract_entities_from_text(task_content)
            people = [e for e in extracted_entities if e.get('type') == 'person']
            suggestions['relevant_people'] = people
            
            # Suggest similar tasks
            similar_tasks = self.memory.search(task_dict['name'], filters={"type": "task"})
            suggestions['similar_tasks'] = [t for t in similar_tasks if t['id'] != task_id][:3]
            
            # Follow-up actions
            actions = []
            if not related_convs:
                actions.append("Discuss this task with team members")
            
            project_id = task_dict.get('metadata', {}).get('project_id')
            if project_id:
                project_tasks = self.memory.search("", filters={
                    "type": "task", 
                    "metadata.project_id": project_id
                })
                if len(project_tasks) > 5:
                    actions.append("Review other project tasks for dependencies")
            
            # Check for overdue tasks
            if task_dict.get('metadata', {}).get('due_date'):
                due_date_str = task_dict['metadata']['due_date']
                try:
                    # Parse the due date string to datetime
                    if isinstance(due_date_str, str):
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                        if datetime.now() > due_date:
                            actions.append("Update deadline or mark as blocked")
                except (ValueError, TypeError):
                    # Skip if date parsing fails
                    pass
            
            suggestions['follow_up_actions'] = actions
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate task suggestions: {e}")
            return {}
    
    def _conversation_suggestions(self, context_id: str) -> Dict[str, List]:
        """Suggestions when viewing a conversation."""
        
        try:
            context = self.memory.get_context(context_id)
            if not context:
                return {}
            
            # Convert MemoryContext to dict for compatibility
            context_dict = context.to_dict()
            
            related_entities = self.memory.get_related(context_id)
            
            suggestions = {}
            
            # Extract action items for task creation
            action_items = self._extract_action_items(context_dict['content'])
            suggestions['follow_up_actions'] = [
                f"Create task: {action}" for action in action_items[:3]
            ]
            
            # Find related conversations
            similar_convs = self.memory.search(
                context_dict['content'][:200], 
                filters={"type": "handoff"}
            )
            suggestions['related_content'] = [c for c in similar_convs if c['id'] != context_id][:3]
            
            # Suggest people to follow up with
            people = [e for e in related_entities if e.get('type') == 'person']
            suggestions['relevant_people'] = people
            
            # Suggest related files/code
            files = [e for e in related_entities if e.get('type') in ['file', 'function']]
            suggestions['related_files'] = files
            
            # Extract mentioned technologies
            tech_mentions = self._extract_technologies(context_dict['content'])
            if tech_mentions:
                suggestions['learning_resources'] = [
                    f"Learn more about {tech}" for tech in tech_mentions[:3]
                ]
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate conversation suggestions: {e}")
            return {}
    
    def _project_suggestions(self, project_id: str) -> Dict[str, List]:
        """Suggestions when viewing a project."""
        
        try:
            project = self.memory.get_entity(project_id)
            if not project:
                return {}
            
            # Convert MemoryEntity to dict for compatibility
            project_dict = project.to_dict()
            
            related_entities = self.memory.get_related(project_id)
            
            suggestions = {}
            
            # Get project components
            tasks = [e for e in related_entities if e.get('type') == 'task']
            conversations = [e for e in related_entities if e.get('type') == 'handoff']
            files = [e for e in related_entities if e.get('type') in ['file', 'function']]
            people = [e for e in related_entities if e.get('type') == 'person']
            
            # Related content
            suggestions['related_content'] = conversations[:5]
            suggestions['relevant_people'] = people
            
            # Follow-up actions
            actions = []
            
            if not tasks:
                actions.append("Create initial project tasks")
            else:
                completed_tasks = [t for t in tasks if t.get('metadata', {}).get('status') == 'completed']
                if len(completed_tasks) == 0:
                    actions.append("Start working on project tasks")
                elif len(completed_tasks) < len(tasks):
                    actions.append("Review and update task progress")
            
            if not conversations:
                actions.append("Schedule project kickoff meeting")
            
            if len(files) == 0:
                actions.append("Set up project repository and initial files")
            
            suggestions['follow_up_actions'] = actions
            
            # Similar projects
            similar_projects = self.memory.search(
                project_dict.get('content', '')[:100], 
                filters={"type": "project"}
            )
            suggestions['similar_projects'] = [p for p in similar_projects if p['id'] != project_id][:3]
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate project suggestions: {e}")
            return {}
    
    def _code_suggestions(self, file_id: str) -> Dict[str, List]:
        """Suggestions when viewing code files."""
        
        try:
            file_entity = self.memory.get_entity(file_id)
            if not file_entity:
                return {}
            
            related_entities = self.memory.get_related(file_id)
            
            suggestions = {}
            
            # Related conversations about this code
            conversations = [e for e in related_entities if e.get('type') == 'handoff']
            suggestions['related_content'] = conversations
            
            # People who worked on this code
            people = [e for e in related_entities if e.get('type') == 'person']
            suggestions['relevant_people'] = people
            
            # Related files
            related_files = [e for e in related_entities if e.get('type') in ['file', 'function']]
            suggestions['related_files'] = [f for f in related_files if f['id'] != file_id][:5]
            
            # Follow-up actions
            actions = []
            
            if not conversations:
                actions.append("Document code changes and decisions")
            
            # Check if this is a new file
            if file_entity.get('created_at'):
                try:
                    created_at_str = file_entity['created_at']
                    if isinstance(created_at_str, str):
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        days_since_creation = (datetime.now() - created_at).days
                        if days_since_creation < 7:
                            actions.append("Add tests for new functionality")
                            actions.append("Update documentation")
                except (ValueError, TypeError):
                    # Skip if date parsing fails
                    pass
            
            suggestions['follow_up_actions'] = actions
            
            # Learning resources based on file type
            file_extension = file_entity.get('name', '').split('.')[-1].lower()
            if file_extension in ['py', 'js', 'ts', 'java', 'cpp', 'c']:
                suggestions['learning_resources'] = [
                    f"Best practices for {file_extension} development"
                ]
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate code suggestions: {e}")
            return {}
    
    def _person_suggestions(self, person_id: str) -> Dict[str, List]:
        """Suggestions when viewing a person's profile."""
        
        try:
            person = self.memory.get_entity(person_id)
            if not person:
                return {}
            
            related_entities = self.memory.get_related(person_id)
            
            suggestions = {}
            
            # Projects they're involved in
            projects = [e for e in related_entities if e.get('type') == 'project']
            suggestions['related_content'] = projects
            
            # Recent conversations
            conversations = [e for e in related_entities if e.get('type') == 'handoff']
            recent_conversations = sorted(conversations, 
                                        key=lambda x: x.get('created_at', datetime.min),
                                        reverse=True)[:5]
            suggestions['recent_conversations'] = recent_conversations
            
            # Files they've worked on
            files = [e for e in related_entities if e.get('type') in ['file', 'function']]
            suggestions['recent_files'] = files[:5]
            
            # Follow-up actions
            actions = []
            
            if conversations:
                latest_conversation = max(conversations, key=lambda x: x.get('created_at', datetime.min))
                days_since_contact = (datetime.now() - latest_conversation['created_at']).days
                
                if days_since_contact > 7:
                    actions.append("Schedule a catch-up meeting")
            
            if projects:
                actions.append("Review project collaboration opportunities")
            
            suggestions['follow_up_actions'] = actions
            
            # Similar people (based on project overlap)
            similar_people = self._find_similar_people(person_id, projects)
            suggestions['similar_people'] = similar_people
            
            return suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate person suggestions: {e}")
            return {}
    
    def _extract_entities_from_text(self, text: str) -> List[Dict]:
        """Extract potential entities from text."""
        try:
            # Simple entity extraction - in a real implementation, this would use AI
            entities = []
            
            # Look for capitalized names (potential people)
            import re
            name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            names = re.findall(name_pattern, text)
            
            for name in names:
                if len(name.split()) >= 2:  # Full names only
                    entities.append({
                        'type': 'person',
                        'name': name,
                        'confidence': 0.7
                    })
            
            # Look for technology mentions
            tech_keywords = ['Python', 'JavaScript', 'React', 'API', 'database', 'authentication']
            for tech in tech_keywords:
                if tech.lower() in text.lower():
                    entities.append({
                        'type': 'technology',
                        'name': tech,
                        'confidence': 0.8
                    })
            
            return entities
            
        except Exception as e:
            logger.warning(f"Failed to extract entities: {e}")
            return []
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract action items from text."""
        try:
            import re
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
            
        except Exception as e:
            logger.warning(f"Failed to extract action items: {e}")
            return []
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions from text."""
        try:
            tech_keywords = [
                'Python', 'JavaScript', 'TypeScript', 'React', 'Vue', 'Angular',
                'Node.js', 'Django', 'Flask', 'FastAPI', 'PostgreSQL', 'MongoDB',
                'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
                'Git', 'GitHub', 'GitLab', 'CI/CD', 'API', 'REST', 'GraphQL'
            ]
            
            mentioned_tech = []
            for tech in tech_keywords:
                if tech.lower() in text.lower():
                    mentioned_tech.append(tech)
            
            return mentioned_tech
            
        except Exception as e:
            logger.warning(f"Failed to extract technologies: {e}")
            return []
    
    def _find_similar_people(self, person_id: str, projects: List) -> List[Dict]:
        """Find people similar to the given person based on project overlap."""
        try:
            similar_people = []
            
            for project in projects:
                project_people = self.memory.get_related(project['id'])
                people = [p for p in project_people if p.get('type') == 'person' and p['id'] != person_id]
                
                for person in people:
                    # Check if we already have this person
                    existing = next((p for p in similar_people if p['id'] == person['id']), None)
                    if existing:
                        existing['overlap_count'] += 1
                    else:
                        person['overlap_count'] = 1
                        similar_people.append(person)
            
            # Sort by overlap count
            similar_people.sort(key=lambda x: x.get('overlap_count', 0), reverse=True)
            return similar_people[:5]
            
        except Exception as e:
            logger.warning(f"Failed to find similar people: {e}")
            return []
    
    def get_workflow_suggestions(self, user_context: Dict = None) -> Dict[str, List]:
        """Get workflow suggestions based on user's current activity."""
        
        suggestions = {
            'next_actions': [],
            'efficiency_tips': [],
            'collaboration_opportunities': []
        }
        
        # Analyze user's recent activity
        recent_entities = self._get_recent_user_activity()
        
        # Generate workflow suggestions
        if recent_entities:
            suggestions['next_actions'] = self._suggest_next_actions(recent_entities)
            suggestions['efficiency_tips'] = self._suggest_efficiency_improvements(recent_entities)
            suggestions['collaboration_opportunities'] = self._suggest_collaboration_opportunities(recent_entities)
        
        return suggestions
    
    def _get_recent_user_activity(self) -> List[Dict]:
        """Get recent user activity from the memory store."""
        try:
            # Get recent entities (last 7 days)
            recent_entities = self.memory.search("", limit=50)
            
            # Filter by recent activity
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_entities = [e for e in recent_entities 
                             if e.get('created_at') and e['created_at'] > cutoff_date]
            
            return recent_entities
            
        except Exception as e:
            logger.warning(f"Failed to get recent activity: {e}")
            return []
    
    def _suggest_next_actions(self, recent_entities: List[Dict]) -> List[str]:
        """Suggest next actions based on recent activity."""
        suggestions = []
        
        # Analyze entity types
        entity_types = [e.get('type') for e in recent_entities]
        
        if 'task' in entity_types:
            # Check for incomplete tasks
            tasks = [e for e in recent_entities if e.get('type') == 'task']
            incomplete_tasks = [t for t in tasks 
                              if t.get('metadata', {}).get('status') != 'completed']
            
            if incomplete_tasks:
                suggestions.append(f"Continue working on {len(incomplete_tasks)} incomplete tasks")
        
        if 'handoff' in entity_types:
            # Check for conversations that need follow-up
            conversations = [e for e in recent_entities if e.get('type') == 'handoff']
            if conversations:
                suggestions.append("Review recent conversations for action items")
        
        if 'file' in entity_types:
            # Check for code that needs testing or documentation
            files = [e for e in recent_entities if e.get('type') == 'file']
            if files:
                suggestions.append("Add tests and documentation for recent code changes")
        
        return suggestions[:3]
    
    def _suggest_efficiency_improvements(self, recent_entities: List[Dict]) -> List[str]:
        """Suggest efficiency improvements based on activity patterns."""
        suggestions = []
        
        # Check for task switching patterns
        entity_types = [e.get('type') for e in recent_entities]
        if len(set(entity_types)) > 3:
            suggestions.append("Consider batching similar tasks to reduce context switching")
        
        # Check for overdue items
        overdue_count = 0
        for entity in recent_entities:
            if entity.get('type') == 'task':
                due_date = entity.get('metadata', {}).get('due_date')
                if due_date and datetime.now() > due_date:
                    overdue_count += 1
        
        if overdue_count > 0:
            suggestions.append(f"Review {overdue_count} overdue items and update deadlines")
        
        # Check for communication patterns
        conversations = [e for e in recent_entities if e.get('type') == 'handoff']
        if len(conversations) > 10:
            suggestions.append("Consider consolidating frequent communications into regular meetings")
        
        return suggestions[:3]
    
    def _suggest_collaboration_opportunities(self, recent_entities: List[Dict]) -> List[str]:
        """Suggest collaboration opportunities based on activity."""
        suggestions = []
        
        # Find people mentioned in recent activity
        people_mentioned = set()
        for entity in recent_entities:
            if entity.get('type') == 'handoff':
                related = self.memory.get_related(entity['id'])
                people = [r for r in related if r.get('type') == 'person']
                people_mentioned.update([p['id'] for p in people])
        
        if len(people_mentioned) > 2:
            suggestions.append("Schedule a team sync to align on recent work")
        
        # Check for shared projects
        projects = [e for e in recent_entities if e.get('type') == 'project']
        if projects:
            suggestions.append("Review project collaboration and share progress updates")
        
        # Check for code reviews needed
        files = [e for e in recent_entities if e.get('type') == 'file']
        if files:
            suggestions.append("Request code reviews for recent changes")
        
        return suggestions[:3] 