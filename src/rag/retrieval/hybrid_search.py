"""
Hybrid Retrieval Engine for PM Discovery Workbench
Combines SQLite FTS5 BM25 keyword search with BAAI BGE vector cosine similarity using Reciprocal Rank Fusion (RRF).
"""

import os
import sys
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.storage.db.database_manager import (
    search_bm25,
    search_vector_cosine,
    get_db_connection
)
from src.storage.vector.bge_indexer import BGEHybridIndexer

class HybridRetrievalEngine:
    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.indexer = BGEHybridIndexer()

    def search(
        self,
        query: str,
        top_k: int = 15,
        source_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid search across normalized learner feedback.
        Applies BM25 full-text matching and BGE dense vector similarity.
        """
        # 1. BM25 Search
        bm25_matches = search_bm25(query, limit=top_k * 3)

        # 2. Vector Cosine Search
        query_vector = self.indexer.embed_query(query)
        vector_matches = search_vector_cosine(query_vector, limit=top_k * 3)

        # 3. Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        items_map: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(bm25_matches):
            rid = item["record_id"]
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            items_map[rid] = item

        for rank, (item, cos_sim) in enumerate(vector_matches):
            rid = item["record_id"]
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
            if rid not in items_map:
                items_map[rid] = item
            items_map[rid]["cosine_similarity"] = round(cos_sim, 4)

        # 4. Filter and rank
        ranked_rids = sorted(rrf_scores.keys(), key=lambda rid: rrf_scores[rid], reverse=True)

        results = []
        for rid in ranked_rids:
            item = items_map[rid]
            # Optional Source filter
            if source_filter and item.get("source") != source_filter:
                continue
            # Optional Category filter
            if category_filter and item.get("primary_category") != category_filter:
                continue

            item["rrf_score"] = round(rrf_scores[rid], 5)
            results.append(item)
            if len(results) >= top_k:
                break

        return results

if __name__ == "__main__":
    engine = HybridRetrievalEngine()
    test_q = "frustrated with linear equation hints"
    matches = engine.search(test_q, top_k=5)
    print(f"Query: '{test_q}' -> {len(matches)} results:")
    for m in matches:
        print(f"- [{m.get('source')}] {m.get('record_id')}: {m.get('sanitized_text')[:90]}...")
