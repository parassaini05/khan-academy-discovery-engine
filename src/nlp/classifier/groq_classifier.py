"""
Groq Cognitive Classifier Implementation
Uses Pydantic validation, structured few-shot prompts, and dynamic failover between Groq models.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.nlp.classifier.cognitive_taxonomy_prompt import (
    FEW_SHOT_SYSTEM_PROMPT,
    BatchClassificationResponse,
    ClassificationItem
)

from dotenv import load_dotenv
load_dotenv()

DEFAULT_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-120b"

class GroqCognitiveClassifier:
    def __init__(self, api_key: str = DEFAULT_GROQ_API_KEY):
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )

    def classify_batch(self, items: List[Dict[str, Any]]) -> List[ClassificationItem]:
        """Classifies a batch of learner records with Pydantic validation."""
        if not items:
            return []

        user_content = "Classify the following learner records according to the cognitive taxonomy:\n"
        for idx, it in enumerate(items, 1):
            rid = it.get("record_id") or it.get("external_id")
            text = it.get("sanitized_text") or it.get("raw_text") or ""
            user_content += f"\n--- Record {idx} (ID: {rid}) ---\n{text[:450]}\n"

        for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": FEW_SHOT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.0,
                    max_tokens=1800
                )
                raw_text = response.choices[0].message.content.strip()

                # Clean markdown blocks
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()

                parsed_dict = json.loads(raw_text)
                validated_response = BatchClassificationResponse.model_validate(parsed_dict)
                return validated_response.classifications

            except Exception as e:
                print(f"[Classifier Warning] Model {model} error: {e}. Retrying with next model...")
                time.sleep(2)

        print("[Classifier Error] Failed all models in failover chain for batch.")
        return []
