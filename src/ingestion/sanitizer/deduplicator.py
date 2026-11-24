"""
Deduplication Engine for Learner Feedback
Prunes exact and near-duplicate cross-posts, bot spam, and repetitive reviews.
"""

import hashlib
import re
from typing import List, Dict, Any, Set, Tuple

def normalize_text_for_hash(text: str) -> str:
    """Normalizes whitespace, lowercases, and removes punctuation for robust duplicate matching."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def compute_content_hash(text: str) -> str:
    """Computes SHA-256 fingerprint of normalized text."""
    normalized = normalize_text_for_hash(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

class Deduplicator:
    def __init__(self, jaccard_threshold: float = 0.85):
        self.seen_exact_hashes: Set[str] = set()
        self.seen_token_sets: List[Tuple[str, Set[str]]] = []
        self.jaccard_threshold = jaccard_threshold

    def is_duplicate(self, record_id: str, text: str) -> bool:
        """Determines if a record is an exact or near duplicate of an existing record."""
        # 1. Exact normalized hash match
        c_hash = compute_content_hash(text)
        if c_hash in self.seen_exact_hashes:
            return True

        # 2. Token Jaccard near-duplicate match
        tokens = set(normalize_text_for_hash(text).split())
        if len(tokens) >= 8:  # Only evaluate near-duplicates for substantial texts
            for existing_id, existing_tokens in self.seen_token_sets:
                intersection = len(tokens.intersection(existing_tokens))
                union = len(tokens.union(existing_tokens))
                if union > 0 and (intersection / union) >= self.jaccard_threshold:
                    return True

        # Register novel record
        self.seen_exact_hashes.add(c_hash)
        if len(tokens) >= 8:
            self.seen_token_sets.append((record_id, tokens))

        return False

    def deduplicate_batch(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters a batch of records, retaining only distinct, high-signal entries."""
        unique_records = []
        for r in records:
            rid = r.get("external_id", "unknown")
            text = r.get("raw_text", "")
            if not self.is_duplicate(rid, text):
                unique_records.append(r)
        return unique_records
