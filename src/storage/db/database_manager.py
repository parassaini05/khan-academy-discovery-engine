"""
Database Manager for Learner Discovery Engine
Provides SQLite-based relational storage, FTS5 full-text BM25 search, and vector storage.
"""

import sqlite3
import json
import os
import math
import re
from typing import List, Dict, Any, Optional, Tuple

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/discovery_database.sqlite"))

def get_db_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initializes SQLite tables for feedback, classifications, vector embeddings, and FTS5 search."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learner_feedback (
        record_id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        external_id TEXT NOT NULL,
        timestamp TEXT,
        author_pseudonym TEXT,
        rating INTEGER,
        title TEXT,
        sanitized_text TEXT NOT NULL,
        context_url TEXT,
        upvotes_or_likes INTEGER DEFAULT 0,
        metadata_json TEXT
    );
    """)

    # 2. Cognitive Classifications Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cognitive_classifications (
        classification_id TEXT PRIMARY KEY,
        record_id TEXT NOT NULL,
        primary_category TEXT NOT NULL,
        observed_behavior TEXT NOT NULL,
        frustration_score REAL NOT NULL,
        abandonment_risk TEXT NOT NULL,
        struggle_topic TEXT,
        verbatim_struggle_quote TEXT,
        confidence_score REAL DEFAULT 0.90,
        llm_model TEXT NOT NULL,
        classified_at TEXT NOT NULL,
        FOREIGN KEY (record_id) REFERENCES learner_feedback(record_id) ON DELETE CASCADE
    );
    """)

    # 3. Vector Embeddings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback_embeddings (
        record_id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        dimensions INTEGER NOT NULL,
        embedding_json TEXT NOT NULL,
        FOREIGN KEY (record_id) REFERENCES learner_feedback(record_id) ON DELETE CASCADE
    );
    """)

    # 4. FTS5 Virtual Table for BM25 Search
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS feedback_fts USING fts5(
        record_id UNINDEXED,
        title,
        sanitized_text,
        tokenize = 'porter ascii'
    );
    """)

    conn.commit()
    conn.close()
    print(f"[Database Manager] Initialized database schema at: {DB_PATH}")

def insert_feedback_record(record: Dict[str, Any]):
    """Inserts or replaces a feedback record and updates the FTS index."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO learner_feedback 
    (record_id, source, external_id, timestamp, author_pseudonym, rating, title, sanitized_text, context_url, upvotes_or_likes, metadata_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["record_id"],
        record["source"],
        record["external_id"],
        record.get("timestamp"),
        record.get("sanitized_author") or record.get("author_pseudonym"),
        record.get("rating"),
        record.get("title"),
        record["sanitized_text"],
        record.get("context_url"),
        record.get("upvotes_or_likes", 0),
        json.dumps(record.get("metadata", {}))
    ))

    # Update FTS5
    cursor.execute("DELETE FROM feedback_fts WHERE record_id = ?", (record["record_id"],))
    cursor.execute("""
    INSERT INTO feedback_fts (record_id, title, sanitized_text)
    VALUES (?, ?, ?)
    """, (
        record["record_id"],
        record.get("title") or "",
        record["sanitized_text"]
    ))

    conn.commit()
    conn.close()

def insert_classification_record(classification: Dict[str, Any]):
    """Inserts or replaces a cognitive classification record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO cognitive_classifications
    (classification_id, record_id, primary_category, observed_behavior, frustration_score, abandonment_risk, struggle_topic, verbatim_struggle_quote, confidence_score, llm_model, classified_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        classification.get("classification_id") or f"cls_{classification['record_id']}",
        classification["record_id"],
        classification["primary_category"],
        classification["observed_behavior"],
        classification["frustration_score"],
        classification["abandonment_risk"],
        classification.get("struggle_topic"),
        classification.get("verbatim_struggle_quote"),
        classification.get("confidence_score", 0.90),
        classification.get("llm_model", "Groq-Qwen-27B"),
        classification.get("classified_at")
    ))

    conn.commit()
    conn.close()

def insert_vector_embedding(record_id: str, embedding: List[float], model_name: str = "BAAI/bge-small-en-v1.5"):
    """Stores the dense vector embedding for a record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO feedback_embeddings
    (record_id, model_name, dimensions, embedding_json)
    VALUES (?, ?, ?, ?)
    """, (
        record_id,
        model_name,
        len(embedding),
        json.dumps(embedding)
    ))

    conn.commit()
    conn.close()

def search_bm25(query_terms: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Performs full-text BM25 search across learner feedback with sanitized FTS5 expression."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clean special characters that break SQLite FTS5 syntax (. ? - * " etc.)
    clean_terms = re.sub(r'[^\w\s]', ' ', query_terms).strip()
    tokens = [t for t in clean_terms.split() if len(t) >= 2 and not t.isdigit()]
    if not tokens:
        conn.close()
        return []

    # Construct safe OR query over tokens
    fts_expr = " OR ".join(tokens[:8])

    try:
        cursor.execute("""
        SELECT f.*, bm25(feedback_fts) as rank
        FROM feedback_fts fts
        JOIN learner_feedback f ON fts.record_id = f.record_id
        WHERE feedback_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """, (fts_expr, limit))
        rows = [dict(r) for r in cursor.fetchall()]
    except Exception as e:
        print(f"[Database Manager] FTS5 search error: {e}")
        rows = []

    conn.close()
    return rows

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)

def search_vector_cosine(query_vector: List[float], limit: int = 20) -> List[Tuple[Dict[str, Any], float]]:
    """Performs brute-force exact cosine similarity search over stored BGE embeddings."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT e.record_id, e.embedding_json, f.*, c.primary_category, c.frustration_score
    FROM feedback_embeddings e
    JOIN learner_feedback f ON e.record_id = f.record_id
    LEFT JOIN cognitive_classifications c ON f.record_id = c.record_id
    """)

    results = []
    for r in cursor.fetchall():
        vec = json.loads(r["embedding_json"])
        sim = cosine_similarity(query_vector, vec)
        results.append((dict(r), sim))

    conn.close()
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]
