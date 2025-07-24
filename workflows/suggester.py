"""
Workflow Suggester

Analyzes usage patterns and proposes new automations based on user behavior.
Uses AI to identify repetitive patterns and suggest workflow improvements.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from emily_core import UnifiedMemoryStore

from .dsl import WorkflowDSL, EXAMPLE_WORKFLOWS

logger = logging.getLogger(__name__)


class WorkflowSuggester:
    """AI-powered workflow suggestion engine."""
    
    def __init__(self, memory_store: UnifiedMemoryStore):
        self.memory = memory_store
        self.dsl = WorkflowDSL()
        
    def analyze_patterns(self, time_range_days: int = 30) -> Dict[str, Any]:
        """Analyze user activity patterns to identify automation opportunities."""
        try:
            cutoff_date = datetime.now() - timedelta(days=time_range_days)
            
            # Get recent entities
            recent_entities = self._get_recent_entities(cutoff_date)
            
            # Analyze patterns
            patterns = {
                'entity_creation_patterns': self._analyze_entity_creation(recent_entities),
                'task_completion_patterns': self._analyze_task_completion(recent_entities),
                'conversation_patterns': self._analyze_conversation_patterns(recent_entities),
                'relation_patterns': self._analyze_relation_patterns(recent_entities),
                'temporal_patterns': self._analyze_temporal_patterns(recent_entities),
                'content_patterns': self._analyze_content_patterns(recent_entities)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to analyze patterns: {e}")
            return {}
    
    def generate_suggestions(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate workflow suggestions based on analyzed patterns."""
        suggestions = []
        
        try:
            # Task completion suggestions
            task_patterns = patterns.get('task_completion_patterns', {})
            if task_patterns.get('frequent_completion'):
                suggestions.append(self._suggest_task_completion_workflow(task_patterns))
            
            # Conversation follow-up suggestions
            conv_patterns = patterns.get('conversation_patterns', {})
            if conv_patterns.get('needs_follow_up'):
                suggestions.append(self._suggest_conversation_followup_workflow(conv_patterns))
            
            # Project management suggestions
            project_patterns = patterns.get('entity_creation_patterns', {}).get('project', {})
            if project_patterns.get('frequent_creation'):
                suggestions.append(self._suggest_project_setup_workflow(project_patterns))
            
            # Notification suggestions
            temporal_patterns = patterns.get('temporal_patterns', {})
            if temporal_patterns.get('regular_activity'):
                suggestions.append(self._suggest_reminder_workflow(temporal_patterns))
                suggestions.append(self._suggest_deadline_reminder_workflow(temporal_patterns))
            
            # Content organization suggestions
            content_patterns = patterns.get('content_patterns', {})
            if content_patterns.get('repetitive_content'):
                suggestions.append(self._suggest_content_organization_workflow(content_patterns))
            
            # Bug report suggestions (always include as a common pattern)
            suggestions.append(self._suggest_bug_report_workflow({}))
            
            # Code review suggestions (always include as a common pattern)
            suggestions.append(self._suggest_code_review_workflow({}))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []
    
    def _get_recent_entities(self, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Get entities created after the cutoff date."""
        try:
            # Get all entities and filter by date
            all_entities = self.memory.get_all_entities(limit=1000)
            recent_entities = []
            
            for entity in all_entities:
                try:
                    created_at = datetime.fromisoformat(entity.get('created_at', ''))
                    if created_at >= cutoff_date:
                        recent_entities.append(entity)
                except (ValueError, TypeError):
                    continue
            
            return recent_entities
            
        except Exception as e:
            logger.error(f"Failed to get recent entities: {e}")
            return []
    
    def _analyze_entity_creation(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in entity creation."""
        patterns = defaultdict(int)
        type_patterns = defaultdict(list)
        
        for entity in entities:
            entity_type = entity.get('type', 'unknown')
            patterns[entity_type] += 1
            type_patterns[entity_type].append(entity)
        
        # Identify frequent creation patterns
        frequent_types = {k: v for k, v in patterns.items() if v >= 3}
        
        return {
            'frequent_creation': frequent_types,
            'type_distribution': dict(patterns),
            'type_details': dict(type_patterns)
        }
    
    def _analyze_task_completion(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze task completion patterns."""
        task_entities = [e for e in entities if e.get('type') == 'task']
        
        if not task_entities:
            return {}
        
        completion_patterns = {
            'total_tasks': len(task_entities),
            'completed_tasks': 0,
            'pending_tasks': 0,
            'completion_rate': 0.0,
            'frequent_completion': False
        }
        
        for task in task_entities:
            status = task.get('metadata', {}).get('status', 'pending')
            if status == 'completed':
                completion_patterns['completed_tasks'] += 1
            else:
                completion_patterns['pending_tasks'] += 1
        
        if completion_patterns['total_tasks'] > 0:
            completion_patterns['completion_rate'] = (
                completion_patterns['completed_tasks'] / completion_patterns['total_tasks']
            )
            completion_patterns['frequent_completion'] = completion_patterns['total_tasks'] >= 5
        
        return completion_patterns
    
    def _analyze_conversation_patterns(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation and handoff patterns."""
        conv_entities = [e for e in entities if e.get('type') == 'handoff']
        
        if not conv_entities:
            return {}
        
        # Analyze conversation topics
        topics = []
        for conv in conv_entities:
            conv_topics = conv.get('metadata', {}).get('topics', [])
            if isinstance(conv_topics, list):
                topics.extend(conv_topics)
        
        topic_counter = Counter(topics)
        frequent_topics = {topic: count for topic, count in topic_counter.items() if count >= 2}
        
        # Check if conversations need follow-up
        needs_followup = len(conv_entities) >= 3 and len(frequent_topics) > 0
        
        return {
            'total_conversations': len(conv_entities),
            'frequent_topics': frequent_topics,
            'needs_follow_up': needs_followup,
            'topics_distribution': dict(topic_counter)
        }
    
    def _analyze_relation_patterns(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationship patterns between entities."""
        try:
            # Get recent relations
            all_relations = self.memory.get_relations_by_type('', limit=1000)
            
            relation_types = Counter()
            for relation in all_relations:
                relation_types[relation.relation_type] += 1
            
            frequent_relations = {k: v for k, v in relation_types.items() if v >= 3}
            
            return {
                'frequent_relation_types': frequent_relations,
                'relation_distribution': dict(relation_types)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze relation patterns: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in user activity."""
        if not entities:
            return {}
        
        # Group by hour of day
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for entity in entities:
            try:
                created_at = datetime.fromisoformat(entity.get('created_at', ''))
                hourly_activity[created_at.hour] += 1
                daily_activity[created_at.weekday()] += 1
            except (ValueError, TypeError):
                continue
        
        # Identify peak activity times
        peak_hours = [hour for hour, count in hourly_activity.items() if count >= 3]
        peak_days = [day for day, count in daily_activity.items() if count >= 3]
        
        return {
            'hourly_distribution': dict(hourly_activity),
            'daily_distribution': dict(daily_activity),
            'peak_hours': peak_hours,
            'peak_days': peak_days,
            'regular_activity': len(peak_hours) > 0 or len(peak_days) > 0
        }
    
    def _analyze_content_patterns(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content patterns for repetitive elements."""
        content_analysis = {
            'repetitive_content': False,
            'common_keywords': [],
            'content_lengths': []
        }
        
        if not entities:
            return content_analysis
        
        # Extract keywords from content
        all_content = []
        for entity in entities:
            content = entity.get('content', '')
            if content:
                all_content.append(content.lower())
        
        if all_content:
            # Simple keyword extraction (in a real implementation, use NLP)
            words = []
            for content in all_content:
                words.extend(content.split())
            
            word_counter = Counter(words)
            common_words = [word for word, count in word_counter.items() if count >= 3 and len(word) > 3]
            
            content_analysis['common_keywords'] = common_words[:10]
            content_analysis['repetitive_content'] = len(common_words) > 0
        
        return content_analysis
    
    def _suggest_task_completion_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for task completion automation."""
        return {
            'id': 'auto_task_completion',
            'name': 'Task Completion Automation',
            'description': 'Automatically update project status and notify stakeholders when tasks are completed',
            'confidence': 0.85,
            'reasoning': f"Found {patterns.get('total_tasks', 0)} tasks with {patterns.get('completion_rate', 0):.1%} completion rate",
            'workflow_yaml': EXAMPLE_WORKFLOWS['task_completion'],
            'category': 'task_management',
            'estimated_impact': 'high'
        }
    
    def _suggest_conversation_followup_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for conversation follow-up automation."""
        frequent_topics = patterns.get('frequent_topics', {})
        topics_list = list(frequent_topics.keys())[:3]
        
        return {
            'id': 'auto_conversation_followup',
            'name': 'Conversation Follow-up Automation',
            'description': f'Automatically create tasks and notify team for conversations about {", ".join(topics_list)}',
            'confidence': 0.80,
            'reasoning': f"Found {patterns.get('total_conversations', 0)} conversations with frequent topics: {topics_list}",
            'workflow_yaml': EXAMPLE_WORKFLOWS['meeting_followup'],
            'category': 'communication',
            'estimated_impact': 'medium'
        }
    
    def _suggest_project_setup_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for project setup automation."""
        return {
            'id': 'auto_project_setup',
            'name': 'Project Setup Automation',
            'description': 'Automatically create initial tasks and setup project structure when new projects are created',
            'confidence': 0.75,
            'reasoning': f"Found frequent project creation patterns",
            'workflow_yaml': """
id: project_setup
name: Project Setup Automation
description: Automatically setup new projects with initial tasks
trigger:
  type: entity_created
  filter:
    type: project
actions:
  - type: create_task
    params:
      title: "Project Setup - Define Requirements"
      priority: high
      content: "Define project requirements and scope"
  - type: create_task
    params:
      title: "Project Setup - Create Timeline"
      priority: medium
      content: "Create project timeline and milestones"
  - type: notify
    params:
      channel: console
      message: "New project '{{ entity.name }}' has been set up with initial tasks"
""",
            'category': 'project_management',
            'estimated_impact': 'high'
        }
    
    def _suggest_reminder_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for reminder automation."""
        peak_hours = patterns.get('peak_hours', [])
        peak_days = patterns.get('peak_days', [])
        
        schedule = "0 9 * * 1-5"  # Default to 9 AM weekdays
        if peak_hours:
            schedule = f"0 {peak_hours[0]} * * 1-5"
        
        return {
            'id': 'auto_reminder',
            'name': 'Activity Reminder',
            'description': f'Send reminders during peak activity hours ({peak_hours[0] if peak_hours else 9}:00)',
            'confidence': 0.70,
            'reasoning': f"Detected peak activity at hours: {peak_hours}, days: {peak_days}",
            'workflow_yaml': EXAMPLE_WORKFLOWS['daily_standup'],
            'category': 'productivity',
            'estimated_impact': 'medium'
        }
    
    def _suggest_content_organization_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for content organization automation."""
        common_keywords = patterns.get('common_keywords', [])
        
        return {
            'id': 'auto_content_organization',
            'name': 'Content Organization',
            'description': f'Automatically tag and organize content based on common keywords: {", ".join(common_keywords[:3])}',
            'confidence': 0.65,
            'reasoning': f"Found {len(common_keywords)} common keywords in content",
            'workflow_yaml': """
id: content_organization
name: Content Organization
description: Automatically tag and organize content
trigger:
  type: entity_created
  filter:
    type: handoff
actions:
  - type: update_entity
    params:
      entity_id: "{{ entity.id }}"
      metadata:
        auto_tagged: true
        keywords: "{{ common_keywords }}"
  - type: notify
    params:
      channel: console
      message: "Content automatically tagged with keywords"
""",
            'category': 'content_management',
            'estimated_impact': 'low'
        }
    
    def _suggest_bug_report_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for bug report automation."""
        return {
            'id': 'auto_bug_report',
            'name': 'Bug Report Automation',
            'description': 'Automatically create tasks for bug reports and issues',
            'confidence': 0.75,
            'reasoning': "Based on common bug reporting patterns",
            'workflow_yaml': EXAMPLE_WORKFLOWS['bug_report'],
            'category': 'issue_management',
            'estimated_impact': 'high'
        }
    
    def _suggest_code_review_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for code review automation."""
        return {
            'id': 'auto_code_review',
            'name': 'Code Review Automation',
            'description': 'Automatically create tasks for code reviews',
            'confidence': 0.70,
            'reasoning': "Based on code review patterns",
            'workflow_yaml': EXAMPLE_WORKFLOWS['code_review'],
            'category': 'development',
            'estimated_impact': 'medium'
        }
    
    def _suggest_deadline_reminder_workflow(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest workflow for deadline reminder automation."""
        return {
            'id': 'auto_deadline_reminder',
            'name': 'Deadline Reminder Automation',
            'description': 'Send reminders for upcoming deadlines',
            'confidence': 0.85,
            'reasoning': "Based on temporal activity patterns",
            'workflow_yaml': EXAMPLE_WORKFLOWS['deadline_reminder'],
            'category': 'productivity',
            'estimated_impact': 'medium'
        }
    
    def get_suggestion_by_id(self, suggestion_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific suggestion by ID."""
        patterns = self.analyze_patterns()
        suggestions = self.generate_suggestions(patterns)
        
        for suggestion in suggestions:
            if suggestion['id'] == suggestion_id:
                return suggestion
        
        return None
    
    def suggest_workflows(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get workflow suggestions based on a query."""
        try:
            # Analyze patterns first
            patterns = self.analyze_patterns()
            
            # Generate suggestions
            suggestions = self.generate_suggestions(patterns)
            
            # Filter by query if provided
            if query:
                filtered_suggestions = []
                query_lower = query.lower()
                for suggestion in suggestions:
                    if (query_lower in suggestion['name'].lower() or 
                        query_lower in suggestion['description'].lower() or
                        query_lower in suggestion['category'].lower()):
                        filtered_suggestions.append(suggestion)
                suggestions = filtered_suggestions
            
            # Limit results
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to suggest workflows: {e}")
            return []
    
    def approve_suggestion(self, suggestion_id: str) -> bool:
        """Approve a workflow suggestion and optionally register it."""
        try:
            suggestion = self.get_suggestion_by_id(suggestion_id)
            if suggestion:
                # For now, just mark as approved
                # In a full implementation, you might want to:
                # 1. Parse the workflow YAML
                # 2. Register it with the workflow engine
                # 3. Store approval metadata
                logger.info(f"Approved workflow suggestion: {suggestion_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to approve suggestion {suggestion_id}: {e}")
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics about workflow suggestions."""
        try:
            patterns = self.analyze_patterns()
            suggestions = self.generate_suggestions(patterns)
            
            return {
                'total_suggestions': len(suggestions),
                'suggestions_by_category': self._group_suggestions_by_category(suggestions),
                'average_confidence': sum(s['confidence'] for s in suggestions) / len(suggestions) if suggestions else 0,
                'high_impact_suggestions': len([s for s in suggestions if s['estimated_impact'] == 'high']),
                'patterns_analyzed': list(patterns.keys()) if patterns else []
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {}
    
    def _group_suggestions_by_category(self, suggestions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group suggestions by category."""
        categories = defaultdict(int)
        for suggestion in suggestions:
            categories[suggestion['category']] += 1
        return dict(categories) 