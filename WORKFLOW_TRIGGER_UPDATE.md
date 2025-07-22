# Workflow Trigger System Update

## Summary

Updated the workflow engine to support a simplified trigger syntax that focuses on entity type matching rather than requiring explicit event types. This makes workflow definitions more intuitive and reduces complexity.

## Changes Made

### 1. Updated WorkflowTrigger Model

**Before:**
```python
class WorkflowTrigger(BaseModel):
    type: str  # Required event type like "entity_created"
    filter: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
```

**After:**
```python
class WorkflowTrigger(BaseModel):
    # Direct entity matching fields
    type: Optional[str] = None  # Entity type (e.g., "handoff", "task")
    content: Optional[str] = None  # Content filter
    name: Optional[str] = None  # Name filter  
    tags: Optional[List[str]] = None  # Tag filters
    metadata: Optional[Dict[str, Any]] = None  # Metadata filters
    
    # Legacy support
    event_type: Optional[str] = None  # For backward compatibility
    schedule: Optional[str] = None  # Cron schedule
```

### 2. Updated Matching Logic

- **Entity-based matching**: Workflows now match against entity properties directly
- **Multiple entity support**: Single events can contain multiple entities
- **Backward compatibility**: Legacy event_type + filter syntax still works

### 3. Enhanced Event Emission

Updated `_emit_workflow_event` to support:
- Multiple entities in a single event (`entities` parameter)
- Optional event types (defaults to "entity_event")
- Better payload structure for entity matching

## Usage Examples

### New Simplified Syntax

```yaml
# Simple entity type matching
trigger:
  type: handoff
  content: meow

# Multiple criteria
trigger:
  type: task
  tags: ["urgent", "bug"]
  metadata:
    priority: high
```

### Legacy Syntax (Still Supported)

```yaml
# Old way - still works
trigger:
  event_type: entity_created
  filter:
    entity.type: handoff
    entity.content: meow
```

### Comparison

**OLD WAY:**
```json
{
  "trigger": {
    "type": "context_created",
    "filter": {
      "entity.type": "handoff",
      "entity.content": "meow"
    }
  }
}
```

**NEW WAY:**
```json
{
  "trigger": {
    "type": "handoff",
    "content": "meow"
  }
}
```

## Benefits

1. **Simpler syntax**: Direct entity matching without nested filter objects
2. **More intuitive**: Focus on what you want to match, not how events are structured
3. **Multiple entity support**: Single workflow can process multiple entities at once
4. **Backward compatible**: Existing workflows continue to work
5. **Flexible matching**: Support for content, name, tags, and metadata filters

## Technical Details

### Entity Matching Logic

The new `_entity_matches_trigger` method checks:
1. **Entity type**: Exact match on `entity.type`
2. **Content**: Substring match in `entity.content`
3. **Name**: Substring match in `entity.name` 
4. **Tags**: Any tag in trigger must exist in entity tags
5. **Metadata**: Exact key-value matches in entity metadata

### Multiple Entity Events

Events can now contain multiple entities:
```python
memory_store._emit_workflow_event(
    event_type="batch_created",
    entities=[entity1, entity2, entity3]
)
```

Each entity is checked individually against workflow triggers.

## Migration Guide

### For New Workflows
Use the simplified syntax:
```yaml
trigger:
  type: handoff
  content: meeting
  tags: ["urgent"]
```

### For Existing Workflows
No changes needed - legacy syntax continues to work. Optionally migrate to new syntax for clarity.

### Automation Tool Integration
The automation tool automatically handles both syntaxes when registering workflows through the MCP interface. 