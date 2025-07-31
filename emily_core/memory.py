"""
Core UnifiedMemoryStore class for intelligent memory backend.
Phase 2.2: AI Entity Extraction & Enhancement
"""

import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

try:
    from .models import MemoryEntity, MemoryRelation, MemoryContext
    from .database import DatabaseManager
except ImportError:
    from core.models import MemoryEntity, MemoryRelation, MemoryContext
    from core.database import DatabaseManager

# Lazy import AI extraction to avoid circular imports
AIExtractor = None
EntityMatcher = None  
ContentEnhancer = None

def _lazy_import_ai_extraction():
    """Lazy import AI extraction classes to avoid circular imports."""
    global AIExtractor, EntityMatcher, ContentEnhancer
    if AIExtractor is None:
        try:
            from intelligence.ai_extraction import AIExtractor as _AIExtractor, EntityMatcher as _EntityMatcher, ContentEnhancer as _ContentEnhancer
            AIExtractor = _AIExtractor
            EntityMatcher = _EntityMatcher
            ContentEnhancer = _ContentEnhancer
        except ImportError:
            logger.error("Failed to import AI extraction classes")
            raise

# Import sqlite-vec for vector search
try:
    import sqlite_vec
except ImportError:
    sqlite_vec = None

logger = logging.getLogger(__name__)


class UnifiedMemoryStore:
    """Intelligent memory backend using SQLite + sqlite-vec."""
    
    DEFAULT_EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    DEFAULT_EMBEDDING_DIMENSION = 384
    
    def __init__(self, 
                 db_path: Union[str, Path],
                 embedding_model: Optional[str] = None,
                 embedding_dimension: int = 384,
                 enable_vector_search: bool = True,
                 enable_ai_extraction: bool = True):
        """
        Initialize the UnifiedMemoryStore.
        
        Args:
            db_path: Path to SQLite database file
            embedding_model: Name of sentence-transformers model to use
            embedding_dimension: Dimension of embedding vectors
            enable_vector_search: Whether to enable vector search capabilities
            enable_ai_extraction: Whether to enable AI entity extraction
        """
        self.db_path = Path(db_path)
        self.embedding_dimension = embedding_dimension
        self.enable_vector_search = enable_vector_search
        self.enable_ai_extraction = enable_ai_extraction
        
        # Thread-local storage for database connections
        self._local = threading.local()
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Initialize embedding model
        self.embedding_model = None
        self.vector_enabled = False
        self.workflow_engine = None
        
        if enable_vector_search:
            self._setup_embedding_model(embedding_model)
        
        # Initialize AI extraction components
        self.ai_extractor = None
        self.entity_matcher = None
        self.content_enhancer = None
        
        if enable_ai_extraction:
            self._setup_ai_extraction()
        
        # Initialize schema using database manager's connection
        self._setup_schema()
        
        # Now that schema is initialized, we can use thread-local connections
        
        logger.info(f"UnifiedMemoryStore initialized: {self.db_path}")
        logger.info(f"Vector search enabled: {self.vector_enabled}")
        logger.info(f"AI extraction enabled: {self.enable_ai_extraction}")
    
    def _setup_ai_extraction(self) -> None:
        """Initialize AI extraction components."""
        try:
            _lazy_import_ai_extraction()
            self.ai_extractor = AIExtractor(use_spacy=True)
            self.entity_matcher = EntityMatcher(self)
            self.content_enhancer = ContentEnhancer(self, self.ai_extractor, self.entity_matcher)
            logger.info("AI extraction components initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize AI extraction: {e}")
            self.enable_ai_extraction = False
    
    def _get_conn(self) -> sqlite3.Connection:
        """Return a per-thread SQLite connection, creating it lazily."""
        if not hasattr(self._local, "conn"):
            # Create a new connection for this thread
            conn = sqlite3.connect(str(self.db_path))
            self._configure_conn(conn)
            self._local.conn = conn
        return self._local.conn
    
    def _configure_conn(self, conn: sqlite3.Connection) -> None:
        """Configure SQLite connection with optimal settings."""
        # Enable JSON support
        conn.execute("PRAGMA json_validation = ON")
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        # Performance optimizations
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = MEMORY")
        
        # Load sqlite-vec extension if available
        if self.enable_vector_search and sqlite_vec is not None:
            try:
                # Enable extension loading
                conn.enable_load_extension(True)
                # Use sqlite-vec's load function to enable vector search
                sqlite_vec.load(conn)
                logger.info("sqlite-vec extension loaded successfully")
            except Exception as e:
                logger.warning(f"sqlite-vec extension not available: {e}")
                # Don't disable vector search here - let the embedding model setup handle it
    
    def _setup_embedding_model(self, model_name: Optional[str] = None) -> None:
        """Initialize the embedding model."""
        if not self.enable_vector_search:
            self.vector_enabled = False
            return
        
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = model_name or self.DEFAULT_EMBEDDING_MODEL
            self.embedding_model = SentenceTransformer(model_name)
            # self.embedding_model = SentenceTransformer(self.db_path.parent / model_name)
            # self.embedding_model.save(self.db_path.parent / model_name)
            # Verify model dimension
            test_embedding = self.embedding_model.encode("test")
            actual_dimension = len(test_embedding)
            
            if actual_dimension != self.embedding_dimension:
                logger.warning(f"Model dimension mismatch: expected {self.embedding_dimension}, got {actual_dimension}")
                self.embedding_dimension = actual_dimension
            
            # Set vector enabled to True if we successfully loaded the model
            self.vector_enabled = True
            logger.info(f"Embedding model loaded: {model_name} ({self.embedding_dimension} dimensions)")
            
        except ImportError:
            logger.warning("sentence-transformers not available. Vector search disabled.")
            self.vector_enabled = False
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.vector_enabled = False
            self.embedding_model = None
    
    def _setup_schema(self) -> None:
        """Initialize database schema."""
        try:
            # Initialize schema using database manager
            if not self.db_manager.verify_schema():
                logger.info("Initializing database schema...")
                self.db_manager.initialize_schema()
                self.db_manager.create_schema_version_table()
                self.db_manager.record_schema_version("1.0.0", "Initial unified memory schema")
            
            # Verify schema was created successfully using the database manager's connection
            if not self.db_manager.verify_schema():
                raise RuntimeError("Schema initialization failed - required tables missing")
            
            # Set up vector search tables if enabled
            if self.vector_enabled:
                self._setup_vector_tables()
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    def _setup_vector_tables(self) -> None:
        """Set up vector search tables and indexes."""
        if sqlite_vec is None:
            logger.warning("sqlite-vec not available, skipping vector table creation")
            return
            
        conn = self._get_conn()
        
        try:
            # Create regular tables to store embeddings with sqlite-vec BLOB format
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entity_embeddings (
                    id TEXT PRIMARY KEY,
                    embedding BLOB,
                    FOREIGN KEY (id) REFERENCES entity_data(id) ON DELETE CASCADE
                )
            """)
            
            # Create vector table for context embeddings using sqlite-vec
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_embeddings (
                    id TEXT PRIMARY KEY,
                    embedding BLOB,
                    FOREIGN KEY (id) REFERENCES contexts(id) ON DELETE CASCADE
                )
            """)
            
            conn.commit()
            logger.info("Vector tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create vector tables: {e}")
            # Vector tables are optional - don't disable vector search entirely
            logger.warning("Vector tables not available, but embedding model can still be used")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text content."""
        if not self.vector_enabled or not self.embedding_model or not text:
            return None
        
        try:
            # Clean and normalize text
            text = text.strip()
            if not text:
                return None
            
            # Generate embedding
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None
    
    def _store_embedding(self, table: str, id: str, embedding: List[float]) -> bool:
        """Store embedding in vector table."""
        if not self.vector_enabled or not embedding or sqlite_vec is None:
            return False
        
        conn = self._get_conn()
        
        try:
            # Convert embedding to JSON string for storage (sqlite-vec can handle JSON)
            embedding_json = json.dumps(embedding)
            
            conn.execute(f"""
                INSERT OR REPLACE INTO {table}_embeddings (id, embedding)
                VALUES (?, ?)
            """, (id, embedding_json))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embedding: {e}")
            return False

    # ============================================================================
    # ENTITY CRUD OPERATIONS
    # ============================================================================
    
    def save_entity(self, entity: MemoryEntity, use_transaction: bool = True) -> MemoryEntity:
        """Save entity with automatic embedding generation."""
        conn = self._get_conn()
        
        logger.info(f"Saving entity: {entity.id}")
        
        try:
            if use_transaction:
                conn.execute("BEGIN TRANSACTION")
            
            # Check if this is a new entity (for workflow event emission)
            is_new_entity = not entity.id or not self._entity_exists(entity.id)
            
            # Generate UUID if entity.id is None
            if not entity.id:
                entity.id = str(uuid.uuid4())
            
            # Update timestamps
            now = datetime.now(timezone.utc)
            entity.updated_at = now
            if not entity.created_at:
                entity.created_at = now
            
            # Prepare entity data
            entity_dict = entity.to_dict()
            
            # Insert into entities table
            conn.execute("""
                INSERT OR REPLACE INTO entities (uuid, created_at)
                VALUES (?, ?)
            """, (entity.id, entity.created_at.isoformat()))
            
            # Insert into entity_data table
            conn.execute("""
                INSERT OR REPLACE INTO entity_data 
                (id, type, name, content, metadata, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.id, entity.type, entity.name, entity.content,
                json.dumps(entity.metadata), json.dumps(entity.tags),
                entity.created_at.isoformat(), entity.updated_at.isoformat()
            ))
            
            # Generate and store embedding
            if self.vector_enabled:
                # Combine name and content for embedding
                embedding_text = f"{entity.name}"
                if entity.content:
                    embedding_text += f" {entity.content}"
                
                embedding = self._generate_embedding(embedding_text)
                if embedding:
                    self._store_embedding("entity", entity.id, embedding)
            
            # Update FTS index
            self._ensure_fts_table()
            conn.execute("""
                INSERT OR REPLACE INTO entity_fts(id, name, content, tags)
                VALUES (?, ?, ?, ?)
            """, (
                entity.id, entity.name, entity.content,
                json.dumps(entity.tags) if entity.tags else None
            ))
            
            if use_transaction:
                conn.commit()
            
            # Emit workflow event after successful save
            self._emit_workflow_event(entity=entity)
            logger.debug(f"Saved entity: {entity.id} ({entity.type})")
            return entity
            
        except Exception as e:
            if use_transaction:
                conn.rollback()
            logger.error(f"Failed to save entity: {e}")
            raise
    
    def get_entity(self, entity_id: str) -> Optional[MemoryEntity]:
        """Retrieve entity by ID."""
        conn = self._get_conn()
        
        try:
            cursor = conn.execute("""
                SELECT id, type, name, content, metadata, tags, created_at, updated_at
                FROM entity_data
                WHERE id = ?
            """, (entity_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dict
            data = dict(row)
            
            # Parse JSON metadata
            if data['metadata']:
                data['metadata'] = json.loads(data['metadata'])
            
            return MemoryEntity.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            return None
    
    def _entity_exists(self, entity_id: str) -> bool:
        """Check if an entity or context exists by ID."""
        conn = self._get_conn()
        
        try:
            # Check in entity_data table
            cursor = conn.execute("SELECT id FROM entity_data WHERE id = ?", (entity_id,))
            if cursor.fetchone():
                return True
            
            # Check in contexts table
            cursor = conn.execute("SELECT id FROM contexts WHERE id = ?", (entity_id,))
            if cursor.fetchone():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check if entity exists {entity_id}: {e}")
            return False
    
    def update_entity(self, entity: MemoryEntity) -> MemoryEntity:
        """Update existing entity, regenerate embedding if content changed."""
        if not entity.id:
            raise ValueError("Entity must have an ID to update")
        
        # Get existing entity to check for changes
        existing = self.get_entity(entity.id)
        if not existing:
            raise ValueError(f"Entity {entity.id} not found")
        
        # Update timestamps
        entity.updated_at = datetime.now(timezone.utc)
        entity.created_at = existing.created_at  # Preserve original creation time
        
        # Check if content changed (for embedding regeneration)
        content_changed = (
            existing.name != entity.name or 
            existing.content != entity.content
        )
        
        # Save the entity (this will update both tables)
        updated_entity = self.save_entity(entity)
        
        # Regenerate embedding if content changed
        if content_changed and self.vector_enabled:
            embedding_text = f"{entity.name}"
            if entity.content:
                embedding_text += f" {entity.content}"
            
            embedding = self._generate_embedding(embedding_text)
            if embedding:
                self._store_embedding("entity", entity.id, embedding)
        
        logger.debug(f"Updated entity: {entity.id}")
        return updated_entity
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity and its relationships."""
        conn = self._get_conn()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Check if entity exists first
            cursor = conn.execute("SELECT id FROM entity_data WHERE id = ?", (entity_id,))
            if not cursor.fetchone():
                conn.rollback()
                return False
            
            # Delete relationships where this entity is source or target
            conn.execute("""
                DELETE FROM entity_relations 
                WHERE source_id = ? OR target_id = ?
            """, (entity_id, entity_id))
            
            # Delete from entity_data
            conn.execute("DELETE FROM entity_data WHERE id = ?", (entity_id,))
            
            # Delete from entities table
            conn.execute("DELETE FROM entities WHERE uuid = ?", (entity_id,))
            
            # Delete embeddings if vector search is enabled
            if self.vector_enabled:
                try:
                    conn.execute("DELETE FROM entity_embeddings WHERE id = ?", (entity_id,))
                except sqlite3.OperationalError:
                    # Vector table might not exist
                    pass
            
            # Delete from FTS index
            try:
                conn.execute("DELETE FROM entity_fts WHERE id = ?", (entity_id,))
            except sqlite3.OperationalError:
                # FTS table might not exist
                pass
            
            conn.commit()
            logger.debug(f"Deleted entity: {entity_id}")
            return True
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            return False

    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    def search(self, query: str, filters: Optional[Dict] = None, limit: int = 10) -> List[Dict]:
        """Unified search across entities using semantic + full-text search."""
        logger.debug(f"Search called - query: '{query}', filters: {filters}, limit: {limit}")
        if not query.strip() and not filters:
            logger.debug("Empty query and no filters, returning empty results")
            return []
        
        filters = filters or {}
        
        # Perform vector search if enabled
        vector_results = []
        if self.vector_enabled:
            vector_results = self._vector_search(query, filters, limit * 2)
        
        # Perform full-text search
        fts_results = self._fts_search(query, filters, limit * 2)
        
        # Combine and rank results
        combined_results = self._combine_search_results(vector_results, fts_results)
        
        # Apply final limit
        return combined_results[:limit]
    
    def _vector_search(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Perform vector similarity search using sqlite-vec distance functions."""
        if not self.vector_enabled or sqlite_vec is None:
            return []
        
        conn = self._get_conn()
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return []
            
            # Build filter conditions
            where_clause, params = self._build_filter_conditions(filters)
            
            # Vector similarity search using sqlite-vec distance functions
            sql = f"""
                SELECT 
                    ed.*,
                    vec_distance_cosine(?, ee.embedding) as distance
                FROM entity_embeddings ee
                JOIN entity_data ed ON ed.id = ee.id
                {where_clause}
                ORDER BY distance
                LIMIT ?
            """
            
            # Convert query embedding to JSON string for sqlite-vec
            query_embedding_json = json.dumps(query_embedding)
            
            # Add filter parameters
            all_params = [query_embedding_json, limit] + params
            
            cursor = conn.execute(sql, all_params)
            results = []
            
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def _fts_search(self, query: str, filters: Dict, limit: int) -> List[Dict]:
        """Perform full-text search using FTS5."""
        conn = self._get_conn()
        
        try:
            # Check if FTS table exists, create if not
            self._ensure_fts_table()
            
            # Build filter conditions
            where_clause, params = self._build_filter_conditions(filters)
            logger.debug(f"FTS search - query: '{query}', filters: {filters}, where_clause: '{where_clause}', params: {params}")
            
            # FTS search with ranking
            if query.strip():
                # Text search with FTS
                sql = f"""
                    SELECT 
                        ed.id, ed.type, ed.name, ed.content, ed.metadata, 
                        ed.tags, ed.created_at, ed.updated_at,
                        bm25(entity_fts) as relevance
                    FROM entity_fts fts
                    JOIN entity_data ed ON fts.id = ed.id
                    WHERE entity_fts MATCH ?
                    {where_clause}
                    ORDER BY relevance
                    LIMIT ?
                """
                all_params = [query] + params + [limit]
            else:
                # Filter-only search (no text query)
                sql = f"""
                    SELECT 
                        ed.id, ed.type, ed.name, ed.content, ed.metadata, 
                        ed.tags, ed.created_at, ed.updated_at,
                        0.0 as relevance
                    FROM entity_data ed
                    WHERE 1=1 {where_clause}
                    ORDER BY ed.created_at DESC
                    LIMIT ?
                """
                all_params = params + [limit]
            cursor = conn.execute(sql, all_params)
            results = []
            
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"FTS search failed: {e}")
            return []
    
    def _ensure_fts_table(self) -> None:
        """Ensure FTS table exists and is populated."""
        conn = self._get_conn()
        
        try:
            # Check if FTS table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='entity_fts'
            """)
            
            if not cursor.fetchone():
                # Create FTS table without content table to avoid sync issues
                conn.execute("""
                    CREATE VIRTUAL TABLE entity_fts USING fts5(
                        id, name, content, tags
                    )
                """)
                
                # Populate with existing data
                conn.execute("""
                    INSERT INTO entity_fts(id, name, content, tags)
                    SELECT id, name, content, tags FROM entity_data
                """)
                
                conn.commit()
                logger.info("FTS table created and populated")
        
        except Exception as e:
            logger.error(f"Failed to ensure FTS table: {e}")
    
    def _combine_search_results(self, vector_results: List[Dict], fts_results: List[Dict]) -> List[Dict]:
        """Combine and rank vector + FTS search results."""
        # Create lookup for deduplication
        seen_ids = set()
        combined_results = []
        
        # Process vector results
        for result in vector_results:
            entity_id = result['id']
            if entity_id not in seen_ids:
                seen_ids.add(entity_id)
                # Normalize vector distance (0 = identical, 1 = completely different)
                vector_score = 1.0 - result.get('distance', 0.0)
                result['combined_score'] = 0.6 * vector_score
                combined_results.append(result)
        
        # Process FTS results
        for result in fts_results:
            entity_id = result['id']
            if entity_id not in seen_ids:
                seen_ids.add(entity_id)
                # Normalize FTS relevance (higher is better)
                fts_score = min(result.get('relevance', 0.0), 2500.0) / 2500.0
                result['combined_score'] = 0.4 * fts_score
                combined_results.append(result)
            else:
                # Update existing result with FTS score
                for existing in combined_results:
                    if existing['id'] == entity_id:
                        fts_score = min(result.get('relevance', 0.0), 2500.0) / 2500.0
                        existing['combined_score'] += 0.4 * fts_score
                        break
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x.get('combined_score', 0.0), reverse=True)
        
        return combined_results
    
    def _build_filter_conditions(self, filters: Dict) -> tuple:
        """Build SQL WHERE conditions from filter dict."""
        conditions = []
        params = []
        
        if not filters:
            return "", []
        
        # Entity type filter
        if 'type' in filters:
            conditions.append("ed.type = ?")
            params.append(filters['type'])
        
        if 'types' in filters:
            placeholders = ','.join(['?' for _ in filters['types']])
            conditions.append(f"ed.type IN ({placeholders})")
            params.extend(filters['types'])
        
        # Tags filter
        if 'tags' in filters:
            tag_conditions = []
            for tag in filters['tags']:
                tag_conditions.append("ed.tags LIKE ?")
                params.append(f"%{tag}%")
            if tag_conditions:
                conditions.append(f"({' OR '.join(tag_conditions)})")
        
        # Date filters
        if 'created_after' in filters:
            conditions.append("ed.created_at >= ?")
            params.append(filters['created_after'])
        
        if 'created_before' in filters:
            conditions.append("ed.created_at <= ?")
            params.append(filters['created_before'])
        
        # Metadata filters (JSON path queries)
        for key, value in filters.items():
            if key.startswith('metadata.'):
                json_path = key.replace('metadata.', '$.')
                conditions.append(f"json_extract(ed.metadata, ?) = ?")
                params.extend([json_path, value])
        
        where_clause = ""
        if conditions:
            where_clause = " AND " + " AND ".join(conditions)
        
        return where_clause, params

    # ============================================================================
    # RELATIONSHIP OPERATIONS
    # ============================================================================
    
    def save_relation(self, relation: MemoryRelation, use_transaction: bool = True) -> MemoryRelation:
        """Save relationship between entities."""
        conn = self._get_conn()
        
        logger.info(f"Saving relation: {relation.id}")
        try:
            if use_transaction:
                conn.execute("BEGIN TRANSACTION")
            
            # Validate source and target entities exist
            source_exists = self._entity_exists(relation.source_id)
            target_exists = self._entity_exists(relation.target_id)
            
            if not source_exists:
                raise ValueError(f"Source entity {relation.source_id} not found")
            if not target_exists:
                raise ValueError(f"Target entity {relation.target_id} not found")
            
            # Generate UUID for relation.id if not provided
            if not relation.id:
                relation.id = str(uuid.uuid4())
            
            # Save to entity_relations table
            conn.execute("""
                INSERT OR REPLACE INTO entity_relations 
                (id, source_id, target_id, relation_type, strength, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                relation.id, relation.source_id, relation.target_id,
                relation.relation_type, relation.strength,
                json.dumps(relation.metadata), relation.created_at.isoformat()
            ))
            
            if use_transaction:
                conn.commit()
            
            # Emit workflow event after successful save
            self._emit_workflow_event(relation=relation)
            
            logger.debug(f"Saved relation: {relation.id}")
            return relation
            
        except Exception as e:
            if use_transaction:
                conn.rollback()
            logger.error(f"Failed to save relation: {e}")
            raise
    
    def get_related(self, entity_id: str, relation_types: Optional[List[str]] = None) -> List[Dict]:
        """Get entities related to the given entity."""
        conn = self._get_conn()
        
        try:
            # Build query
            sql = """
                SELECT 
                    er.id as relation_id, er.relation_type, er.strength, er.metadata as relation_metadata,
                    ed.id, ed.type, ed.name, ed.content, ed.metadata, ed.tags, ed.created_at, ed.updated_at
                FROM entity_relations er
                JOIN entity_data ed ON (er.target_id = ed.id AND er.source_id = ?)
                   OR (er.source_id = ed.id AND er.target_id = ?)
            """
            params = [entity_id, entity_id]
            
            if relation_types:
                placeholders = ','.join(['?' for _ in relation_types])
                sql += f" WHERE er.relation_type IN ({placeholders})"
                params.extend(relation_types)
            
            cursor = conn.execute(sql, params)
            results = []
            
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                if data['relation_metadata']:
                    data['relation_metadata'] = json.loads(data['relation_metadata'])
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get related entities for {entity_id}: {e}")
            return []
    
    def get_related_contexts(self, entity_id: str, relation_types: Optional[List[str]] = None) -> List[Dict]:
        """Get contexts related to the given entity."""
        conn = self._get_conn()
        
        try:
            # Build query
            sql = """
                SELECT 
                    er.id as relation_id, er.relation_type, er.strength, er.metadata as relation_metadata,
                    c.id, c.type, c.content, c.summary, c.topics, c.entity_ids, c.metadata, c.created_at
                FROM entity_relations er
                JOIN contexts c ON (er.target_id = c.id AND er.source_id = ?)
                   OR (er.source_id = c.id AND er.target_id = ?)
            """
            params = [entity_id, entity_id]
            
            if relation_types:
                placeholders = ','.join(['?' for _ in relation_types])
                sql += f" WHERE er.relation_type IN ({placeholders})"
                params.extend(relation_types)
            
            cursor = conn.execute(sql, params)
            results = []
            
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                if data['relation_metadata']:
                    data['relation_metadata'] = json.loads(data['relation_metadata'])
                # Add a 'name' field for compatibility with entity format
                data['name'] = data.get('summary', data.get('content', '')[:50])
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get related contexts for {entity_id}: {e}")
            return []
    
    def get_relation_by_id(self, relation_id: str) -> Optional[MemoryRelation]:
        """Get a specific relation by ID."""
        conn = self._get_conn()
        
        try:
            cursor = conn.execute("""
                SELECT id, source_id, target_id, relation_type, strength, metadata, created_at
                FROM entity_relations
                WHERE id = ?
            """, (relation_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            data = dict(row)
            # Parse JSON metadata
            if data['metadata']:
                data['metadata'] = json.loads(data['metadata'])
            
            return MemoryRelation.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to get relation {relation_id}: {e}")
            return None
    
    def delete_relation(self, relation_id: str) -> bool:
        """Delete specific relationship."""
        conn = self._get_conn()
        
        try:
            cursor = conn.execute("DELETE FROM entity_relations WHERE id = ?", (relation_id,))
            conn.commit()
            
            deleted = cursor.rowcount > 0
            if deleted:
                logger.debug(f"Deleted relation: {relation_id}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete relation {relation_id}: {e}")
            return False

    # ============================================================================
    # CONTEXT OPERATIONS
    # ============================================================================
    
    def get_context(self, context_id: str) -> Optional[MemoryContext]:
        """Get a context by ID."""
        conn = self._get_conn()
        
        try:
            cursor = conn.execute("""
                SELECT id, type, content, summary, topics, entity_ids, metadata, created_at
                FROM contexts
                WHERE id = ?
            """, (context_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            data = dict(row)
            # Parse JSON metadata
            if data['metadata']:
                data['metadata'] = json.loads(data['metadata'])
            
            return MemoryContext.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            return None
    
    def save_context(self, context: MemoryContext) -> MemoryContext:
        """Save context/conversation data with AI enhancement."""
        conn = self._get_conn()
        logger.info(f"Saving context: {context.id}")
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Generate UUID if context.id is None
            if not context.id:
                context.id = str(uuid.uuid4())
            
            # Apply AI enhancement if enabled
            if self.enable_ai_extraction and self.content_enhancer:
                try:
                    enhancement = self.content_enhancer.enhance_context(context)
                    
                    # Update context with AI-generated metadata
                    keys = ['topics', 'summary', 'action_items', 'extracted_entities', 'extract_hash']
                    for key in keys:
                        if enhancement.get(key):
                            context.metadata[key] = enhancement[key]
                    
                    logger.info(f"Enhancement: {enhancement}")
                    # Create new entities for extracted entities marked for creation
                    new_entity_ids = []
                    for entity_data in enhancement['extracted_entities']:
                        if entity_data['action'] == 'create':
                            # Create new entity
                            entity = MemoryEntity(
                                type=entity_data['type'],
                                name=entity_data['name'],
                                content=f"Auto-extracted from context: {context.id}",
                                metadata={
                                    'auto_generated': True, 
                                    'confidence': entity_data['confidence']
                                }
                            )
                            saved_entity = self.save_entity(entity, use_transaction=False)
                            new_entity_ids.append(saved_entity.id)
                    
                    # Add new entity IDs to context
                    if new_entity_ids:
                        context.entity_ids = list(set(context.entity_ids + new_entity_ids))
                    
                except Exception as e:
                    logger.warning(f"AI enhancement failed for context {context.id}: {e}")
            
            # Prepare context data
            context_dict = context.to_dict()
            
            # Save to contexts table
            conn.execute("""
                INSERT OR REPLACE INTO contexts 
                (id, type, content, summary, topics, entity_ids, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.id, context.type, context.content, context.summary,
                context_dict['topics'], context_dict['entity_ids'],
                json.dumps(context.metadata), context.created_at.isoformat()
            ))
            
            # Generate and store embedding
            if self.vector_enabled:
                embedding = self._generate_embedding(context.content)
                if embedding:
                    self._store_embedding("context", context.id, embedding)
            
            conn.commit()
            
            # Create relationships for linked entities
            if self.enable_ai_extraction and self.content_enhancer:
                try:
                    enhancement = self.content_enhancer.enhance_context(context)
                    relationships = self.content_enhancer.create_content_relationships(
                        context.id, enhancement['extracted_entities']
                    )
                    
                    for relation_data in relationships:
                        relation = MemoryRelation(**relation_data)
                        self.save_relation(relation, use_transaction=False)
                        
                except Exception as e:
                    logger.warning(f"Failed to create relationships for context {context.id}: {e}")
            
            self._emit_workflow_event(context=context)
            logger.debug(f"Saved context: {context.id} ({context.type})")
            return context
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save context: {e}")
            raise
    
    def search_contexts(self, query: str, filters: Optional[Dict] = None) -> List[MemoryContext]:
        """Search contexts by content and metadata."""
        conn = self._get_conn()
        
        try:
            # Build filter conditions
            where_clause, params = self._build_context_filter_conditions(filters or {})
            
            # Search contexts
            sql = f"""
                SELECT id, type, content, summary, topics, entity_ids, metadata, created_at
                FROM contexts
                WHERE content LIKE ?
                {where_clause}
                ORDER BY created_at DESC
            """
            
            all_params = [f"%{query}%"] + params
            cursor = conn.execute(sql, all_params)
            results = []
            
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                results.append(MemoryContext.from_dict(data))
            
            return results
            
        except Exception as e:
            logger.error(f"Context search failed: {e}")
            return []
    
    def update_context(self, context: MemoryContext) -> MemoryContext:
        """Update an existing context."""
        conn = self._get_conn()
        
        try:
            conn.execute("BEGIN TRANSACTION")
            
            # Prepare context data
            context_dict = context.to_dict()
            
            # Update context in database
            conn.execute("""
                UPDATE contexts 
                SET type = ?, content = ?, summary = ?, topics = ?, entity_ids = ?, metadata = ?
                WHERE id = ?
            """, (
                context.type, context.content, context.summary,
                context_dict['topics'], context_dict['entity_ids'],
                json.dumps(context.metadata), context.id
            ))
            
            # Update embedding if vector search is enabled
            if self.vector_enabled:
                embedding = self._generate_embedding(context.content)
                if embedding:
                    self._store_embedding("context", context.id, embedding)
            
            conn.commit()
            
            logger.debug(f"Updated context: {context.id} ({context.type})")
            return context
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update context: {e}")
            raise
    
    # ============================================================================
    # AI EXTRACTION METHODS
    # ============================================================================
    
    def extract_entities_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using AI extraction."""
        if not self.enable_ai_extraction or not self.ai_extractor:
            return []
        
        try:
            return self.ai_extractor.extract_entities(text)
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topics from text using AI extraction."""
        if not self.enable_ai_extraction or not self.ai_extractor:
            return []
        
        try:
            return self.ai_extractor.extract_topics(text)
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return []
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate summary from text using AI extraction."""
        if not self.enable_ai_extraction or not self.ai_extractor:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        try:
            return self.ai_extractor.generate_summary(text, max_length)
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract action items from text using AI extraction."""
        if not self.enable_ai_extraction or not self.ai_extractor:
            return []
        
        try:
            return self.ai_extractor.extract_action_items(text)
        except Exception as e:
            logger.error(f"Action item extraction failed: {e}")
            return []
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using AI extraction (alias for extract_entities_from_text)."""
        return self.extract_entities_from_text(text)
    
    def search_entities(self, entity_type: str, filters: Optional[Dict] = None, limit: int = 20) -> List[MemoryEntity]:
        """Search for entities by type with optional filters."""
        conn = self._get_conn()
        
        # Build filter conditions
        where_conditions = ["type = ?"]
        params = [entity_type]
        
        if filters:
            if 'name' in filters:
                where_conditions.append("name LIKE ?")
                params.append(f"%{filters['name']}%")
            
            if 'tags' in filters:
                # Search for entities with any of the specified tags
                tag_conditions = []
                for tag in filters['tags']:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f"%{tag}%")
                if tag_conditions:
                    where_conditions.append(f"({' OR '.join(tag_conditions)})")
        
        where_clause = " AND ".join(where_conditions)
        
        try:
            cursor = conn.execute(f"""
                SELECT * FROM entity_data 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, params + [limit])
            
            entities = []
            for row in cursor.fetchall():
                try:
                    # Parse metadata with error handling
                    metadata = {}
                    if row['metadata']:
                        try:
                            metadata = json.loads(row['metadata'])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in metadata for entity {row['id']}")
                    
                    # Parse tags with error handling
                    tags = []
                    if row['tags']:
                        try:
                            tags = json.loads(row['tags'])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in tags for entity {row['id']}")
                    
                    entity = MemoryEntity(
                        id=row['id'],
                        type=row['type'],
                        name=row['name'],
                        content=row['content'],
                        metadata=metadata,
                        tags=tags,
                        created_at=datetime.fromisoformat(row['created_at'])
                    )
                    entities.append(entity)
                except Exception as e:
                    logger.error(f"Failed to create entity from row {row['id']}: {e}")
                    continue
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity search failed: {e}")
            return []
    
    def get_all_entities(self, entity_type: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        """Get all entities, optionally filtered by type."""
        conn = self._get_conn()
        
        try:
            if entity_type:
                cursor = conn.execute("""
                    SELECT id, type, name, content, metadata, tags, created_at, updated_at
                    FROM entity_data
                    WHERE type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (entity_type, limit))
            else:
                cursor = conn.execute("""
                    SELECT id, type, name, content, metadata, tags, created_at, updated_at
                    FROM entity_data
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                # Parse JSON metadata
                if data['metadata']:
                    data['metadata'] = json.loads(data['metadata'])
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get all entities: {e}")
            return []
    
    def get_relations_by_type(self, relation_type: str, limit: int = 100) -> List[MemoryRelation]:
        """Get relations by type."""
        conn = self._get_conn()
        
        try:
            cursor = conn.execute("""
                SELECT * FROM entity_relations 
                WHERE relation_type = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, [relation_type, limit])
            
            relations = []
            for row in cursor.fetchall():
                relation = MemoryRelation(
                    id=row['id'],
                    source_id=row['source_id'],
                    target_id=row['target_id'],
                    relation_type=row['relation_type'],
                    strength=row['strength'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                relations.append(relation)
            
            return relations
            
        except Exception as e:
            logger.error(f"Relation search failed: {e}")
            return []
    
    def save_context_with_ai(self, context: MemoryContext) -> MemoryContext:
        """Save context with AI enhancement."""
        # Save the context first
        saved_context = self.save_context(context)
        
        # Apply AI enhancement if available
        if self.enable_ai_extraction and self.content_enhancer:
            try:
                enhancement = self.content_enhancer.enhance_context(saved_context)
                
                # Update the context with enhancement data
                if enhancement.get('topics'):
                    saved_context.topics = enhancement['topics']
                if enhancement.get('summary'):
                    saved_context.summary = enhancement['summary']
                if enhancement.get('action_items'):
                    saved_context.metadata['action_items'] = enhancement['action_items']
                if enhancement.get('extracted_entities'):
                    saved_context.metadata['extracted_entities'] = enhancement['extracted_entities']
                if enhancement.get('extract_hash'):
                    saved_context.metadata['extract_hash'] = enhancement['extract_hash']
                
                # Save the enhanced context
                return self.save_context(saved_context)
            except Exception as e:
                logger.warning(f"AI enhancement failed for context {context.id}: {e}")
                return saved_context
        
        return saved_context
    
    def _build_context_filter_conditions(self, filters: Dict) -> tuple:
        """Build SQL WHERE conditions for context filters."""
        conditions = []
        params = []
        
        if not filters:
            return "", []
        
        # Context type filter
        if 'type' in filters:
            conditions.append("type = ?")
            params.append(filters['type'])
        
        if 'types' in filters:
            placeholders = ','.join(['?' for _ in filters['types']])
            conditions.append(f"type IN ({placeholders})")
            params.extend(filters['types'])
        
        # Date filters
        if 'created_after' in filters:
            conditions.append("created_at >= ?")
            params.append(filters['created_after'])
        
        if 'created_before' in filters:
            conditions.append("created_at <= ?")
            params.append(filters['created_before'])
        
        where_clause = ""
        if conditions:
            where_clause = " AND " + " AND ".join(conditions)
        
        return where_clause, params

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def check_pragma(self) -> Dict[str, Any]:
        """Check database capabilities and configuration."""
        conn = self._get_conn()
        
        try:
            # Check journal mode
            journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            
            # Check compile options
            compile_opts = {row[0] for row in conn.execute("PRAGMA compile_options")}
            
            # Check if tables exist
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('entities', 'entity_data', 'entity_relations', 'contexts')
            """)
            existing_tables = {row['name'] for row in cursor.fetchall()}
            
            # Check JSON validation pragma
            json_validation_result = conn.execute("PRAGMA json_validation").fetchone()
            json_validation = json_validation_result[0] if json_validation_result else 0
            
            # Check if JSON functions are available by testing a simple JSON operation
            try:
                conn.execute("SELECT json('{}')").fetchone()
                json_functions_work = True
            except sqlite3.OperationalError:
                json_functions_work = False
            
            return {
                "json_enabled": json_functions_work or json_validation == 1 or "ENABLE_JSON1" in compile_opts,
                "fts_enabled": "ENABLE_FTS5" in compile_opts,
                "vector_enabled": self.vector_enabled,
                "journal_mode": journal_mode,
                "tables_exist": {
                    "entities": "entities" in existing_tables,
                    "entity_data": "entity_data" in existing_tables,
                    "entity_relations": "entity_relations" in existing_tables,
                    "contexts": "contexts" in existing_tables,
                },
                "embedding_model": getattr(self.embedding_model, 'name', str(type(self.embedding_model))) if self.embedding_model else None,
                "embedding_dimension": self.embedding_dimension
            }
            
        except Exception as e:
            logger.error(f"Failed to check pragma: {e}")
            return {"error": str(e)}
    
    def close(self) -> None:
        """Close all database connections."""
        if hasattr(self._local, "conn"):
            self._local.conn.close()
            delattr(self._local, "conn")
        
        self.db_manager.disconnect()
        logger.info("UnifiedMemoryStore connections closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def _emit_workflow_event(self, entity: MemoryEntity = None, relation = None, context = None, entities: List[MemoryEntity] = None) -> None:
        """Emit a workflow event if workflow engine is available."""
        if not self.workflow_engine:
            return
            
        try:
            # Import Event here to avoid circular imports
            from workflows.engine import Event
            
            # Prepare event payload - can handle multiple entities
            payload = []
            
            # Single entity
            if entity:
                payload.append(entity.to_dict())
            
            
            # Other data types
            if relation:
                payload.append(relation.to_dict())
            if context:
                payload.append(context.to_dict())
            
            # Create and trigger event
            # For new trigger system, we don't rely on event_type as much
            event = Event(
                payload=payload,
                source="memory_store"
            )
            
            # Trigger event - WorkflowEngine now handles sync/async contexts
            self.workflow_engine.trigger_event(event)
            logger.debug(f"Emitted workflow event: {payload}")
            
        except Exception as e:
            # Don't let workflow event failures break memory operations
            logger.warning(f"Failed to emit workflow event {payload}: {e}")


def create_memory_store(data_dir: Union[str, Path], **kwargs) -> UnifiedMemoryStore:
    """Create a UnifiedMemoryStore instance with default configuration."""
    data_path = Path(data_dir)
    db_path = data_path / "unified_memory.db"
    
    return UnifiedMemoryStore(db_path, **kwargs)


# Convenience function for testing
def create_test_memory_store(**kwargs) -> UnifiedMemoryStore:
    """Create a UnifiedMemoryStore for testing."""
    import tempfile
    import os
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_memory.db"
    
    # Disable vector search for faster testing unless explicitly enabled
    if 'enable_vector_search' not in kwargs:
        kwargs['enable_vector_search'] = False
    
    return UnifiedMemoryStore(db_path, **kwargs) 