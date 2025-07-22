-- Unified Memory Architecture Database Schema
-- Phase 1.1: Database Schema & Core Models

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Enable JSON functions (SQLite 3.38+)
PRAGMA json_validation = ON;

-- entities - Primary entity registry
CREATE TABLE entities (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- entity_data - Entity metadata and content
CREATE TABLE entity_data (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    content TEXT,
    metadata JSON,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- entity_relations - Relationships between entities
CREATE TABLE entity_relations (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- contexts - Conversation/session data
CREATE TABLE contexts (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    topics TEXT,
    entity_ids TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for entity_data
CREATE INDEX idx_entity_data_type_created ON entity_data(type, created_at);
CREATE INDEX idx_entity_data_tags ON entity_data(tags);
CREATE INDEX idx_entity_data_name ON entity_data(name);

-- Indexes for entity_relations
CREATE INDEX idx_entity_relations_source ON entity_relations(source_id);
CREATE INDEX idx_entity_relations_target ON entity_relations(target_id);
CREATE INDEX idx_entity_relations_type ON entity_relations(relation_type);

-- Indexes for contexts
CREATE INDEX idx_contexts_type_created ON contexts(type, created_at); 