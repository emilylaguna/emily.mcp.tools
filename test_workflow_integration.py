#!/usr/bin/env python3
"""
Workflow Integration Test Suite

A comprehensive test file for experimenting with and testing the workflow 
trigger and filter system. You can run this file directly and modify it
to test your own scenarios.

Usage:
    python test_workflow_integration.py
    
Or run specific test categories:
    python test_workflow_integration.py --basic
    python test_workflow_integration.py --filters  
    python test_workflow_integration.py --templates
    python test_workflow_integration.py --custom
    
Options:
    --debug     Enable debug logging (shows all workflow details)
    --quiet     Minimal output (just test results)
"""

import asyncio
import json
import logging
import tempfile
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any

import coloredlogs
coloredlogs.install(level='DEBUG')

# Setup clean logging
# logging.basicConfig(
#     level=logging.WARNING,  # Suppress most library logs
#     format='%(message)s'    # Clean format
# )

# Suppress noisy external libraries
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR) 
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('huggingface_hub').setLevel(logging.ERROR)
logging.getLogger('filelock').setLevel(logging.ERROR)

# Set our loggers to INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import the workflow system
try:
    from core import UnifiedMemoryStore
    from workflows.engine import WorkflowEngine, Workflow, WorkflowTrigger, WorkflowAction, Event
    from core.models import MemoryEntity, MemoryRelation
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the emily.mcp.tools directory")
    exit(1)


class WorkflowTestSuite:
    """Comprehensive test suite for workflow triggers and filters."""
    
    def __init__(self, debug: bool = False, quiet: bool = False):
        self.debug = debug
        self.quiet = quiet
        
        # Suppress additional logs if not in debug mode
        if not debug:
            logging.getLogger('workflows.engine').setLevel(logging.WARNING)
            logging.getLogger('core.memory').setLevel(logging.WARNING)
            logging.getLogger('intelligence.ai_extraction').setLevel(logging.ERROR)
            logging.getLogger('core.database').setLevel(logging.ERROR)
        else:
            logging.getLogger('workflows.engine').setLevel(logging.DEBUG)
            logging.getLogger('core.memory').setLevel(logging.DEBUG)
        
        # Disable tqdm progress bars unless debug mode
        import os
        if not debug:
            os.environ['TQDM_DISABLE'] = '1'
        
        if not quiet:
            print("🔧 Initializing test environment...")
        
        # Create temporary test environment  
        self.temp_dir = tempfile.mkdtemp()
        self.memory_store = UnifiedMemoryStore(Path(self.temp_dir) / 'test.db')
        self.workflow_engine = WorkflowEngine(self.memory_store)
        self.memory_store.workflow_engine = self.workflow_engine
        
        # Test tracking
        self.test_results = []
        
        if not quiet:
            print(f"✅ Test environment ready!")
            print()
    
    def log_test(self, name: str, success: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        if not self.quiet:
            if message:
                print(f"   {status} {name} - {message}")
            else:
                print(f"   {status} {name}")
        self.test_results.append({
            "name": name,
            "success": success,
            "message": message
        })
    
    def create_test_workflow(self, workflow_id: str, name: str, trigger_type: str, 
                           filter_dict: Dict[str, Any] = None, 
                           action_type: str = "create_task") -> Workflow:
        """Helper to create test workflows."""
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=f"Test workflow: {name}",
            trigger=WorkflowTrigger(
                type=trigger_type,
                filter=filter_dict
            ),
            actions=[
                WorkflowAction(
                    type=action_type,
                    params={
                        "title": f"Auto-created by {name}: {{{{ entity.name }}}}",
                        "content": "Test task created by workflow: {{{{ entity.content }}}}"
                    }
                )
            ]
        )
        
        self.workflow_engine.register_workflow(workflow)
        return workflow
    
    def create_test_entity(self, entity_type: str, name: str, content: str = "", 
                          metadata: Dict[str, Any] = None, tags: List[str] = None) -> MemoryEntity:
        """Helper to create test entities."""
        entity = MemoryEntity(
            type=entity_type,
            name=name,
            content=content,
            metadata=metadata or {},
            tags=tags or []
        )
        
        return self.memory_store.save_entity(entity)
    
    def wait_for_workflows(self, timeout: float = 2.0):
        """Wait for workflows to complete execution."""
        if self.quiet:
            # Show progress dot in quiet mode
            print(".", end="", flush=True)
        time.sleep(timeout)
    
    def count_tasks_created(self, search_term: str = "Auto-created") -> int:
        """Count tasks created by workflows."""
        tasks = self.memory_store.search_entities(entity_type="task", limit=100)
        matching_tasks = [t for t in tasks if search_term in t.name]
        return len(matching_tasks)
    
    def run_basic_tests(self):
        """Test basic workflow functionality."""
        if not self.quiet:
            print("🚀 Running Basic Workflow Tests")
        
        # Test 1: Simple entity type filter
        try:
            self.create_test_workflow(
                workflow_id="test-note-workflow",
                name="Note to Task Converter",
                trigger_type="entity_created",
                filter_dict={"entity.type": "note"}
            )
            
            initial_tasks = self.count_tasks_created()
            
            self.create_test_entity(
                entity_type="note",
                name="Important Meeting Notes",
                content="Discussed project timeline and deliverables"
            )
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created()
            success = final_tasks > initial_tasks
            
            self.log_test(
                "Basic Entity Type Filter",
                success,
                f"Created {final_tasks - initial_tasks} tasks"
            )
            
        except Exception as e:
            self.log_test("Basic Entity Type Filter", False, f"Error: {e}")
        
        # Test 2: No filter (should trigger on any entity)
        try:
            self.create_test_workflow(
                workflow_id="test-any-entity",
                name="Any Entity Tracker",
                trigger_type="entity_created",
                filter_dict=None  # No filter
            )
            
            initial_tasks = self.count_tasks_created("Any Entity Tracker")
            
            self.create_test_entity(
                entity_type="person",
                name="John Doe",
                content="Senior developer"
            )
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created("Any Entity Tracker")
            success = final_tasks > initial_tasks
            
            self.log_test(
                "No Filter (Match All)",
                success,
                f"Created {final_tasks - initial_tasks} tasks"
            )
            
        except Exception as e:
            self.log_test("No Filter (Match All)", False, f"Error: {e}")
    
    def run_filter_tests(self):
        """Test advanced filter functionality."""
        if not self.quiet:
            print("🎯 Running Advanced Filter Tests")
        
        # Test 1: Nested metadata filter
        try:
            self.create_test_workflow(
                workflow_id="test-high-priority",
                name="High Priority Handler",
                trigger_type="entity_created",
                filter_dict={
                    "entity.type": "handoff",
                    "entity.metadata.priority": "high"
                }
            )
            
            initial_tasks = self.count_tasks_created("High Priority Handler")
            
            # Should trigger
            self.create_test_entity(
                entity_type="handoff",
                name="Critical Bug Report",
                content="Production system is down",
                metadata={"priority": "high", "severity": "critical"}
            )
            
            # Should NOT trigger (wrong priority)
            self.create_test_entity(
                entity_type="handoff", 
                name="Regular Update",
                content="Weekly status update",
                metadata={"priority": "medium"}
            )
            
            # Should NOT trigger (wrong type)
            self.create_test_entity(
                entity_type="note",
                name="High Priority Note",
                metadata={"priority": "high"}
            )
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created("High Priority Handler")
            created_tasks = final_tasks - initial_tasks
            success = created_tasks == 1  # Should only trigger once
            
            self.log_test(
                "Nested Metadata Filter",
                success,
                f"Created {created_tasks} tasks (expected 1)"
            )
            
        except Exception as e:
            self.log_test("Nested Metadata Filter", False, f"Error: {e}")
        
        # Test 2: Tag list matching
        try:
            self.create_test_workflow(
                workflow_id="test-urgent-tags",
                name="Urgent Tag Handler", 
                trigger_type="entity_created",
                filter_dict={
                    "entity.type": "task",
                    "entity.tags": ["urgent", "critical"]
                }
            )
            
            initial_tasks = self.count_tasks_created("Urgent Tag Handler")
            
            # Should trigger (has "urgent" tag)
            self.create_test_entity(
                entity_type="task",
                name="Fix Login Bug",
                tags=["frontend", "urgent", "bug"]
            )
            
            # Should trigger (has "critical" tag)
            self.create_test_entity(
                entity_type="task",
                name="Database Migration",
                tags=["backend", "critical", "database"]
            )
            
            # Should NOT trigger (no matching tags)
            self.create_test_entity(
                entity_type="task",
                name="Regular Task",
                tags=["feature", "low-priority"]
            )
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created("Urgent Tag Handler")
            created_tasks = final_tasks - initial_tasks
            success = created_tasks == 2  # Should trigger twice
            
            self.log_test(
                "Tag List Matching",
                success,
                f"Created {created_tasks} tasks (expected 2)"
            )
            
        except Exception as e:
            self.log_test("Tag List Matching", False, f"Error: {e}")
        
        # Test 3: Complex multi-condition filter
        try:
            self.create_test_workflow(
                workflow_id="test-complex-filter",
                name="Complex Filter Handler",
                trigger_type="entity_updated",
                filter_dict={
                    "entity.type": "task",
                    "entity.metadata.status": "completed",
                    "entity.metadata.project_id": "project-123"
                }
            )
            
            initial_tasks = self.count_tasks_created("Complex Filter Handler")
            
            # Create initial task
            test_task = self.create_test_entity(
                entity_type="task",
                name="Test Task",
                metadata={"status": "todo", "project_id": "project-123"}
            )
            
            # Update to completed (should trigger)
            test_task.metadata["status"] = "completed"
            self.memory_store.save_entity(test_task)
            
            # Create completed task in different project (should NOT trigger)
            other_task = self.create_test_entity(
                entity_type="task",
                name="Other Task",
                metadata={"status": "todo", "project_id": "project-456"}
            )
            other_task.metadata["status"] = "completed"
            self.memory_store.save_entity(other_task)
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created("Complex Filter Handler")
            created_tasks = final_tasks - initial_tasks
            success = created_tasks == 1  # Should trigger once
            
            self.log_test(
                "Complex Multi-Condition Filter",
                success,
                f"Created {created_tasks} tasks (expected 1)"
            )
            
        except Exception as e:
            self.log_test("Complex Multi-Condition Filter", False, f"Error: {e}")
    
    def run_template_tests(self):
        """Test template variable resolution."""
        if not self.quiet:
            print("📝 Running Template Variable Tests")
        
        try:
            # Create workflow with various template variables
            workflow = Workflow(
                id="template-test",
                name="Template Test Workflow",
                description="Test template variable resolution",
                trigger=WorkflowTrigger(
                    type="entity_created",
                    filter={"entity.type": "project"}
                ),
                actions=[
                    WorkflowAction(
                        type="create_task",
                        params={
                            "title": "Project: {{ entity.name }}",
                            "content": "Description: {{ entity.content }}\nPriority: {{ entity.metadata.priority | default('medium') }}\nCreated: {{ entity.created_at }}",
                            "priority": "{{ entity.metadata.priority | default('medium') }}",
                            "tags": ["auto-created", "{{ entity.type }}"]
                        }
                    )
                ]
            )
            
            self.workflow_engine.register_workflow(workflow)
            
            # Create test entity with metadata
            self.create_test_entity(
                entity_type="project",
                name="Web Application",
                content="Full-stack web application development",
                metadata={"priority": "high", "deadline": "2024-03-15"}
            )
            
            self.wait_for_workflows()
            
            # Check if task was created with resolved templates
            tasks = self.memory_store.search_entities(entity_type="task", limit=100)
            template_tasks = [t for t in tasks if "Project: Web Application" in t.name]
            
            success = len(template_tasks) > 0
            if success and template_tasks:
                task = template_tasks[0]
                has_content = "Description: Full-stack web application development" in task.content
                has_priority = task.metadata.get("priority") == "high"
                success = has_content and has_priority

                message = f"Task created with title: '{task.name}'"
                if has_content and has_priority:
                    message += " - Templates resolved correctly"
                else:
                    message += f" - Template issues: content={has_content}, priority={has_priority}"
            else:
                message = "No tasks created"
            
            self.log_test("Template Variable Resolution", success, message)
            
        except Exception as e:
            self.log_test("Template Variable Resolution", False, f"Error: {e}")
    
    def run_relation_tests(self):
        """Test relation-based workflows."""
        if not self.quiet:
            print("🔗 Running Relation Tests")
        
        try:
            # Create workflow that triggers on relation creation
            self.create_test_workflow(
                workflow_id="test-relation-workflow",
                name="Relation Handler",
                trigger_type="relation_created",
                filter_dict={"relation.relation_type": "depends_on"}
            )
            
            initial_tasks = self.count_tasks_created("Relation Handler")
            
            # Create entities
            task1 = self.create_test_entity(
                entity_type="task",
                name="Setup Database",
                content="Initialize database schema"
            )
            
            task2 = self.create_test_entity(
                entity_type="task", 
                name="Implement Authentication",
                content="Add user authentication system"
            )
            
            # Create relation (should trigger workflow)
            relation = MemoryRelation(
                source_id=task2.id,
                target_id=task1.id,
                relation_type="depends_on",
                strength=0.8
            )
            
            self.memory_store.save_relation(relation)
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created("Relation Handler")
            created_tasks = final_tasks - initial_tasks
            success = created_tasks > 0
            
            self.log_test(
                "Relation-Based Workflow",
                success,
                f"Created {created_tasks} tasks"
            )
            
        except Exception as e:
            self.log_test("Relation-Based Workflow", False, f"Error: {e}")
    
    def run_custom_tests(self):
        """Add your own custom tests here."""
        if not self.quiet:
            print("🧪 Running Custom Tests")
        
        # Example custom test - modify this section for your own tests
        try:
            # Test: Workflow with condition
            workflow = Workflow(
                id="conditional-test",
                name="Conditional Test",
                description="Test workflow with action conditions",
                trigger=WorkflowTrigger(
                    type="entity_created",
                    filter={"entity.type": "handoff"}
                ),
                actions=[
                    WorkflowAction(
                        type="create_task",
                        params={
                            "title": "HIGH PRIORITY: {{ entity.name }}",
                            "priority": "high"
                        },
                        condition="{{ entity.metadata.priority == 'critical' }}"
                    ),
                    WorkflowAction(
                        type="create_task", 
                        params={
                            "title": "Regular: {{ entity.name }}",
                            "priority": "medium"
                        },
                        condition="{{ entity.metadata.priority != 'critical' }}"
                    )
                ]
            )
            
            self.workflow_engine.register_workflow(workflow)
            
            initial_tasks = self.count_tasks_created()
            
            # Critical handoff (should create high priority task)
            self.create_test_entity(
                entity_type="handoff",
                name="Critical Issue",
                metadata={"priority": "critical"}
            )
            
            # Regular handoff (should create medium priority task)
            self.create_test_entity(
                entity_type="handoff",
                name="Regular Issue", 
                metadata={"priority": "low"}
            )
            
            self.wait_for_workflows()
            
            final_tasks = self.count_tasks_created()
            created_tasks = final_tasks - initial_tasks
            
            # Check task priorities
            recent_tasks = self.memory_store.search_entities(entity_type="task", limit=10)
            high_priority_tasks = [t for t in recent_tasks if t.name.startswith("HIGH PRIORITY")]
            regular_tasks = [t for t in recent_tasks if t.name.startswith("Regular")]
            
            success = len(high_priority_tasks) == 1 and len(regular_tasks) == 1
            
            self.log_test(
                "Conditional Actions",
                success,
                f"Created {len(high_priority_tasks)} high priority and {len(regular_tasks)} regular tasks"
            )
            
        except Exception as e:
            self.log_test("Conditional Actions", False, f"Error: {e}")
        
        # Add more custom tests here...
        # Example:
        # self.test_my_specific_scenario()
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("🧪 WORKFLOW INTEGRATION TEST RESULTS")
        print("="*60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        print(f"Tests passed: {passed}/{total}")
        print(f"Success rate: {passed/total*100:.1f}%")
        print()
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}")
            if result["message"]:
                print(f"   {result['message']}")
        
        print("\n" + "="*60)
        
        if passed == total:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total - passed} tests failed")
        
        print("="*60)
    
    def run_all_tests(self):
        """Run all test suites."""
        if not self.quiet:
            print("🧪 WORKFLOW INTEGRATION TESTS")
            print("=" * 50)
            print()
        
        self.run_basic_tests()
        if not self.quiet: print()
        
        self.run_filter_tests()
        if not self.quiet: print()
        
        self.run_template_tests()
        if not self.quiet: print()
        
        self.run_relation_tests()
        if not self.quiet: print()
        
        self.run_custom_tests()
        if not self.quiet: print()
        
        self.print_summary()


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Workflow Integration Tests")
    parser.add_argument("--basic", action="store_true", help="Run basic tests only")
    parser.add_argument("--filters", action="store_true", help="Run filter tests only")
    parser.add_argument("--templates", action="store_true", help="Run template tests only")
    parser.add_argument("--relations", action="store_true", help="Run relation tests only")
    parser.add_argument("--custom", action="store_true", help="Run custom tests only")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--quiet", action="store_true", help="Minimal output (just results)")
    
    args = parser.parse_args()
    
    suite = WorkflowTestSuite(debug=args.debug, quiet=args.quiet)
    
    if args.basic:
        suite.run_basic_tests()
    elif args.filters:
        suite.run_filter_tests()
    elif args.templates:
        suite.run_template_tests()
    elif args.relations:
        suite.run_relation_tests()
    elif args.custom:
        suite.run_custom_tests()
    else:
        suite.run_all_tests()
    
    if not (args.basic or args.filters or args.templates or args.relations or args.custom):
        suite.print_summary()


if __name__ == "__main__":
    main() 