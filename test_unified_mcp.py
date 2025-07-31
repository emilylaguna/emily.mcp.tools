#!/usr/bin/env python3
"""
Comprehensive test suite for the unified.py MCP server.
Tests all available tools from the server-info.json file.
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastmcp import Client
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UnifiedMCPTester:
    
    """Test suite for the unified.py MCP server."""
    def __init__(self, client: Client):
        self.client = client
        self.test_results = []

    async def test_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a specific tool and return the result."""
        if parameters is None:
            parameters = {}
            
        try:
            logger.info(f"Testing tool: {tool_name}")
            start_time = time.time()
            
            result = await self.client.call_tool("call_tool", {
                "tool_name": tool_name,
                "parameters": parameters
            })
            
            end_time = time.time()
            duration = end_time - start_time
            
            test_result = {
                "tool_name": tool_name,
                "success": True,
                "duration": duration,
                "result": result.data,
                "error": None
            }
            
            logger.info(f"✓ {tool_name} completed in {duration:.2f}s")
            return test_result
            
        except Exception as e:
            test_result = {
                "tool_name": tool_name,
                "success": False,
                "duration": 0,
                "result": None,
                "error": str(e)
            }
            
            logger.error(f"✗ {tool_name} failed: {e}")
            return test_result
    
    async def test_list_available_tools(self):
        """Test the list_available_tools function."""
        try:
            logger.info("Testing list_available_tools")
            result = await self.client.call_tool("list_available_tools", {})
            tools = result.data
            
            logger.info(f"✓ Found {len(tools)} available tools")
            return {
                "tool_name": "list_available_tools",
                "success": True,
                "tools_count": len(tools),
                "tools": tools,
                "error": None
            }
        except Exception as e:
            logger.error(f"✗ list_available_tools failed: {e}")
            return {
                "tool_name": "list_available_tools",
                "success": False,
                "tools_count": 0,
                "tools": [],
                "error": str(e)
            }
    
    async def test_todo_tools(self):
        """Test todo-related tools."""
        logger.info("=== Testing Todo Tools ===")
        
        # Test data for todo operations
        test_area = {
            "name": "Test Area",
            "description": "Test area for MCP testing"
        }
        
        test_project = {
            "name": "Test Project",
            "description": "Test project for MCP testing"
        }
        
        test_task = {
            "title": "Test Task",
            "description": "Test task for MCP testing",
            "priority": "medium",
            "energy_level": "medium"
        }
        
        # Test area creation
        area_result = await self.test_tool("todo_create_area", test_area)
        self.test_results.append(area_result)
        
        if area_result["success"]:
            area_id = area_result["result"].get("id")
            
            # Test project creation with area
            project_params = {**test_project, "area_id": area_id}
            project_result = await self.test_tool("todo_create_project", project_params)
            self.test_results.append(project_result)
            
            if project_result["success"]:
                project_id = project_result["result"].get("id")
                
                # Test task creation with project
                task_params = {**test_task, "project_id": project_id}
                task_result = await self.test_tool("todo_create_task", task_params)
                self.test_results.append(task_result)
                
                if task_result["success"]:
                    task_id = task_result["result"].get("id")
                    
                    # Test task update
                    update_result = await self.test_tool("todo_update_task", {
                        "task_id": task_id,
                        "priority": "high"
                    })
                    self.test_results.append(update_result)
                    
                    # Test task completion
                    complete_result = await self.test_tool("todo_complete_task", {
                        "task_id": task_id
                    })
                    self.test_results.append(complete_result)
        
        # Test read-only todo tools
        read_tools = [
            ("todo_get_today", {}),
            ("todo_get_evening", {}),
            ("todo_get_upcoming", {"days": 7}),
            ("todo_get_anytime", {}),
            ("todo_get_someday", {}),
            ("todo_list_areas", {}),
            ("todo_list_projects", {}),
            ("todo_suggest_priorities", {}),
            ("todo_get_statistics", {}),
        ]
        
        for tool_name, params in read_tools:
            result = await self.test_tool(tool_name, params)
            self.test_results.append(result)
    
    async def test_handoff_tools(self):
        """Test handoff-related tools."""
        logger.info("=== Testing Handoff Tools ===")
        
        # Test handoff save
        save_result = await self.test_tool("handoff_save", {
            "context": "Test handoff context for MCP testing"
        })
        self.test_results.append(save_result)
        
        # Test handoff get
        get_result = await self.test_tool("handoff_get", {})
        self.test_results.append(get_result)
        
        # Test handoff list
        list_result = await self.test_tool("handoff_list", {"limit": 5})
        self.test_results.append(list_result)
        
        # Test handoff search
        search_result = await self.test_tool("handoff_search", {
            "query": "test",
            "limit": 5
        })
        self.test_results.append(search_result)
        
        # Test handoff insights (if we have a context_id)
        if get_result["success"] and get_result["result"]:
            context_id = get_result["result"].get("id")
            if context_id:
                insights_result = await self.test_tool("handoff_insights", {
                    "context_id": context_id
                })
                self.test_results.append(insights_result)
                
                related_result = await self.test_tool("handoff_related", {
                    "context_id": context_id
                })
                self.test_results.append(related_result)
                
                actions_result = await self.test_tool("handoff_suggest_actions", {
                    "context_id": context_id
                })
                self.test_results.append(actions_result)
    
    async def test_graph_tools(self):
        """Test knowledge graph tools."""
        logger.info("=== Testing Knowledge Graph Tools ===")
        
        # Test entity creation
        entity_payload = {
            "name": "Test Entity",
            "type": "concept",
            "description": "Test entity for MCP testing",
            "properties": {"test_prop": "test_value"}
        }
        
        create_entity_result = await self.test_tool("graph_create_entity", {
            "payload": entity_payload
        })
        self.test_results.append(create_entity_result)
        
        if create_entity_result["success"]:
            entity_id = create_entity_result["result"].get("id")
            
            # Test entity retrieval
            get_entity_result = await self.test_tool("graph_get_entity", {
                "entity_id": entity_id
            })
            self.test_results.append(get_entity_result)
            
            # Test graph search
            search_result = await self.test_tool("graph_search", {
                "query": "test",
                "limit": 10
            })
            self.test_results.append(search_result)
            
            # Test find related
            related_result = await self.test_tool("graph_find_related", {
                "entity_id": entity_id,
                "depth": 2
            })
            self.test_results.append(related_result)
            
            # Test centrality
            centrality_result = await self.test_tool("graph_get_centrality", {
                "entity_id": entity_id
            })
            self.test_results.append(centrality_result)
            
            # Test get relations
            relations_result = await self.test_tool("graph_get_relations", {
                "entity_id": entity_id
            })
            self.test_results.append(relations_result)
            
            # Test find clusters
            clusters_result = await self.test_tool("graph_find_clusters", {
                "entity_type": "concept"
            })
            self.test_results.append(clusters_result)
        
        # Test graph search without specific entity
        general_search_result = await self.test_tool("graph_search", {
            "query": "test",
            "limit": 5
        })
        self.test_results.append(general_search_result)
    
    async def test_intelligence_tools(self):
        """Test intelligence and search tools."""
        logger.info("=== Testing Intelligence Tools ===")
        
        intelligence_tools = [
            ("intelligent_search", {"query": "test query"}),
            ("natural_query", {"query": "What is the status of my tasks?"}),
            ("intent_based_search", {"natural_query": "Find my high priority tasks"}),
            ("complex_query", {"query": "Show me tasks that are due this week and have high priority"}),
            ("search_with_context", {"query": "test", "entity_context": "testing context"}),
            ("get_smart_suggestions", {"context": {"current_activity": "testing"}}),
            ("get_workflow_suggestions", {"user_context": {"activity": "testing"}}),
            ("get_expertise_map", {}),
        ]
        
        for tool_name, params in intelligence_tools:
            result = await self.test_tool(tool_name, params)
            self.test_results.append(result)
    
    async def test_automation_tools(self):
        """Test automation workflow tools."""
        logger.info("=== Testing Automation Tools ===")
        
        # Test workflow registration with updated schema
        workflow_definition = {
            "name": "Test Workflow",
            "description": "Test workflow for MCP testing",
            "trigger": {
                "type": "task",
                "content": "test"
            },
            "actions": [
                {
                    "type": "create_task",
                    "params": {
                        "title": "Test workflow task",
                        "description": "Created by workflow"
                    }
                }
            ]
        }
        
        register_result = await self.test_tool("automation_register_workflow", {
            "workflow": workflow_definition
        })
        self.test_results.append(register_result)
        
        # Test list workflows
        list_result = await self.test_tool("automation_list_workflows", {})
        self.test_results.append(list_result)
        
        if register_result["success"]:
            workflow = register_result["result"].get("workflow")
            workflow_id = workflow.get("id")
            
            # Test get workflow
            get_result = await self.test_tool("automation_get_workflow", {
                "workflow_id": workflow_id
            })
            self.test_results.append(get_result)
            
            # Test pause workflow
            pause_result = await self.test_tool("automation_pause_workflow", {
                "workflow_id": workflow_id
            })
            self.test_results.append(pause_result)
            
            # Test resume workflow
            resume_result = await self.test_tool("automation_resume_workflow", {
                "workflow_id": workflow_id
            })
            self.test_results.append(resume_result)
            
            # Test trigger workflow
            trigger_result = await self.test_tool("automation_trigger_workflow", {
                "workflow_id": workflow_id,
                "event_data": {"test": "data"}
            })
            self.test_results.append(trigger_result)
            
            # Test list runs
            runs_result = await self.test_tool("automation_list_runs", {
                "workflow_id": workflow_id,
                "limit": 5
            })
            self.test_results.append(runs_result)
        
        # Test workflow suggestions
        suggestions_result = await self.test_tool("automation_get_workflow_suggestions", {
            "query": "test",
            "limit": 5
        })
        self.test_results.append(suggestions_result)
        
        # Test suggestion metrics
        metrics_result = await self.test_tool("automation_get_suggestion_metrics", {})
        self.test_results.append(metrics_result)
    
    async def test_task_nl_tools(self):
        """Test natural language task creation tools."""
        logger.info("=== Testing Natural Language Task Tools ===")
        
        # Test natural language task creation
        nl_task_result = await self.test_tool("todo_create_task_nl", {
            "input_text": "Create a high priority task to test the MCP server tomorrow"
        })
        self.test_results.append(nl_task_result)
        
        # First create a handoff context to use for conversation task creation
        handoff_result = await self.test_tool("handoff_save", {
            "context": "Test conversation context for task creation testing"
        })
        self.test_results.append(handoff_result)
        
        # Test task creation from conversation using the created context
        if handoff_result["success"] and handoff_result["result"]:
            context_id = str(handoff_result["result"].get("id"))
            conv_task_result = await self.test_tool("todo_create_from_conversation", {
                "context_id": context_id,
                "title": "Test conversation task"
            })
            self.test_results.append(conv_task_result)
        else:
            # If handoff creation failed, skip the conversation task test
            logger.warning("Skipping conversation task test due to handoff creation failure")
            conv_task_result = {
                "tool_name": "todo_create_from_conversation",
                "success": False,
                "error": "Handoff context creation failed"
            }
            self.test_results.append(conv_task_result)
    
    async def test_search_tools(self):
        """Test search and query tools."""
        logger.info("=== Testing Search Tools ===")
        
        search_tools = [
            ("todo_quick_find", {"query": "test"}),
            ("todo_search_tasks", {"query": "test", "filters": {"priority": "high"}}),
        ]
        
        for tool_name, params in search_tools:
            result = await self.test_tool(tool_name, params)
            self.test_results.append(result)
    
    async def test_project_tools(self):
        """Test project-related tools."""
        logger.info("=== Testing Project Tools ===")
        
        # Get a project ID from previous tests or create one
        projects_result = await self.test_tool("todo_list_projects", {})
        self.test_results.append(projects_result)
        
        if projects_result["success"] and projects_result["result"]:
            project_id = projects_result["result"][0].get("id")
            
            # Test project progress
            progress_result = await self.test_tool("todo_get_project_progress", {
                "project_id": project_id
            })
            self.test_results.append(progress_result)
            
            # Test project timeline
            timeline_result = await self.test_tool("todo_project_timeline", {
                "project_id": project_id
            })
            self.test_results.append(timeline_result)
            
            # Test project intelligence
            intelligence_result = await self.test_tool("get_project_intelligence", {
                "project_id": project_id
            })
            self.test_results.append(intelligence_result)
            
            # Test cross-domain insights
            insights_result = await self.test_tool("get_cross_domain_insights", {
                "entity_id": project_id
            })
            self.test_results.append(insights_result)
    
    async def test_additional_todo_tools(self):
        """Test additional todo tools not covered in main todo test."""
        logger.info("=== Testing Additional Todo Tools ===")
        
        # Test project completion
        projects_result = await self.test_tool("todo_list_projects", {})
        if projects_result["success"] and projects_result["result"]:
            project_id = projects_result["result"][0].get("id")
            
            # Test project update
            update_project_result = await self.test_tool("todo_update_project", {
                "project_id": project_id,
                "progress": 50.0
            })
            self.test_results.append(update_project_result)
        
        # Test area archiving
        areas_result = await self.test_tool("todo_list_areas", {})
        if areas_result["success"] and areas_result["result"]:
            area_id = areas_result["result"][0].get("id")
            
            # Test area archive
            archive_result = await self.test_tool("todo_archive_area", {
                "area_id": area_id
            })
            self.test_results.append(archive_result)
        
        # Test task deletion
        tasks_result = await self.test_tool("todo_search_tasks", {"query": "test"})
        if tasks_result["success"] and tasks_result["result"]:
            task_id = tasks_result["result"][0].get("id")
            
            # Test task delete
            delete_result = await self.test_tool("todo_delete_task", {
                "task_id": task_id
            })
            self.test_results.append(delete_result)
        
        # Test task details with a real task ID if available
        if tasks_result["success"] and tasks_result["result"]:
            real_task_id = tasks_result["result"][0].get("id")
            task_details_result = await self.test_tool("todo_get_task_details", {
                "task_id": real_task_id
            })
        else:
            # Test with invalid ID to verify error handling
            task_details_result = await self.test_tool("todo_get_task_details", {
                "task_id": "test_task_id"
            })
        self.test_results.append(task_details_result)
    
    async def test_additional_graph_tools(self):
        """Test additional graph tools not covered in main graph test."""
        logger.info("=== Testing Additional Graph Tools ===")
        
        # First create some test entities to work with
        entity1_result = await self.test_tool("graph_create_entity", {
            "payload": {
                "name": "Test Source Entity",
                "type": "concept",
                "description": "Test entity for relation testing"
            }
        })
        
        entity2_result = await self.test_tool("graph_create_entity", {
            "payload": {
                "name": "Test Target Entity", 
                "type": "concept",
                "description": "Test target entity for relation testing"
            }
        })
        
        # Test relation creation with real entities
        if entity1_result["success"] and entity2_result["success"]:
            source_id = entity1_result["result"].get("id")
            target_id = entity2_result["result"].get("id")
            
            create_relation_result = await self.test_tool("graph_create_relation", {
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": "related_to",
                "strength": 0.8
            })
            self.test_results.append(create_relation_result)
            
            # Test shortest path with real entities
            shortest_path_result = await self.test_tool("graph_shortest_path", {
                "source_id": source_id,
                "target_id": target_id
            })
            self.test_results.append(shortest_path_result)
            
            # Test entity deletion with real entity
            delete_entity_result = await self.test_tool("graph_delete_entity", {
                "entity_id": source_id
            })
            self.test_results.append(delete_entity_result)
            
            # Test relation deletion (this will likely fail since we deleted the source entity)
            delete_relation_result = await self.test_tool("graph_delete_relation", {
                "relation_id": "test_relation_id"
            })
            self.test_results.append(delete_relation_result)
        else:
            # If entity creation failed, test with invalid IDs to verify error handling
            create_relation_result = await self.test_tool("graph_create_relation", {
                "source_id": "test_source_id",
                "target_id": "test_target_id",
                "relation_type": "related_to",
                "strength": 0.8
            })
            self.test_results.append(create_relation_result)
            
            shortest_path_result = await self.test_tool("graph_shortest_path", {
                "source_id": "test_source_id",
                "target_id": "test_target_id"
            })
            self.test_results.append(shortest_path_result)
            
            delete_entity_result = await self.test_tool("graph_delete_entity", {
                "entity_id": "test_entity_id"
            })
            self.test_results.append(delete_entity_result)
            
            delete_relation_result = await self.test_tool("graph_delete_relation", {
                "relation_id": "test_relation_id"
            })
            self.test_results.append(delete_relation_result)
    
    async def test_additional_automation_tools(self):
        """Test additional automation tools not covered in main automation test."""
        logger.info("=== Testing Additional Automation Tools ===")
        
        # Get a real workflow ID from previous tests if available
        workflows_result = await self.test_tool("automation_list_workflows", {})
        
        if workflows_result["success"] and workflows_result["result"]:
            workflow_id = workflows_result['result'][0].id
            
            # Test workflow deletion with real workflow
            delete_workflow_result = await self.test_tool("automation_delete_workflow", {
                "workflow_id": workflow_id
            })
            self.test_results.append(delete_workflow_result)
        else:
            # Test with invalid ID to verify error handling
            delete_workflow_result = await self.test_tool("automation_delete_workflow", {
                "workflow_id": "test_workflow_id"
            })
            self.test_results.append(delete_workflow_result)
        
        # Test get run with invalid ID (runs are created during workflow execution)
        get_run_result = await self.test_tool("automation_get_run", {
            "run_id": "test_run_id"
        })
        self.test_results.append(get_run_result)
        
        # Test approve workflow suggestion with invalid ID (suggestions are generated by AI)
        approve_suggestion_result = await self.test_tool("automation_approve_workflow_suggestion", {
            "suggestion_id": "test_suggestion_id"
        })
        self.test_results.append(approve_suggestion_result)
    
    async def run_all_tests(self):
        """Run all test categories."""
        logger.info("Starting comprehensive MCP tool testing...")
        
        # Test basic connectivity
        tools_result = await self.test_list_available_tools()
        self.test_results.append(tools_result)
        
        # Run all test categories
        await self.test_todo_tools()
        await self.test_handoff_tools()
        await self.test_graph_tools()
        await self.test_intelligence_tools()
        await self.test_automation_tools()
        await self.test_task_nl_tools()
        await self.test_search_tools()
        await self.test_project_tools()
        await self.test_additional_todo_tools()
        await self.test_additional_graph_tools()
        await self.test_additional_automation_tools()
        
        logger.info("All tests completed!")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive test report."""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        # Group results by tool category
        categories = {
            "todo": [],
            "handoff": [],
            "graph": [],
            "intelligence": [],
            "automation": [],
            "search": [],
            "project": [],
            "other": []
        }
        
        for result in self.test_results:
            tool_name = result["tool_name"]
            if tool_name.startswith("todo_"):
                categories["todo"].append(result)
            elif tool_name.startswith("handoff_"):
                categories["handoff"].append(result)
            elif tool_name.startswith("graph_"):
                categories["graph"].append(result)
            elif tool_name.startswith(("intelligent_", "natural_", "intent_", "complex_", "get_")):
                categories["intelligence"].append(result)
            elif tool_name.startswith("automation_"):
                categories["automation"].append(result)
            elif tool_name.startswith(("search_", "quick_find")):
                categories["search"].append(result)
            elif "project" in tool_name:
                categories["project"].append(result)
            else:
                categories["other"].append(result)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "categories": categories,
            "detailed_results": self.test_results
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report."""
        print("\n" + "="*60)
        print("UNIFIED MCP TEST REPORT")
        print("="*60)
        
        summary = report["summary"]
        print("\nSUMMARY:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Successful: {summary['successful_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        
        print("\nCATEGORY BREAKDOWN:")
        for category, results in report["categories"].items():
            if results:
                success_count = sum(1 for r in results if r["success"])
                print(f"  {category.upper()}: {success_count}/{len(results)} successful")
        
        print("\nFAILED TESTS:")
        failed_tests = [r for r in self.test_results if not r["success"]]
        for result in failed_tests:
            print(f"  ✗ {result['tool_name']}: {result['error']}")
        
        print("="*60)


async def main():
    """Main test runner."""
    async with Client("http://127.0.0.1:9090/mcp/") as client:
        try:
            tester = UnifiedMCPTester(client)

            # Run all tests
            await tester.run_all_tests()
            
            # Generate and print report
            report = tester.generate_report()
            tester.print_report(report)
            
            # Save detailed report to file
            with open("mcp_test_report.json", "w") as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info("Detailed report saved to mcp_test_report.json")
            
        except KeyboardInterrupt:
            logger.info("Testing interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error during testing: {e}")
        finally:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())