# Unified MCP Test Suite

This test suite provides comprehensive testing for the `unified.py` MCP server, testing all available tools from the `unified-tools.json` file.

## Overview

The test suite includes:

- **Todo Tools**: Area, project, and task management
- **Handoff Tools**: Context saving and retrieval
- **Knowledge Graph Tools**: Entity and relationship management
- **Intelligence Tools**: AI-powered search and analysis
- **Automation Tools**: Workflow management
- **Search Tools**: Various search capabilities
- **Project Tools**: Project-specific operations

## Prerequisites

1. Make sure you have the required dependencies installed:
   ```bash
   pip install fastmcp
   ```

2. Ensure the main MCP server (`main.py`) can be started by `unified.py`

## Running the Tests

### Option 1: Using the Automated Script (Recommended)

```bash
./run_mcp_tests.sh
```

This script will:
1. Start the `unified.py` MCP server
2. Wait for it to be ready
3. Run the comprehensive test suite
4. Stop the server when done
5. Generate a detailed report

### Option 2: Manual Testing

1. Start the unified MCP server:
   ```bash
   python unified.py
   ```

2. In another terminal, run the test suite:
   ```bash
   python test_unified_mcp.py
   ```

## Test Output

The test suite provides:

1. **Real-time logging**: Progress and results as tests run
2. **Console report**: Summary of test results
3. **Detailed JSON report**: Saved to `mcp_test_report.json`

### Sample Output

```
============================================================
UNIFIED MCP TEST REPORT
============================================================

SUMMARY:
  Total Tests: 45
  Successful: 42
  Failed: 3
  Success Rate: 93.3%

CATEGORY BREAKDOWN:
  TODO: 12/12 successful
  HANDOFF: 6/6 successful
  GRAPH: 8/8 successful
  INTELLIGENCE: 7/7 successful
  AUTOMATION: 8/8 successful
  SEARCH: 2/2 successful
  PROJECT: 2/2 successful

FAILED TESTS:
  ✗ todo_create_task_nl: Connection timeout
  ✗ handoff_insights: Invalid context_id
  ✗ automation_trigger_workflow: Workflow not found
============================================================
```

## Test Categories

### Todo Tools
- Area creation and management
- Project creation and management
- Task creation, updating, and completion
- Task retrieval (today, upcoming, anytime, etc.)
- Statistics and progress tracking

### Handoff Tools
- Context saving and retrieval
- Context listing and searching
- AI-powered insights and suggestions

### Knowledge Graph Tools
- Entity creation and management
- Relationship management
- Graph search and traversal
- Centrality analysis and clustering

### Intelligence Tools
- Intelligent search across domains
- Natural language query processing
- Intent-based search
- Smart suggestions and workflow recommendations

### Automation Tools
- Workflow registration and management
- Workflow execution and monitoring
- Suggestion system testing

### Search Tools
- Quick semantic search
- Advanced task filtering

### Project Tools
- Project progress tracking
- Timeline analysis
- Cross-domain insights

## Configuration

You can modify the test configuration in `test_unified_mcp.py`:

- **Server connection**: Change `host` and `port` in `UnifiedMCPTester.__init__()`
- **Test data**: Modify test parameters in individual test methods
- **Logging level**: Adjust the logging configuration

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure `unified.py` is running and accessible on port 9090
2. **Import errors**: Ensure all dependencies are installed
3. **Timeout errors**: Some tools may take longer to respond; consider increasing timeouts
4. **Database errors**: Ensure the main server's database is properly configured

### Debug Mode

For more detailed debugging, you can modify the logging level:

```python
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
```

## Extending the Tests

To add new tests:

1. Create a new test method in the `UnifiedMCPTester` class
2. Add the method call to `run_all_tests()`
3. Update the category classification in `generate_report()`

Example:
```python
async def test_new_tool(self):
    """Test a new tool."""
    result = await self.test_tool("new_tool_name", {"param": "value"})
    self.test_results.append(result)
```

## Report Analysis

The detailed JSON report (`mcp_test_report.json`) contains:

- Complete test results with timing information
- Error details for failed tests
- Categorized results for analysis
- Performance metrics

This can be used for:
- Continuous integration testing
- Performance monitoring
- Debugging tool issues
- Regression testing 