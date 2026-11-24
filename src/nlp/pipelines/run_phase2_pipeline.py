"""
Phase 2 Execution Pipeline
Loads sanitized corpus from Phase 1, runs Groq cognitive taxonomy classification,
generates BAAI BGE dense vector embeddings, and stores records in SQLite with hybrid BM25 index.
"""

import os
import sys
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.storage.db.database_manager import (
    initialize_database,
    insert_feedback_record,
    insert_classification_record,
    get_db_connection
)
from src.nlp.classifier.groq_classifier import GroqCognitiveClassifier
from src.storage.vector.bge_indexer import BGEHybridIndexer

DATA_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
SANITZED_CORPUS_PATH = os.path.join(DATA_BASE_DIR, "sanitized_discovery_corpus.json")
PHASE2_MANIFEST_PATH = os.path.join(DATA_BASE_DIR, "phase2_manifest.json")

STRUGGLE_KEYWORDS = [
    "math", "hint", "hints", "exercise", "practice", "wrong", "answer", "answers", 
    "explain", "explanation", "understand", "confus", "stuck", "question", "questions",
    "test", "quiz", "algebra", "learn", "solve", "step", "steps", "mistake", "error",
    "equation", "difficult", "hard", "problem", "frustrat", "give up", "quit", "help",
    "mastery", "prerequisite", "video", "fail", "score"
]

def run_phase2_pipeline(max_items_to_classify: int = 40):
    print("=" * 70)
    print("KHAN ACADEMY LEARNER EXPERIENCE: PHASE 2 CLASSIFICATION & STORAGE")
    print("=" * 70)
    start_time = time.time()

    # 1. Initialize SQLite database & FTS5
    print("\n[Step 1/5] Initializing Database & Full-Text Search Schema...")
    initialize_database()

    # 2. Load sanitized corpus from Phase 1
    print(f"\n[Step 2/5] Loading Sanitized Discovery Corpus from: {SANITZED_CORPUS_PATH}...")
    if not os.path.exists(SANITZED_CORPUS_PATH):
        raise FileNotFoundError(f"Corpus file not found: {SANITZED_CORPUS_PATH}")

    with open(SANITZED_CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    print(f"Loaded {len(corpus)} sanitized records.")

    # 3. Insert all feedback records into SQLite database
    print("\n[Step 3/5] Indexing all feedback records into SQLite & FTS5...")
    for rec in corpus:
        insert_feedback_record(rec)
    print(f"Successfully inserted {len(corpus)} records into database.")

    # 4. Filter high-signal learning struggle subset for classification & vector embeddings
    high_signal = []
    for r in corpus:
        text = r.get("sanitized_text", "").lower()
        if any(kw in text for kw in STRUGGLE_KEYWORDS) and len(text) >= 30:
            high_signal.append(r)

    print(f"Filtered {len(high_signal)} high-signal learner struggle records.")
    sample_to_process = high_signal[:max_items_to_classify]

    # 5. Classify via Groq with Pydantic validation
    print(f"\n[Step 4/5] Running Groq LLM cognitive classification on {len(sample_to_process)} records...")
    classifier = GroqCognitiveClassifier()
    batch_size = 4
    classified_items = []

    for i in range(0, len(sample_to_process), batch_size):
        batch = sample_to_process[i:i + batch_size]
        print(f"  Classifying batch {i//batch_size + 1}/{(len(sample_to_process) + batch_size - 1)//batch_size}...")
        results = classifier.classify_batch(batch)
        for c in results:
            item_dict = c.model_dump()
            item_dict["classified_at"] = datetime.utcnow().isoformat()
            classified_items.append(item_dict)
            insert_classification_record(item_dict)
        time.sleep(1)

    print(f"Classified and stored {len(classified_items)} cognitive records.")

    # 6. Generate BAAI BGE vector embeddings & store
    print(f"\n[Step 5/5] Generating BAAI BGE embeddings (bge-small-en-v1.5) for {len(sample_to_process)} records...")
    indexer = BGEHybridIndexer()
    indexer.index_records(sample_to_process)

    # 7. Test Hybrid Search Query
    test_query = "why hints do not explain why my linear equation answer is wrong"
    print(f"\nTesting hybrid search query (BM25 + BGE Vector RRF): '{test_query}'...")
    search_results = indexer.search_hybrid(test_query, top_k=3)
    print(f"Hybrid search returned {len(search_results)} relevant matches:")
    for rank, res in enumerate(search_results, 1):
        print(f"  #{rank} [RRF: {res['rrf_score']}] ID: {res['record_id']} | Source: {res['source']}")
        print(f"     Excerpt: {res['sanitized_text'][:100]}...")

    # Manifest
    duration = round(time.time() - start_time, 2)
    manifest = {
        "pipeline_phase": "Phase 2",
        "execution_timestamp": datetime.utcnow().isoformat(),
        "total_corpus_indexed": len(corpus),
        "high_signal_filtered": len(high_signal),
        "classified_count": len(classified_items),
        "vector_embeddings_indexed": len(sample_to_process),
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "embedding_dimensions": 384,
        "llm_classifier": "Groq (Qwen 2.5 27B / GPT-OSS 120B)",
        "duration_seconds": duration
    }

    with open(PHASE2_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 70)
    print(f"PHASE 2 COMPLETED SUCCESSFULLY in {duration}s")
    print(f"Manifest written to: {PHASE2_MANIFEST_PATH}")
    print("=" * 70)

    return manifest

if __name__ == "__main__":
    run_phase2_pipeline(max_items_to_classify=36)
