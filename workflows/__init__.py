"""
Workflow and automation functionality for Emily.Tools.

This package contains workflow engines, actions, DSL, and suggestion systems.
"""

from .engine import WorkflowEngine
from .actions import WorkflowActionExecutor, ActionResult
from .dsl import WorkflowDSL
from .suggester import WorkflowSuggester

__all__ = [
    'WorkflowEngine',
    'WorkflowActionExecutor',
    'ActionResult', 
    'WorkflowDSL',
    'WorkflowSuggester'
] 