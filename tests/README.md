# Test Suite for Emily MCP Tools

This directory contains comprehensive tests for the Emily MCP Tools project.

## Test Structure

- `test_memory_graph.py` - Tests for the MemoryGraphTool class
- `test_todo.py` - Tests for the TodoTool class
- `test_calendar.py` - Tests for the CalendarTool class
- `test_knowledgebase.py` - Tests for the KnowledgebaseTool class
- `test_time_service.py` - Tests for the TimeServiceTool class
- `test_handoff.py` - Tests for the HandoffTool class
- `test_async_tasks.py` - Tests for the AsyncTasksTool class
- `__init__.py` - Makes tests a Python package

## Running Tests

### Using the test runner script
```bash
python run_tests.py
```

### Using pytest directly
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_memory_graph.py

# Run specific test
pytest tests/test_memory_graph.py::TestMemoryGraphTool::test_create_entities_new

# Run with verbose output
pytest -v

# Run with coverage (if pytest-cov is installed)
pytest --cov=tools
```

## Test Coverage

The test suite provides comprehensive coverage for all tools in the Emily MCP Tools project:

### Memory Graph Tool (`test_memory_graph.py`)
- **Entity Management**: Creating, reading, and deleting entities
- **Relation Management**: Creating and deleting relations between entities
- **Observation Management**: Adding and removing observations from entities
- **Graph Operations**: Reading the entire graph and searching nodes

### Todo Tool (`test_todo.py`)
- **Task Management**: Creating, updating, and deleting tasks
- **Priority & Status**: Managing task priorities and status transitions
- **Search & Filtering**: Searching tasks by title/description and filtering by status/priority
- **Statistics**: Generating task statistics and analytics

### Calendar Tool (`test_calendar.py`)
- **Event Management**: Creating, updating, and deleting calendar events
- **Event Types**: Managing different types of events (meetings, tasks, appointments)
- **Date/Time Operations**: Handling date ranges, upcoming events, and time filtering
- **Attendees & Locations**: Managing event attendees and locations

### Knowledgebase Tool (`test_knowledgebase.py`)
- **Codebase Management**: Registering and managing multiple codebases
- **Knowledge Nodes**: Adding and searching knowledge nodes (functions, classes, etc.)
- **Relations**: Creating relationships between knowledge nodes
- **Graph Queries**: Querying the knowledge graph with filters

### Time Service Tool (`test_time_service.py`)
- **Time Information**: Getting comprehensive current time information
- **Time Formatting**: Formatting timestamps in various formats
- **Timezone Handling**: Managing timezone information and conversions
- **Time Calculations**: Calculating time differences and relative times

### Handoff Tool (`test_handoff.py`)
- **Context Management**: Saving and retrieving chat contexts
- **Session Handoff**: Managing context persistence between sessions
- **Context History**: Listing and managing multiple contexts
- **Timestamp Management**: Ensuring context freshness with timestamps

### Async Tasks Tool (`test_async_tasks.py`)
- **Task Scheduling**: Creating and scheduling background tasks
- **Task Execution**: Managing task status and execution lifecycle
- **Priority Management**: Handling task priorities and queuing
- **Task History**: Tracking task history and completion status

### Core Functionality Tests
- **Entity Management**: Creating, reading, and deleting entities
- **Relation Management**: Creating and deleting relations between entities
- **Observation Management**: Adding and removing observations from entities
- **Graph Operations**: Reading the entire graph and searching nodes

### Edge Cases and Error Handling
- **Duplicate Prevention**: Tests ensure no duplicate entities or relations are created
- **Cascading Deletes**: When entities are deleted, related relations are also removed
- **Corrupted Data**: Tests handle corrupted JSONL files gracefully
- **Non-existent Entities**: Tests behavior when operations are performed on non-existent entities

### Integration Tests
- **MCP Registration**: Tests that all tools are properly registered with the MCP server
- **File I/O**: Tests file reading and writing operations
- **Data Persistence**: Tests that data is properly saved and loaded

## Test Fixtures

The test suite uses several fixtures to provide test data:

- `temp_data_dir`: Creates a temporary directory for test data
- `memory_tool`: Creates a MemoryGraphTool instance for testing
- `sample_entities`: Provides sample entity data
- `sample_relations`: Provides sample relation data
- `sample_observations`: Provides sample observation data

## Test Data

Tests use realistic sample data including:
- **Entities**: People (Alice, Bob) and projects (Project Alpha)
- **Relations**: Social connections (knows) and work relationships (works_on, contributes_to)
- **Observations**: Descriptive information about entities

## Dependencies

- `pytest` - Test framework
- `tempfile` - For creating temporary test directories
- `unittest.mock` - For mocking MCP server interactions

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_<method_name>_<scenario>`
2. Use descriptive docstrings explaining what the test verifies
3. Use the provided fixtures for consistent test data
4. Test both happy path and edge cases
5. Ensure tests are isolated and don't depend on each other

## Continuous Integration

The test suite is designed to run quickly and reliably, making it suitable for CI/CD pipelines. All tests should pass before merging code changes. 