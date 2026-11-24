-- Migration 001: Initial Feedback, Cognitive Classification and Vector Schema
-- Target: PostgreSQL 16 with pgvector extension (or compatible relational stores)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Raw Sanitized Learner Feedback Table
CREATE TABLE IF NOT EXISTS learner_feedback (
    record_id VARCHAR(128) PRIMARY KEY,
    source VARCHAR(32) NOT NULL,
    external_id VARCHAR(128) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE,
    author_pseudonym VARCHAR(128),
    rating INTEGER,
    title TEXT,
    sanitized_text TEXT NOT NULL,
    context_url TEXT,
    upvotes_or_likes INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feedback_source ON learner_feedback(source);
CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON learner_feedback(timestamp);

-- 2. Cognitive Classification Table
CREATE TABLE IF NOT EXISTS cognitive_classifications (
    classification_id VARCHAR(128) PRIMARY KEY,
    record_id VARCHAR(128) NOT NULL REFERENCES learner_feedback(record_id) ON DELETE CASCADE,
    primary_category VARCHAR(64) NOT NULL,
    observed_behavior VARCHAR(64) NOT NULL,
    frustration_score NUMERIC(3, 2) NOT NULL,
    abandonment_risk VARCHAR(16) NOT NULL,
    struggle_topic VARCHAR(128),
    verbatim_struggle_quote TEXT,
    confidence_score NUMERIC(3, 2) DEFAULT 0.90,
    llm_model VARCHAR(64) NOT NULL,
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_classification_category ON cognitive_classifications(primary_category);
CREATE INDEX IF NOT EXISTS idx_classification_behavior ON cognitive_classifications(observed_behavior);
CREATE INDEX IF NOT EXISTS idx_classification_risk ON cognitive_classifications(abandonment_risk);

-- 3. BAAI BGE Vector Embeddings Table
CREATE TABLE IF NOT EXISTS feedback_embeddings (
    record_id VARCHAR(128) PRIMARY KEY REFERENCES learner_feedback(record_id) ON DELETE CASCADE,
    model_name VARCHAR(64) NOT NULL DEFAULT 'BAAI/bge-small-en-v1.5',
    dimensions INTEGER NOT NULL DEFAULT 384,
    embedding_vector vector(384) NOT NULL,
    indexed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw ON feedback_embeddings USING hnsw (embedding_vector vector_cosine_ops);
