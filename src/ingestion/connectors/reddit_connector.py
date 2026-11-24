"""
Reddit Connector for Khan Academy
Extracts posts and comments from r/Khan and r/learnmath via Apify Actor harshmaur/reddit-scraper.
"""

import os
from typing import List, Dict, Any
from apify_client import ApifyClient

from dotenv import load_dotenv
load_dotenv()

DEFAULT_APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
PRE_HARVESTED_DATASET_ID = "XIbxRvOBmWPTzJ1li"

def fetch_reddit_records(
    max_posts: int = 25, 
    crawl_live: bool = False,
    apify_token: str = DEFAULT_APIFY_TOKEN
) -> List[Dict[str, Any]]:
    """Fetches normalized Reddit discussions and comments."""
    client = ApifyClient(apify_token)
    records = []

    try:
        if crawl_live:
            print("[Reddit Connector] Triggering live Apify actor crawl...")
            run_input = {
                "searchComments": True,
                "searchSort": "new",
                "searchTime": "all",
                "startUrls": [
                    {"url": "https://www.reddit.com/r/Khan/"},
                    {"url": "https://www.reddit.com/r/Khan/search/?q=math+practice+stuck&sort=relevance"},
                    {"url": "https://www.reddit.com/r/learnmath/search/?q=khan+academy+algebra&sort=relevance"}
                ],
                "crawlCommentsPerPost": True,
                "maxPostsCount": max_posts,
                "maxCommentsCount": 100,
                "maxCommentsPerPost": 15
            }
            run = client.actor("harshmaur/reddit-scraper").call(run_input=run_input)
            dataset_id = run.default_dataset_id
        else:
            print(f"[Reddit Connector] Loading harvested Apify dataset ({PRE_HARVESTED_DATASET_ID})...")
            dataset_id = PRE_HARVESTED_DATASET_ID

        for item in client.dataset(dataset_id).iterate_items():
            title = (item.get("title") or "").strip()
            body = (item.get("body") or "").strip()
            text = f"{title}\n{body}".strip() if title else body
            
            if not text or len(text) < 20:
                continue

            records.append({
                "source": "reddit",
                "external_id": str(item.get("id")),
                "timestamp": item.get("createdAt") or item.get("crawledAt"),
                "author_pseudonym": item.get("authorName") or "Reddit_Learner",
                "rating": None,
                "title": title if title else None,
                "raw_text": text,
                "context_url": item.get("postUrl"),
                "upvotes_or_likes": item.get("upVotes", 0),
                "metadata": {
                    "community": item.get("communityName") or "r/Khan",
                    "data_type": item.get("dataType", "post"),
                    "num_comments": item.get("commentsCount", 0)
                }
            })

    except Exception as e:
        print(f"[Reddit Connector] Error fetching Reddit data: {e}")

    print(f"[Reddit Connector] Ingested {len(records)} normalized Reddit items.")
    return records
