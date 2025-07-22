"""
Database connection and schema setup for unified memory architecture.
Phase 1.1: Database Schema & Core Models
"""

import logging
import sqlite3
import sqlite_vec

from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connection and schema for unified memory system."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection with proper configuration."""
        if self.connection is None:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create connection
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.enable_load_extension(True)
            sqlite_vec.load(self.connection)

            # Configure connection
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self.connection.execute("PRAGMA json_validation = ON")
            
            logger.info(f"Connected to database: {self.db_path}")
        
        return self.connection
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    def initialize_schema(self) -> None:
        """Initialize database schema from schema.sql file."""
        # Try multiple possible locations for schema.sql
        possible_paths = [
            Path(__file__).parent / "schema.sql",
            Path.cwd() / "schema.sql",
            Path(__file__).parent.parent / "schema.sql"
        ]
        
        schema_file = None
        for path in possible_paths:
            if path.exists():
                schema_file = path
                break
        
        if not schema_file:
            raise FileNotFoundError(f"Schema file not found in any of: {possible_paths}")
        
        conn = self.connect()
        
        try:
            # Read and execute schema
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute the entire schema as one statement
            conn.executescript(schema_sql)
            
            conn.commit()
            logger.info(f"Database schema initialized successfully from {schema_file}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    def check_schema_version(self) -> Optional[str]:
        """Check if schema version table exists and return version."""
        conn = self.connect()
        
        try:
            # Check if schema_version table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_version'
            """)
            
            if cursor.fetchone():
                cursor = conn.execute("SELECT version FROM schema_version ORDER BY created_at DESC LIMIT 1")
                result = cursor.fetchone()
                return result['version'] if result else None
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to check schema version: {e}")
            return None
    
    def create_schema_version_table(self) -> None:
        """Create schema version tracking table."""
        conn = self.connect()
        
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Schema version table created")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create schema version table: {e}")
            raise
    
    def record_schema_version(self, version: str, description: str = "") -> None:
        """Record a new schema version."""
        conn = self.connect()
        
        try:
            conn.execute(
                "INSERT INTO schema_version (version, description) VALUES (?, ?)",
                (version, description)
            )
            conn.commit()
            logger.info(f"Recorded schema version: {version}")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to record schema version: {e}")
            raise
    
    def verify_schema(self) -> bool:
        """Verify that all required tables exist."""
        conn = self.connect()
        
        required_tables = {
            'entities',
            'entity_data', 
            'entity_relations',
            'contexts'
        }
        
        try:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (?, ?, ?, ?)
            """, tuple(required_tables))
            
            existing_tables = {row['name'] for row in cursor.fetchall()}
            missing_tables = required_tables - existing_tables
            
            if missing_tables:
                logger.debug(f"Missing required tables: {missing_tables}")
                return False
            
            logger.debug("Schema verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> list:
        """Get information about a table's structure."""
        conn = self.connect()
        
        try:
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return []
    
    def get_index_info(self, table_name: str) -> list:
        """Get information about indexes on a table."""
        conn = self.connect()
        
        try:
            cursor = conn.execute(f"PRAGMA index_list({table_name})")
            indexes = []
            
            for index_row in cursor.fetchall():
                index_name = index_row['name']
                cursor2 = conn.execute(f"PRAGMA index_info({index_name})")
                index_info = [dict(row) for row in cursor2.fetchall()]
                indexes.append({
                    'name': index_name,
                    'unique': index_row['unique'],
                    'columns': index_info
                })
            
            return indexes
            
        except Exception as e:
            logger.error(f"Failed to get index info for {table_name}: {e}")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_database_manager(data_dir: Path) -> DatabaseManager:
    """Create a database manager for the unified memory system."""
    db_path = data_dir / "unified_memory.db"
    return DatabaseManager(db_path)


def initialize_database(data_dir: Path) -> DatabaseManager:
    """Initialize the database with schema and return manager."""
    db_manager = create_database_manager(data_dir)
    
    try:
        # Initialize schema if needed
        if not db_manager.verify_schema():
            logger.info("Initializing database schema...")
            db_manager.initialize_schema()
            
            # Create version tracking
            db_manager.create_schema_version_table()
            db_manager.record_schema_version("1.0.0", "Initial unified memory schema")
        
        return db_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise 