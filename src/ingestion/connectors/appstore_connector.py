"""
Apple App Store Connector for Khan Academy
Fetches public iOS customer reviews via Apple's official RSS JSON API.
App ID: 469863705 (Khan Academy on iOS)
"""

import requests
from typing import List, Dict, Any
from datetime import datetime

APP_ID = "469863705"
BASE_URL = f"https://itunes.apple.com/us/rss/customerreviews/id={APP_ID}/sortBy=mostRecent/json"

def fetch_appstore_records(max_pages: int = 3) -> List[Dict[str, Any]]:
    """Fetches and normalizes Apple App Store reviews for Khan Academy."""
    records = []
    seen_ids = set()

    for page in range(1, max_pages + 1):
        try:
            page_url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={APP_ID}/sortBy=mostRecent/json"
            response = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if response.status_code != 200:
                break

            data = response.json()
            feed = data.get("feed", {})
            entries = feed.get("entry", [])

            for entry in entries:
                # First entry can sometimes be metadata about the app
                review_id = entry.get("id", {}).get("label")
                if not review_id or review_id in seen_ids:
                    continue

                seen_ids.add(review_id)
                title = entry.get("title", {}).get("label", "")
                content = entry.get("content", {}).get("label", "")
                author = entry.get("author", {}).get("name", {}).get("label", "AppStore_Learner")
                rating_str = entry.get("im:rating", {}).get("label", "0")
                version = entry.get("im:version", {}).get("label", "unknown")
                updated = entry.get("updated", {}).get("label", "")

                text = f"{title}\n{content}".strip() if title else content

                records.append({
                    "source": "appstore",
                    "external_id": str(review_id),
                    "timestamp": updated or datetime.utcnow().isoformat(),
                    "author_pseudonym": author,
                    "rating": int(rating_str) if rating_str.isdigit() else None,
                    "title": title or None,
                    "raw_text": text,
                    "context_url": f"https://apps.apple.com/us/app/khan-academy/id{APP_ID}",
                    "upvotes_or_likes": 0,
                    "metadata": {
                        "app_version": version
                    }
                })

        except Exception as e:
            print(f"[AppStore Connector] Warning for page {page}: {e}")
            break

    print(f"[AppStore Connector] Ingested {len(records)} normalized iOS reviews.")
    return records
