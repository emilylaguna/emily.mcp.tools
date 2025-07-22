"""
Workflow DSL Parser

Parses YAML workflow definitions and converts them to Workflow objects.
Supports validation and template resolution.
"""

import re
import yaml
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from .engine import Workflow, WorkflowAction, WorkflowTrigger

logger = logging.getLogger(__name__)


class WorkflowDSL:
    """YAML-based workflow definition language parser."""
    
    def __init__(self):
        self.supported_action_types = {
            'create_task', 'update_entity', 'save_relation', 
            'notify', 'run_shell', 'http_request'
        }
        self.supported_trigger_types = {
            'entity_created', 'entity_updated', 'relation_created', 
            'scheduled', 'manual'
        }
    
    def parse_yaml(self, yaml_content: str) -> Workflow:
        """Parse YAML workflow definition into a Workflow object."""
        try:
            # Parse YAML
            data = yaml.safe_load(yaml_content)
            if not data:
                raise ValueError("Empty YAML content")
            
            # Validate required fields
            required_fields = ['id', 'name', 'trigger', 'actions']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse trigger
            trigger = self._parse_trigger(data['trigger'])
            
            # Parse actions
            actions = self._parse_actions(data['actions'])
            
            # Create workflow
            workflow = Workflow(
                id=data['id'],
                name=data['name'],
                description=data.get('description', ''),
                trigger=trigger,
                actions=actions,
                enabled=data.get('enabled', True)
            )
            
            return workflow
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
        except Exception as e:
            raise ValueError(f"Failed to parse workflow: {e}")
    
    def _parse_trigger(self, trigger_data: Dict[str, Any]) -> WorkflowTrigger:
        """Parse trigger definition."""
        if not isinstance(trigger_data, dict):
            raise ValueError("Trigger must be a dictionary")
        
        trigger_type = trigger_data.get('type')
        if not trigger_type:
            raise ValueError("Trigger type is required")
        
        if trigger_type not in self.supported_trigger_types:
            raise ValueError(f"Unsupported trigger type: {trigger_type}")
        
        return WorkflowTrigger(
            type=trigger_type,
            filter=trigger_data.get('filter'),
            schedule=trigger_data.get('schedule')
        )
    
    def _parse_actions(self, actions_data: List[Dict[str, Any]]) -> List[WorkflowAction]:
        """Parse action definitions."""
        if not isinstance(actions_data, list):
            raise ValueError("Actions must be a list")
        
        actions = []
        for i, action_data in enumerate(actions_data):
            if not isinstance(action_data, dict):
                raise ValueError(f"Action {i} must be a dictionary")
            
            action_type = action_data.get('type')
            if not action_type:
                raise ValueError(f"Action {i} type is required")
            
            if action_type not in self.supported_action_types:
                raise ValueError(f"Unsupported action type: {action_type}")
            
            action = WorkflowAction(
                type=action_type,
                params=action_data.get('params', {}),
                condition=action_data.get('condition')
            )
            actions.append(action)
        
        return actions
    
    def validate_workflow(self, workflow: Workflow) -> List[str]:
        """Validate a workflow definition and return list of errors."""
        errors = []
        
        # Validate trigger
        if workflow.trigger.type not in self.supported_trigger_types:
            errors.append(f"Unsupported trigger type: {workflow.trigger.type}")
        
        # Validate actions
        for i, action in enumerate(workflow.actions):
            if action.type not in self.supported_action_types:
                errors.append(f"Action {i}: Unsupported action type: {action.type}")
            
            # Validate action-specific parameters
            action_errors = self._validate_action_params(action, i)
            errors.extend(action_errors)
        
        return errors
    
    def _validate_action_params(self, action: WorkflowAction, action_index: int) -> List[str]:
        """Validate action-specific parameters."""
        errors = []
        
        if action.type == 'create_task':
            required_params = ['title']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for create_task")
        
        elif action.type == 'update_entity':
            required_params = ['entity_id']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for update_entity")
        
        elif action.type == 'save_relation':
            required_params = ['source_id', 'target_id', 'relation_type']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for save_relation")
        
        elif action.type == 'notify':
            required_params = ['message']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for notify")
        
        elif action.type == 'run_shell':
            required_params = ['command']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for run_shell")
        
        elif action.type == 'http_request':
            required_params = ['url']
            for param in required_params:
                if param not in action.params:
                    errors.append(f"Action {action_index}: Missing required parameter '{param}' for http_request")
        
        return errors
    
    def resolve_templates(self, workflow: Workflow, context: Dict[str, Any]) -> Workflow:
        """Resolve template variables in workflow parameters."""
        resolved_workflow = workflow.model_copy()
        
        # Resolve trigger filter templates
        if resolved_workflow.trigger.filter:
            resolved_workflow.trigger.filter = self._resolve_dict_templates(
                resolved_workflow.trigger.filter, context
            )
        
        # Resolve action parameter templates
        for action in resolved_workflow.actions:
            action.params = self._resolve_dict_templates(action.params, context)
            if action.condition:
                action.condition = self._resolve_template_string(action.condition, context)
        
        return resolved_workflow
    
    def _resolve_dict_templates(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve templates in a dictionary."""
        resolved = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                resolved[key] = self._resolve_template_string(value, context)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_dict_templates(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_dict_templates(item, context) if isinstance(item, dict)
                    else self._resolve_template_string(item, context) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                resolved[key] = value
        
        return resolved
    
    def _resolve_template_string(self, template: str, context: Dict[str, Any]) -> str:
        """Resolve template variables in a string."""
        def replace_var(match):
            var_path = match.group(1)
            try:
                # Handle nested paths like "entity.metadata.status"
                value = context
                for part in var_path.split('.'):
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                logger.warning(f"Template variable not found: {var_path}")
                return match.group(0)  # Return original if not found
        
        # Replace {{ variable }} patterns
        return re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_var, template)
    
    def to_yaml(self, workflow: Workflow) -> str:
        """Convert a Workflow object back to YAML."""
        data = {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'enabled': workflow.enabled,
            'trigger': {
                'type': workflow.trigger.type,
                'filter': workflow.trigger.filter,
                'schedule': workflow.trigger.schedule
            },
            'actions': [
                {
                    'type': action.type,
                    'params': action.params,
                    'condition': action.condition
                }
                for action in workflow.actions
            ]
        }
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False)


# Example workflow definitions
EXAMPLE_WORKFLOWS = {
    'pr_follow_up': """
id: pr_follow_up
name: PR Follow-up Automation
description: Automatically create tasks and notify team when PR discussions are created
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["pull request"]
actions:
  - type: create_task
    params:
      title: "Review PR related to {{ entity.metadata.pr_number }}"
      priority: high
      content: "Follow up on PR discussion: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "New discussion about PR {{ entity.metadata.pr_number }} needs review."
""",

    'task_completion': """
id: task_completion
name: Task Completion Workflow
description: Automatically update project status when tasks are completed
trigger:
  type: entity_updated
  filter:
    type: task
    metadata.status: "completed"
actions:
  - type: update_entity
    params:
      entity_id: "{{ entity.metadata.project_id }}"
      metadata:
        last_task_completed: "{{ entity.updated_at }}"
  - type: notify
    params:
      channel: email
      message: "Task '{{ entity.name }}' has been completed!"
""",

    'daily_standup': """
id: daily_standup
name: Daily Standup Reminder
description: Send daily standup reminders
trigger:
  type: scheduled
  schedule: "0 9 * * 1-5"  # 9 AM on weekdays
actions:
  - type: notify
    params:
      channel: slack
      message: "Time for daily standup! Please update your task status."
  - type: create_task
    params:
      title: "Daily Standup - {{ datetime.now().strftime('%Y-%m-%d') }}"
      priority: medium
      content: "Daily team synchronization meeting"
""",

    'meeting_followup': """
id: meeting_followup
name: Meeting Follow-up Automation
description: Create action items from meeting notes
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["meeting", "discussion"]
actions:
  - type: create_task
    params:
      title: "Follow up on meeting: {{ entity.name }}"
      priority: medium
      content: "Action items from meeting: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "Meeting follow-up task created: {{ entity.name }}"
""",

    'bug_report': """
id: bug_report
name: Bug Report Automation
description: Automatically create tasks for bug reports
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["bug", "issue", "error"]
actions:
  - type: create_task
    params:
      title: "Investigate bug: {{ entity.name }}"
      priority: high
      content: "Bug report: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "New bug report requires investigation: {{ entity.name }}"
""",

    'project_setup': """
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
      content: "Define project requirements and scope for {{ entity.name }}"
  - type: create_task
    params:
      title: "Project Setup - Create Timeline"
      priority: medium
      content: "Create project timeline and milestones for {{ entity.name }}"
  - type: notify
    params:
      channel: slack
      message: "New project '{{ entity.name }}' has been set up with initial tasks"
""",

    'code_review': """
id: code_review
name: Code Review Automation
description: Automatically create tasks for code reviews
trigger:
  type: entity_created
  filter:
    type: handoff
    metadata.topics: ["code review", "review"]
actions:
  - type: create_task
    params:
      title: "Code Review: {{ entity.name }}"
      priority: medium
      content: "Code review request: {{ entity.content }}"
  - type: notify
    params:
      channel: slack
      message: "Code review task created: {{ entity.name }}"
""",

    'deadline_reminder': """
id: deadline_reminder
name: Deadline Reminder Automation
description: Send reminders for upcoming deadlines
trigger:
  type: scheduled
  schedule: "0 10 * * 1-5"  # 10 AM on weekdays
actions:
  - type: notify
    params:
      channel: slack
      message: "Check for upcoming deadlines and update task status"
  - type: create_task
    params:
      title: "Review Upcoming Deadlines"
      priority: medium
      content: "Review and update status of tasks with upcoming deadlines"
"""
} 