#!/usr/bin/env python3
"""
Migration CLI for converting JSONL-based tools to unified memory architecture.
"""

import argparse
import json
import logging
import shutil
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid

try:
    from core import UnifiedMemoryStore, create_memory_store
    from models import MemoryEntity, MemoryRelation, MemoryContext
    from migration import MigrationManager
except ImportError:
    # Fallback for when running as standalone script
    import sys
    sys.path.append('.')
    from core import UnifiedMemoryStore, create_memory_store
    from models import MemoryEntity, MemoryRelation, MemoryContext
    from migration import MigrationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationCLI:
    """Command-line interface for migration operations."""
    
    def __init__(self):
        self.migrator = None
    
    def migrate(self, data_dir: str, output_db: str, **kwargs) -> bool:
        """Migrate JSONL files to unified database."""
        try:
            logger.info(f"Starting migration from {data_dir} to {output_db}")
            
            # Create output directory
            output_path = Path(output_db)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize migrator with the correct database path
            # create_memory_store expects a directory, not a file path
            data_path = output_path.parent
            memory_store = create_memory_store(data_path)
            self.migrator = MigrationManager(memory_store, data_dir)
            
            # Run migration
            results = self.migrator.migrate_all()
            
            # Print results
            self._print_migration_results(results)
            
            logger.info("Migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def verify(self, db_path: str, compare_with: Optional[str] = None) -> bool:
        """Verify migration results."""
        try:
            logger.info(f"Verifying migration results in {db_path}")
            
            # Initialize memory store with the correct path
            # create_memory_store expects a directory, not a file path
            data_path = Path(db_path).parent
            store = create_memory_store(data_path)
            
            # Get statistics
            stats = self._get_database_stats(store)
            
            # Print statistics
            self._print_verification_results(stats)
            
            # Compare with backup if provided
            if compare_with:
                self._compare_with_backup(db_path, compare_with)
            
            logger.info("Verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def rollback(self, backup_dir: str, restore_to: str) -> bool:
        """Rollback migration by restoring from backup."""
        try:
            logger.info(f"Rolling back migration from {backup_dir} to {restore_to}")
            
            # Check if backup exists
            backup_path = Path(backup_dir)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup directory not found: {backup_dir}")
            
            # Remove current data directory
            restore_path = Path(restore_to)
            if restore_path.exists():
                shutil.rmtree(restore_path)
            
            # Restore from backup
            shutil.copytree(backup_path, restore_path)
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _get_database_stats(self, store: UnifiedMemoryStore) -> Dict[str, Any]:
        """Get database statistics."""
        stats = {}
        
        # Entity counts by type
        entity_types = ['task', 'person', 'project', 'file', 'conversation', 'code', 'meeting', 'note', 'url', 'tool']
        for entity_type in entity_types:
            try:
                entities = store.search_entities(entity_type, limit=1000)
                stats[f"{entity_type}_count"] = len(entities)
            except Exception:
                stats[f"{entity_type}_count"] = 0
        
        # Total entities
        try:
            all_entities = store.get_all_entities(limit=10000)
            stats['total_entities'] = len(all_entities)
        except Exception:
            stats['total_entities'] = 0
        
        # Relation counts
        relation_types = ['relates_to', 'contains', 'assigned_to', 'mentions', 'references', 'depends_on', 'similar_to', 'part_of', 'created_by', 'updated_by', 'follows']
        for relation_type in relation_types:
            try:
                relations = store.get_relations_by_type(relation_type, limit=1000)
                stats[f"{relation_type}_count"] = len(relations)
            except Exception:
                stats[f"{relation_type}_count"] = 0
        
        # Context counts
        try:
            contexts = store.search_contexts("", limit=1000)
            stats['total_contexts'] = len(contexts)
        except Exception:
            stats['total_contexts'] = 0
        
        return stats
    
    def _print_migration_results(self, results: Dict[str, Any]) -> None:
        """Print migration results."""
        print("\n" + "="*50)
        print("MIGRATION RESULTS")
        print("="*50)
        
        # Handle the case where results might be a string or have a different structure
        if isinstance(results, str):
            print(f"Migration result: {results}")
            return
            
        for tool, result in results.items():
            if isinstance(result, str):
                print(f"\n{tool.upper()}: {result}")
                continue
                
            print(f"\n{tool.upper()}:")
            if isinstance(result, dict):
                # Handle different result formats from migration manager
                if 'migrated_count' in result:
                    print(f"  Records migrated: {result.get('migrated_count', 0)}")
                elif 'migrated_entities' in result:
                    print(f"  Entities migrated: {result.get('migrated_entities', 0)}")
                elif 'migrated_contexts' in result:
                    print(f"  Contexts migrated: {result.get('migrated_contexts', 0)}")
                else:
                    print(f"  Records migrated: {result.get('entities', 0)}")
                
                print(f"  Relations migrated: {result.get('relations', 0)}")
                print(f"  Contexts migrated: {result.get('contexts', 0)}")
                print(f"  Errors: {result.get('error_count', result.get('errors', 0))}")
                
                if 'status' in result:
                    print(f"  Status: {result['status']}")
            else:
                print(f"  Result: {result}")
    
    def _print_verification_results(self, stats: Dict[str, Any]) -> None:
        """Print verification results."""
        print("\n" + "="*50)
        print("VERIFICATION RESULTS")
        print("="*50)
        
        print(f"\nTotal Entities: {stats['total_entities']}")
        print(f"Total Contexts: {stats['total_contexts']}")
        
        print("\nEntities by Type:")
        for key, value in stats.items():
            if key.endswith('_count') and not key.startswith('relates_to'):
                entity_type = key.replace('_count', '')
                print(f"  {entity_type}: {value}")
        
        print("\nRelations by Type:")
        for key, value in stats.items():
            if key.endswith('_count') and any(rt in key for rt in ['relates_to', 'contains', 'assigned_to', 'mentions', 'references', 'depends_on', 'similar_to', 'part_of', 'created_by', 'updated_by', 'follows']):
                relation_type = key.replace('_count', '')
                print(f"  {relation_type}: {value}")
    
    def _compare_with_backup(self, db_path: str, backup_dir: str) -> None:
        """Compare migration results with backup."""
        print(f"\nComparing with backup: {backup_dir}")
        
        # Count JSONL files in backup
        backup_path = Path(backup_dir)
        jsonl_files = list(backup_path.glob("*.jsonl"))
        
        print(f"JSONL files in backup: {len(jsonl_files)}")
        
        for jsonl_file in jsonl_files:
            try:
                with open(jsonl_file, 'r') as f:
                    lines = f.readlines()
                    print(f"  {jsonl_file.name}: {len(lines)} records")
            except Exception as e:
                print(f"  {jsonl_file.name}: Error reading file - {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Migration CLI for unified memory system")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate JSONL files to unified database')
    migrate_parser.add_argument('--data-dir', required=True, help='Directory containing JSONL files')
    migrate_parser.add_argument('--output-db', required=True, help='Output database path')
    migrate_parser.add_argument('--enable-vector-search', action='store_true', help='Enable vector search')
    migrate_parser.add_argument('--enable-ai-extraction', action='store_true', help='Enable AI extraction')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify migration results')
    verify_parser.add_argument('--db-path', required=True, help='Database path to verify')
    verify_parser.add_argument('--compare-with', help='Compare with backup directory')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migration')
    rollback_parser.add_argument('--backup-dir', required=True, help='Backup directory path')
    rollback_parser.add_argument('--restore-to', required=True, help='Directory to restore to')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = MigrationCLI()
    
    if args.command == 'migrate':
        success = cli.migrate(args.data_dir, args.output_db)
        exit(0 if success else 1)
    
    elif args.command == 'verify':
        success = cli.verify(args.db_path, args.compare_with)
        exit(0 if success else 1)
    
    elif args.command == 'rollback':
        success = cli.rollback(args.backup_dir, args.restore_to)
        exit(0 if success else 1)


if __name__ == '__main__':
    main() 