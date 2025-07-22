"""
Migration System for Unified Memory Architecture

Converts existing JSONL-based tool data (handoff, todo, memory_graph, knowledgebase)
to the unified SQLite + vector search memory store.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

try:
    from ..core import UnifiedMemoryStore
    from ..core.models import MemoryEntity, MemoryRelation, MemoryContext
except ImportError:
    from core import UnifiedMemoryStore
    from core.models import MemoryEntity, MemoryRelation, MemoryContext

# Configure logging
logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages migration from JSONL files to unified memory store."""
    
    def __init__(self, memory_store: UnifiedMemoryStore, data_dir: Path):
        self.memory_store = memory_store
        self.data_dir = Path(data_dir)
        self.migration_log = []
        
    def migrate_all(self, backup: bool = True) -> Dict[str, Any]:
        """Migrate all JSONL files to unified memory."""
        results = {}
        
        if backup:
            backup_path = self.create_backup()
            logger.info(f"Created backup at: {backup_path}")
        
        # Migrate in dependency order
        results['handoff'] = self.migrate_handoff()
        results['todo'] = self.migrate_todo()
        results['memory_graph'] = self.migrate_memory_graph()
        results['knowledgebase'] = self.migrate_knowledgebase()
        
        # Generate migration report
        return self.generate_migration_report(results)
    
    def migrate_incremental(self, tool_name: str) -> Dict[str, Any]:
        """Migrate single tool data."""
        migration_methods = {
            'handoff': self.migrate_handoff,
            'todo': self.migrate_todo,
            'memory_graph': self.migrate_memory_graph,
            'knowledgebase': self.migrate_knowledgebase
        }
        
        if tool_name not in migration_methods:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
        
        return migration_methods[tool_name]()
    
    def migrate_handoff(self) -> Dict[str, Any]:
        """Migrate handoff.jsonl to contexts table."""
        handoff_file = self.data_dir / "handoff.jsonl"
        
        if not handoff_file.exists():
            return {"status": "skipped", "reason": "file not found"}
        
        migrated_contexts = []
        errors = []
        
        try:
            with open(handoff_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        # Convert to MemoryContext
                        context = MemoryContext(
                            id=f"handoff_{data['id']}",  # Preserve original ID with prefix
                            type="handoff",
                            content=data['context'],
                            metadata={
                                'migrated_from': 'handoff.jsonl',
                                'original_id': data['id'],
                                'migration_date': datetime.now().isoformat()
                            }
                        )
                        
                        # Preserve original timestamp
                        if 'created_at' in data:
                            context.created_at = datetime.fromisoformat(data['created_at'])
                        
                        # Save with AI enhancement
                        saved_context = self.memory_store.save_context_with_ai(context)
                        migrated_contexts.append(saved_context.id)
                        
                    except Exception as e:
                        errors.append(f"Line {line_num}: {str(e)}")
                        continue
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "completed",
            "migrated_count": len(migrated_contexts),
            "error_count": len(errors),
            "errors": errors,
            "migrated_ids": migrated_contexts
        }
    
    def migrate_todo(self) -> Dict[str, Any]:
        """Migrate todo.jsonl to task entities."""
        todo_file = self.data_dir / "todo.jsonl"
        
        if not todo_file.exists():
            return {"status": "skipped", "reason": "file not found"}
        
        migrated_tasks = []
        errors = []
        
        try:
            with open(todo_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        # Convert to MemoryEntity (task type)
                        task = MemoryEntity(
                            id=f"task_{data['id']}",
                            type="task",
                            name=data['title'],
                            content=data.get('description', ''),
                            metadata={
                                'priority': data.get('priority', 'medium'),
                                'status': data.get('status', 'todo'),
                                'migrated_from': 'todo.jsonl',
                                'original_id': data['id'],
                                'migration_date': datetime.now().isoformat()
                            },
                            tags=data.get('tags', [])
                        )
                        
                        # Preserve original timestamp
                        if 'created_at' in data:
                            task.created_at = datetime.fromisoformat(data['created_at'])
                        
                        # Save task entity
                        saved_task = self.memory_store.save_entity(task)
                        migrated_tasks.append(saved_task.id)
                        
                        # Extract and link entities from task content
                        if task.content:
                            self._extract_and_link_task_entities(saved_task)
                        
                    except Exception as e:
                        errors.append(f"Line {line_num}: {str(e)}")
                        continue
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "completed",
            "migrated_count": len(migrated_tasks),
            "error_count": len(errors),
            "errors": errors,
            "migrated_ids": migrated_tasks
        }
    
    def _extract_and_link_task_entities(self, task: MemoryEntity):
        """Extract entities from task and create relationships."""
        try:
            # Use AI extraction to find related entities
            extracted = self.memory_store.extract_entities(f"{task.name} {task.content}")
            
            for entity_data in extracted:
                # Create or link entities
                entity = MemoryEntity(
                    type=entity_data['type'],
                    name=entity_data['name'],
                    content=f"Extracted from task: {task.name}",
                    metadata={'auto_extracted': True, 'source_task': task.id}
                )
                
                saved_entity = self.memory_store.save_entity(entity)
                
                # Create relationship
                relation = MemoryRelation(
                    source_id=task.id,
                    target_id=saved_entity.id,
                    relation_type='relates_to',
                    strength=0.7,
                    metadata={'migration_extracted': True}
                )
                self.memory_store.save_relation(relation)
        except Exception as e:
            logger.warning(f"Failed to extract entities from task {task.id}: {e}")
    
    def migrate_memory_graph(self) -> Dict[str, Any]:
        """Migrate memory_graph.jsonl to entities and relations."""
        memory_file = self.data_dir / "memory_graph.jsonl"
        
        if not memory_file.exists():
            return {"status": "skipped", "reason": "file not found"}
        
        entities = []
        relations = []
        errors = []
        
        # First pass: collect all entities and relations
        entity_data = []
        relation_data = []
        
        try:
            with open(memory_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        if data.get('type') == 'entity':
                            entity_data.append(data)
                        elif data.get('type') == 'relation':
                            relation_data.append(data)
                        
                    except Exception as e:
                        errors.append(f"Line {line_num}: {str(e)}")
                        continue
            
            # Second pass: migrate entities
            entity_id_map = {}  # Map old IDs to new IDs
            
            for data in entity_data:
                try:
                    entity = MemoryEntity(
                        id=f"mg_{data['id']}",  # Prefix to avoid conflicts
                        type=data.get('entity_type', 'unknown'),
                        name=data['name'],
                        content=data.get('description', ''),
                        metadata={
                            **data.get('metadata', {}),
                            'migrated_from': 'memory_graph.jsonl',
                            'original_id': data['id'],
                            'migration_date': datetime.now().isoformat()
                        }
                    )
                    
                    # Preserve timestamp
                    if 'created_at' in data:
                        entity.created_at = datetime.fromisoformat(data['created_at'])
                    
                    saved_entity = self.memory_store.save_entity(entity)
                    entities.append(saved_entity.id)
                    entity_id_map[data['id']] = saved_entity.id
                    
                except Exception as e:
                    errors.append(f"Entity {data.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Third pass: migrate relations
            for data in relation_data:
                try:
                    # Map old entity IDs to new IDs
                    source_id = entity_id_map.get(data['source'])
                    target_id = entity_id_map.get(data['target'])
                    
                    if not source_id or not target_id:
                        errors.append(f"Relation {data}: Missing entity mapping")
                        continue
                    
                    relation = MemoryRelation(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type=data['relation'],
                        strength=data.get('strength', 1.0),
                        metadata={
                            'migrated_from': 'memory_graph.jsonl',
                            'migration_date': datetime.now().isoformat()
                        }
                    )
                    
                    # Preserve timestamp
                    if 'created_at' in data:
                        relation.created_at = datetime.fromisoformat(data['created_at'])
                    
                    saved_relation = self.memory_store.save_relation(relation)
                    relations.append(saved_relation.id)
                    
                except Exception as e:
                    errors.append(f"Relation {data}: {str(e)}")
                    continue
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "completed",
            "migrated_entities": len(entities),
            "migrated_relations": len(relations),
            "error_count": len(errors),
            "errors": errors
        }
    
    def migrate_knowledgebase(self) -> Dict[str, Any]:
        """Migrate knowledgebase.jsonl to file/function entities."""
        kb_file = self.data_dir / "knowledgebase.jsonl"
        
        if not kb_file.exists():
            return {"status": "skipped", "reason": "file not found"}
        
        migrated_files = []
        migrated_functions = []
        errors = []
        
        try:
            with open(kb_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line.strip())
                        
                        # Create file entity
                        file_entity = MemoryEntity(
                            id=f"kb_{data['id']}",
                            type="file",
                            name=data.get('path', data.get('name', 'unknown')),
                            content=data.get('content', ''),
                            metadata={
                                'file_path': data.get('path'),
                                'language': self._detect_language(data.get('path', '')),
                                'migrated_from': 'knowledgebase.jsonl',
                                'original_id': data['id'],
                                'migration_date': datetime.now().isoformat()
                            }
                        )
                        
                        if 'created_at' in data:
                            file_entity.created_at = datetime.fromisoformat(data['created_at'])
                        
                        saved_file = self.memory_store.save_entity(file_entity)
                        migrated_files.append(saved_file.id)
                        
                        # Create function entities if present
                        functions = data.get('functions', [])
                        for func_name in functions:
                            func_entity = MemoryEntity(
                                type="function",
                                name=func_name,
                                content=f"Function in {file_entity.name}",
                                metadata={
                                    'parent_file': saved_file.id,
                                    'migrated_from': 'knowledgebase.jsonl',
                                    'migration_date': datetime.now().isoformat()
                                }
                            )
                            
                            saved_func = self.memory_store.save_entity(func_entity)
                            migrated_functions.append(saved_func.id)
                            
                            # Create file -> function relationship
                            relation = MemoryRelation(
                                source_id=saved_file.id,
                                target_id=saved_func.id,
                                relation_type='contains',
                                strength=1.0,
                                metadata={'migration_generated': True}
                            )
                            self.memory_store.save_relation(relation)
                    
                    except Exception as e:
                        errors.append(f"Line {line_num}: {str(e)}")
                        continue
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "completed",
            "migrated_files": len(migrated_files),
            "migrated_functions": len(migrated_functions),
            "error_count": len(errors),
            "errors": errors
        }
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript', 
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.sql': 'sql'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'unknown')
    
    def create_backup(self) -> str:
        """Create backup of all JSONL files before migration."""
        backup_dir = self.data_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(exist_ok=True)
        
        jsonl_files = ['handoff.jsonl', 'todo.jsonl', 'memory_graph.jsonl', 'knowledgebase.jsonl']
        
        for filename in jsonl_files:
            source = self.data_dir / filename
            if source.exists():
                shutil.copy2(source, backup_dir / filename)
        
        return str(backup_dir)
    
    def validate_migration(self, migration_results: Dict) -> Dict[str, Any]:
        """Validate migration completed successfully."""
        validation = {
            'total_records_migrated': 0,
            'total_errors': 0,
            'tools_migrated': [],
            'validation_passed': True,
            'issues': []
        }
        
        for tool_name, result in migration_results.items():
            if result['status'] == 'completed':
                validation['tools_migrated'].append(tool_name)
                
                # Count migrated records
                if 'migrated_count' in result:
                    validation['total_records_migrated'] += result['migrated_count']
                if 'migrated_entities' in result:
                    validation['total_records_migrated'] += result['migrated_entities']
                if 'migrated_files' in result:
                    validation['total_records_migrated'] += result['migrated_files']
                
                # Count errors
                validation['total_errors'] += result.get('error_count', 0)
            else:
                validation['issues'].append(f"{tool_name}: {result.get('message', 'failed')}")
        
        # Check database integrity
        try:
            entity_count = self.memory_store.conn.execute("SELECT COUNT(*) FROM entity_data").fetchone()[0]
            relation_count = self.memory_store.conn.execute("SELECT COUNT(*) FROM entity_relations").fetchone()[0]
            context_count = self.memory_store.conn.execute("SELECT COUNT(*) FROM contexts").fetchone()[0]
            
            validation['database_counts'] = {
                'entities': entity_count,
                'relations': relation_count,
                'contexts': context_count
            }
            
        except Exception as e:
            validation['issues'].append(f"Database validation failed: {str(e)}")
            validation['validation_passed'] = False
        
        if validation['total_errors'] > 0:
            validation['validation_passed'] = False
        
        return validation
    
    def generate_migration_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive migration report."""
        validation = self.validate_migration(results)
        
        report = {
            'migration_timestamp': datetime.now().isoformat(),
            'results': results,
            'validation': validation,
            'summary': {
                'tools_processed': len(results),
                'tools_successful': len([r for r in results.values() if r['status'] == 'completed']),
                'tools_failed': len([r for r in results.values() if r['status'] != 'completed']),
                'total_records_migrated': validation['total_records_migrated'],
                'total_errors': validation['total_errors']
            }
        }
        
        return report 