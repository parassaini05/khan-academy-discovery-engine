"""
BAAI BGE Vector Indexer & Hybrid Search Engine
Generates 384-dimensional dense vectors using FastEmbed (bge-small-en-v1.5)
and implements Reciprocal Rank Fusion (RRF) combining BM25 keyword search with dense vector cosine similarity.
"""

from typing import List, Dict, Any, Tuple
from fastembed import TextEmbedding
from src.storage.db.database_manager import (
    insert_vector_embedding,
    search_bm25,
    search_vector_cosine
)

BGE_MODEL_NAME = "BAAI/bge-small-en-v1.5"
QUERY_INSTRUCTION_PREFIX = "Represent this sentence for searching relevant passages: "

class BGEHybridIndexer:
    def __init__(self, model_name: str = BGE_MODEL_NAME):
        self.model_name = model_name
        self.embedder = TextEmbedding(model_name=model_name)

    def index_records(self, records: List[Dict[str, Any]]):
        """Generates and persists BGE embeddings for a list of learner records."""
        if not records:
            return

        texts = [r.get("sanitized_text", "") for r in records]
        embeddings = list(self.embedder.embed(texts))

        for idx, r in enumerate(records):
            rid = r.get("record_id") or r.get("external_id")
            vec = embeddings[idx].tolist() if hasattr(embeddings[idx], "tolist") else list(embeddings[idx])
            insert_vector_embedding(rid, vec, model_name=self.model_name)

        print(f"[BGE Indexer] Indexed {len(records)} records into vector database.")

    def embed_query(self, query: str) -> List[float]:
        """Generates embedding for a search query using the recommended BGE instruction prefix."""
        prefixed_query = f"{QUERY_INSTRUCTION_PREFIX}{query}"
        emb = list(self.embedder.embed([prefixed_query]))[0]
        return emb.tolist() if hasattr(emb, "tolist") else list(emb)

    def search_hybrid(self, query: str, top_k: int = 15, rrf_k: int = 60) -> List[Dict[str, Any]]:
        """
        Executes Reciprocal Rank Fusion (RRF) combining:
        1. BM25 keyword search from SQLite FTS5
        2. BGE vector cosine similarity
        """
        # 1. BM25 search
        bm25_results = search_bm25(query, limit=top_k * 2)
        
        # 2. Vector search
        q_vec = self.embed_query(query)
        vector_results = search_vector_cosine(q_vec, limit=top_k * 2)

        # 3. Reciprocal Rank Fusion calculation
        rrf_scores: Dict[str, float] = {}
        items_by_id: Dict[str, Dict[str, Any]] = {}

        for rank, item in enumerate(bm25_results):
            rid = item["record_id"]
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + (1.0 / (rrf_k + rank + 1))
            items_by_id[rid] = item

        for rank, (item, cos_sim) in enumerate(vector_results):
            rid = item["record_id"]
            rrf_scores[rid] = rrf_scores.get(rid, 0.0) + (1.0 / (rrf_k + rank + 1))
            if rid not in items_by_id:
                items_by_id[rid] = item
            items_by_id[rid]["cosine_similarity"] = round(cos_sim, 4)

        # Sort by merged RRF score
        ranked_rids = sorted(rrf_scores.keys(), key=lambda rid: rrf_scores[rid], reverse=True)

        final_results = []
        for rid in ranked_rids[:top_k]:
            merged_item = items_by_id[rid]
            merged_item["rrf_score"] = round(rrf_scores[rid], 5)
            final_results.append(merged_item)

        return final_results
