"""
Daily Discovery Ingestion Pipeline
Orchestrates multi-source ingestion, PII sanitization, deduplication, and partitioned data storage.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.ingestion.connectors.playstore_connector import fetch_playstore_records
from src.ingestion.connectors.reddit_connector import fetch_reddit_records
from src.ingestion.connectors.appstore_connector import fetch_appstore_records
from src.ingestion.connectors.youtube_connector import fetch_youtube_records
from src.ingestion.connectors.forum_connector import fetch_forum_records
from src.ingestion.sanitizer.pii_redactor import redact_pii, is_valid_learner_text
from src.ingestion.sanitizer.deduplicator import Deduplicator

DATA_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
RAW_BASE_DIR = os.path.join(DATA_BASE_DIR, "raw")
CONSOLIDATED_OUTPUT = os.path.join(DATA_BASE_DIR, "sanitized_discovery_corpus.json")
RUN_MANIFEST_PATH = os.path.join(DATA_BASE_DIR, "ingestion_manifest.json")

def save_partitioned_records(source: str, records: List[Dict[str, Any]]):
    """Saves records partitioned by source/YYYY/MM/DD."""
    now = datetime.utcnow()
    partition_path = os.path.join(
        RAW_BASE_DIR,
        source,
        now.strftime("%Y"),
        now.strftime("%m"),
        now.strftime("%d")
    )
    os.makedirs(partition_path, exist_ok=True)
    file_path = os.path.join(partition_path, "records.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(records, f, default=str, indent=2)
    return file_path

def run_daily_ingestion_pipeline(crawl_live_reddit: bool = False) -> Dict[str, Any]:
    """Runs end-to-end multi-source ingestion, sanitization, and partitioning."""
    print("=" * 70)
    print("KHAN ACADEMY LEARNER EXPERIENCE: PHASE 1 INGESTION PIPELINE")
    print("Timestamp:", datetime.utcnow().isoformat())
    print("=" * 70)

    start_time = time.time()
    manifest = {
        "pipeline_version": "1.0.0",
        "run_timestamp": datetime.utcnow().isoformat(),
        "sources_harvested": {},
        "total_raw_collected": 0,
        "valid_text_count": 0,
        "duplicates_pruned": 0,
        "sanitized_corpus_count": 0,
        "pii_redactions_total": {
            "emails": 0,
            "phones": 0,
            "ips": 0,
            "urls": 0,
            "usernames": 0,
            "teachers_schools": 0,
            "names": 0
        },
        "execution_duration_sec": 0.0
    }

    # 1. Harvest from all 5 connectors with error isolation
    raw_by_source = {}

    print("\n[Step 1/4] Harvesting from Source Connectors...")
    
    # 1a. Google Play Store
    try:
        raw_play = fetch_playstore_records(max_per_rating=50)
        raw_by_source["playstore"] = raw_play
        manifest["sources_harvested"]["playstore"] = len(raw_play)
    except Exception as e:
        print(f"[Ingestion Error - PlayStore]: {e}")
        raw_by_source["playstore"] = []

    # 1b. Reddit Discussions
    try:
        raw_reddit = fetch_reddit_records(max_posts=25, crawl_live=crawl_live_reddit)
        raw_by_source["reddit"] = raw_reddit
        manifest["sources_harvested"]["reddit"] = len(raw_reddit)
    except Exception as e:
        print(f"[Ingestion Error - Reddit]: {e}")
        raw_by_source["reddit"] = []

    # 1c. Apple App Store
    try:
        raw_appstore = fetch_appstore_records(max_pages=3)
        raw_by_source["appstore"] = raw_appstore
        manifest["sources_harvested"]["appstore"] = len(raw_appstore)
    except Exception as e:
        print(f"[Ingestion Error - AppStore]: {e}")
        raw_by_source["appstore"] = []

    # 1d. YouTube Comments
    try:
        raw_yt = fetch_youtube_records(max_comments=40)
        raw_by_source["youtube"] = raw_yt
        manifest["sources_harvested"]["youtube"] = len(raw_yt)
    except Exception as e:
        print(f"[Ingestion Error - YouTube]: {e}")
        raw_by_source["youtube"] = []

    # 1e. Khan Community Forums
    try:
        raw_forum = fetch_forum_records(max_threads=20)
        raw_by_source["forum"] = raw_forum
        manifest["sources_harvested"]["forum"] = len(raw_forum)
    except Exception as e:
        print(f"[Ingestion Error - Forum]: {e}")
        raw_by_source["forum"] = []

    total_raw = sum(len(v) for v in raw_by_source.values())
    manifest["total_raw_collected"] = total_raw
    print(f"\nTotal raw records collected across 5 sources: {total_raw}")

    # 2. Partition & Persist Raw Data
    print("\n[Step 2/4] Persisting Partitioned Raw Data Lake...")
    for source, records in raw_by_source.items():
        if records:
            p_file = save_partitioned_records(source, records)
            print(f"  - Partitioned {len(records)} {source} records to: {p_file}")

    # 3. Content Validation & Deduplication
    print("\n[Step 3/4] Validating Text & Pruning Duplicates...")
    deduplicator = Deduplicator(jaccard_threshold=0.85)
    all_raw_list = []
    for records in raw_by_source.values():
        all_raw_list.extend(records)

    valid_records = []
    for r in all_raw_list:
        raw_text = r.get("raw_text", "")
        if is_valid_learner_text(raw_text, min_words=8):
            valid_records.append(r)

    manifest["valid_text_count"] = len(valid_records)
    print(f"  - Valid text records passed character density check: {len(valid_records)} / {total_raw}")

    unique_records = deduplicator.deduplicate_batch(valid_records)
    duplicates_removed = len(valid_records) - len(unique_records)
    manifest["duplicates_pruned"] = duplicates_removed
    print(f"  - Duplicates pruned: {duplicates_removed}. Distinct items remaining: {len(unique_records)}")

    # 4. COPPA/FERPA PII Sanitization
    print("\n[Step 4/4] Executing COPPA/FERPA PII Sanitization...")
    sanitized_corpus = []
    total_pii_counts = manifest["pii_redactions_total"]

    for r in unique_records:
        clean_text, pii_counts = redact_pii(r.get("raw_text", ""))
        clean_author, author_counts = redact_pii(r.get("author_pseudonym", "Learner"))
        clean_title, _ = redact_pii(r.get("title", "") or "")

        for k, v in pii_counts.items():
            total_pii_counts[k] += v

        sanitized_item = {
            "record_id": f"{r['source']}_{r['external_id']}",
            "source": r["source"],
            "external_id": r["external_id"],
            "timestamp": r["timestamp"],
            "sanitized_author": clean_author,
            "rating": r.get("rating"),
            "title": clean_title or None,
            "sanitized_text": clean_text,
            "context_url": r.get("context_url"),
            "upvotes_or_likes": r.get("upvotes_or_likes", 0),
            "metadata": r.get("metadata", {}),
            "pii_redaction_flags": pii_counts
        }
        sanitized_corpus.append(sanitized_item)

    manifest["sanitized_corpus_count"] = len(sanitized_corpus)
    manifest["execution_duration_sec"] = round(time.time() - start_time, 2)

    # 5. Persist Sanitized Corpus & Manifest
    os.makedirs(DATA_BASE_DIR, exist_ok=True)
    with open(CONSOLIDATED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(sanitized_corpus, f, indent=2)
    print(f"\nPersisted sanitized discovery corpus ({len(sanitized_corpus)} items) to:")
    print(f"  -> {CONSOLIDATED_OUTPUT}")

    with open(RUN_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Persisted ingestion manifest to: {RUN_MANIFEST_PATH}")

    print("\n" + "=" * 70)
    print(f"PHASE 1 INGESTION COMPLETE in {manifest['execution_duration_sec']}s")
    print(f"Harvested: {manifest['total_raw_collected']} | Sanitized Corpus: {manifest['sanitized_corpus_count']}")
    print(f"PII Redactions Applied: {sum(manifest['pii_redactions_total'].values())}")
    print("=" * 70)

    return manifest

if __name__ == "__main__":
    run_daily_ingestion_pipeline(crawl_live_reddit=False)
