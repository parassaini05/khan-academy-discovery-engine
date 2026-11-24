"""
Google Play Store Connector for Khan Academy
Fetches reviews across ratings and recency, focusing on practice and learning friction.
"""

import sys
from typing import List, Dict, Any
from datetime import datetime
from google_play_scraper import reviews, Sort

PACKAGE_NAME = "org.khanacademy.android"

def fetch_playstore_records(max_per_rating: int = 50) -> List[Dict[str, Any]]:
    """Fetches and normalizes Google Play Store reviews for Khan Academy."""
    records = []
    seen_ids = set()
    
    # 1. Fetch filtered ratings (focus on 1, 2, 3 stars for struggle analysis)
    for score in [1, 2, 3]:
        try:
            res, _ = reviews(
                PACKAGE_NAME,
                lang='en',
                country='us',
                sort=Sort.MOST_RELEVANT,
                count=max_per_rating,
                filter_score_with=score
            )
            for r in res:
                rid = r.get("reviewId")
                if rid and rid not in seen_ids:
                    seen_ids.add(rid)
                    records.append({
                        "source": "playstore",
                        "external_id": str(rid),
                        "timestamp": r.get("at").isoformat() if hasattr(r.get("at"), "isoformat") else str(r.get("at")),
                        "author_pseudonym": r.get("userName") or "PlayStore_User",
                        "rating": r.get("score"),
                        "title": None,
                        "raw_text": (r.get("content") or "").strip(),
                        "context_url": f"https://play.google.com/store/apps/details?id={PACKAGE_NAME}&reviewId={rid}",
                        "upvotes_or_likes": r.get("thumbsUpCount", 0),
                        "metadata": {
                            "app_version": r.get("reviewCreatedVersion"),
                            "reply_content": r.get("replyContent")
                        }
                    })
        except Exception as e:
            print(f"[PlayStore Connector] Warning for score {score}: {e}")

    # 2. Fetch newest reviews
    try:
        newest, _ = reviews(
            PACKAGE_NAME,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=max_per_rating
        )
        for r in newest:
            rid = r.get("reviewId")
            if rid and rid not in seen_ids:
                seen_ids.add(rid)
                records.append({
                    "source": "playstore",
                    "external_id": str(rid),
                    "timestamp": r.get("at").isoformat() if hasattr(r.get("at"), "isoformat") else str(r.get("at")),
                    "author_pseudonym": r.get("userName") or "PlayStore_User",
                    "rating": r.get("score"),
                    "title": None,
                    "raw_text": (r.get("content") or "").strip(),
                    "context_url": f"https://play.google.com/store/apps/details?id={PACKAGE_NAME}&reviewId={rid}",
                    "upvotes_or_likes": r.get("thumbsUpCount", 0),
                    "metadata": {
                        "app_version": r.get("reviewCreatedVersion")
                    }
                })
    except Exception as e:
        print(f"[PlayStore Connector] Warning for newest: {e}")

    print(f"[PlayStore Connector] Ingested {len(records)} normalized reviews.")
    return records
