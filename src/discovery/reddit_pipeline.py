"""
Reddit Discovery Pipeline using Apify Reddit Scraper Dataset
Filters high-signal learner struggle discussions from r/Khan and r/learnmath,
classifies with Groq LLM, generates BAAI BGE vector embeddings,
and merges into the multi-source discovery database.
"""

import os
import json
import time
import re
from apify_client import ApifyClient
from openai import OpenAI
from fastembed import TextEmbedding

from dotenv import load_dotenv
load_dotenv()

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DATASET_ID = "XIbxRvOBmWPTzJ1li"  # From our successful scraper run
OUTPUT_DATA_DIR = "d:/Khan Academy - Portfolio/data"

client = ApifyClient(APIFY_TOKEN)
groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-120b"

print("1. Fetching dataset items from Apify dataset:", DATASET_ID)
items = list(client.dataset(DATASET_ID).iterate_items())
print(f"Retrieved {len(items)} items from Apify dataset.")

# Save raw items
os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
with open(os.path.join(OUTPUT_DATA_DIR, "raw_reddit_items.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, default=str, indent=2)

def sanitize_text(text: str) -> str:
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
    text = re.sub(r'u\/[A-Za-z0-9_-]+', '[REDACTED_USER]', text)
    text = re.sub(r'https?://\S+', '[REDACTED_URL]', text)
    return text.strip()

STRUGGLE_KEYWORDS = [
    "math", "hint", "hints", "exercise", "practice", "wrong", "answer", "answers", 
    "explain", "explanation", "understand", "confus", "stuck", "question", "questions",
    "test", "quiz", "algebra", "learn", "solve", "step", "steps", "mistake", "error",
    "equation", "difficult", "hard", "problem", "frustrat", "give up", "quit", "help",
    "mastery", "prerequisite", "video", "fail", "score"
]

filtered_reddit = []
seen_texts = set()

for it in items:
    title = it.get("title", "") or ""
    body = it.get("body", "") or ""
    full_text = f"{title}\n{body}".strip() if title else body.strip()
    
    if len(full_text) < 40 or full_text in seen_texts:
        continue
    
    full_text_lower = full_text.lower()
    if any(kw in full_text_lower for kw in STRUGGLE_KEYWORDS):
        seen_texts.add(full_text)
        filtered_reddit.append({
            "reddit_id": it.get("id"),
            "community": it.get("communityName", "r/Khan"),
            "post_type": it.get("dataType", "post"),
            "upvotes": it.get("upVotes", 0),
            "created_at": it.get("createdAt", ""),
            "sanitized_text": sanitize_text(full_text)
        })

print(f"Filtered {len(filtered_reddit)} relevant Reddit learner struggle posts/comments.")
with open(os.path.join(OUTPUT_DATA_DIR, "filtered_reddit_items.json"), "w", encoding="utf-8") as f:
    json.dump(filtered_reddit, f, indent=2)

# Sample for deep Groq classification
sample_reddit = filtered_reddit[:32] if len(filtered_reddit) >= 32 else filtered_reddit

CLASSIFICATION_PROMPT_SYSTEM = """You are an expert Educational Data Scientist and Senior Product Manager on Khan Academy's Learning Experience team.
Analyze batches of Reddit learner posts and classify each into our cognitive struggle taxonomy and behavioral patterns.

For each item, determine:
1. `primary_category`: One of:
   - "PREREQUISITE_GAP": Learner struggles because they lack foundational knowledge required for current topic.
   - "RULE_MISCONCEPTION": Erroneous mathematical rule application or conceptual misunderstanding.
   - "WORD_PROBLEM_TRANSLATION": Difficulty parsing prose into equations.
   - "CALCULATION_OR_EXECUTION_SLIP": Understanding is fine, but calculation slip or rigid grading causes failure.
   - "CONTEXTUAL_TRANSFER_FAILURE": Knows the video example, but fails when exercise structure varies.
   - "EXPLANATION_OR_HINT_FRICTION": Hints give answer without explaining why; explanations are unhelpful.
   - "SYSTEMIC_UI_OR_CONTENT_DEFECT": Technical bug, broken Perseus exercise, or login error.
   - "POSITIVE_LEARNING_EXPERIENCE": Affirming mastery and positive learning progress.

2. `observed_behavior`: One of:
   - "REPEATED_BLIND_RETRY"
   - "PASSIVE_VIDEO_REWATCHING"
   - "HINT_EXHAUSTION"
   - "EXERCISE_ABANDONMENT"
   - "SEEKING_EXTERNAL_TOOL" (e.g. asking Reddit, Photomath, tutoring)
   - "AUTONOMOUS_MASTERY"

3. `frustration_score`: Float between 0.0 and 1.0.
4. `abandonment_risk`: "HIGH", "MEDIUM", or "LOW".
5. `struggle_topic`: e.g. "Algebra / Linear Equations", "Calculus", "Basic Math", etc.
6. `verbatim_struggle_quote`: Short direct excerpt of struggle.

Output STRICT JSON with key "classifications" containing an array of objects:
{
  "classifications": [
    {
      "reddit_id": "...",
      "primary_category": "...",
      "observed_behavior": "...",
      "frustration_score": 0.85,
      "abandonment_risk": "HIGH",
      "struggle_topic": "...",
      "verbatim_struggle_quote": "..."
    }
  ]
}
"""

classified_reddit = []
batch_size = 4  # Smaller batch size to prevent OTPM rate limits on Groq
print(f"Beginning Groq LLM classification for {len(sample_reddit)} Reddit items in batches of {batch_size}...")

for i in range(0, len(sample_reddit), batch_size):
    batch = sample_reddit[i:i + batch_size]
    print(f"Processing Reddit batch {i//batch_size + 1}/{(len(sample_reddit) + batch_size - 1)//batch_size}...")
    
    prompt_user = "Analyze and classify the following Reddit learner posts:\n"
    for idx, item in enumerate(batch, 1):
        prompt_user += f"\n--- Item {idx} (ID: {item['reddit_id']}, Subreddit: {item['community']}) ---\n"
        prompt_user += f"{item['sanitized_text'][:500]}\n"

    success = False
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            response = groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": CLASSIFICATION_PROMPT_SYSTEM},
                    {"role": "user", "content": prompt_user}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            raw_content = response.choices[0].message.content.strip()
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw_content)
            items_classified = parsed.get("classifications", [])
            
            lookup = {r["reddit_id"]: r for r in batch}
            for c in items_classified:
                rid = c.get("reddit_id")
                if rid in lookup:
                    c["original_reddit"] = lookup[rid]
                classified_reddit.append(c)
            
            success = True
            print(f"  Batch successfully classified via {model} ({len(items_classified)} items).")
            break
        except Exception as e:
            print(f"  Error with {model}: {e}. Retrying with fallback...")
            time.sleep(2)
            
    time.sleep(1)

# Generate BGE Embeddings
print("Generating BAAI BGE vector embeddings for Reddit items...")
embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
texts_to_embed = [c.get("original_reddit", {}).get("sanitized_text", "") for c in classified_reddit]
if texts_to_embed:
    embeddings_list = list(embedder.embed(texts_to_embed))
    for idx, c in enumerate(classified_reddit):
        c["bge_embedding_dim"] = len(embeddings_list[idx])
        c["bge_embedding_sample"] = embeddings_list[idx][:5].tolist() if hasattr(embeddings_list[idx], "tolist") else list(embeddings_list[idx][:5])

with open(os.path.join(OUTPUT_DATA_DIR, "classified_reddit_feedback.json"), "w", encoding="utf-8") as f:
    json.dump(classified_reddit, f, indent=2)

print(f"Reddit Discovery Pipeline completed! Saved {len(classified_reddit)} classified records to {OUTPUT_DATA_DIR}/classified_reddit_feedback.json")
