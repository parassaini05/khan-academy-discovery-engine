"""
PM Research Synthesis Agent
Retrieves empirical evidence via Hybrid RAG and synthesizes actionable Product Management findings with Groq.
"""

import os
import sys
import json
from typing import Dict, Any, List
from openai import OpenAI
from src.rag.retrieval.hybrid_search import HybridRetrievalEngine

from dotenv import load_dotenv
load_dotenv()

DEFAULT_GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-120b"

PM_SYNTHESIS_SYSTEM_PROMPT = """You are a Principal Product Manager & Learning Science Lead on Khan Academy's Learning Experience team.
Your task is to answer strategic product discovery questions using empirical evidence from our multi-source learner feedback database.

Rules for Synthesis:
1. Grounded in Evidence: Every observation, root cause, or failure mode you identify must be supported by the provided evidence excerpts.
2. Direct Citations: Quote the learner verbatim and cite the record ID (e.g. `[Record: playstore_...]` or `[Record: reddit_...]`).
3. Pedagogical Taxonomy: Use the 5 cognitive failure modes (Prerequisite Gap, Rule Misconception, Word Problem Translation, Execution Slip, Contextual Transfer Gap).
4. Actionable Product Recommendations: End with 1-2 concrete, high-leverage product feature ideas addressing the root cause.
"""

class PMResearchAgent:
    def __init__(self, api_key: str = DEFAULT_GROQ_API_KEY):
        self.retriever = HybridRetrievalEngine()
        self.client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key
        )

    def answer_research_question(self, question: str, top_k_evidence: int = 10) -> Dict[str, Any]:
        """Performs hybrid retrieval and generates an evidence-grounded PM synthesis brief."""
        print(f"\n[PM Research Agent] Investigating: '{question}'...")
        evidence_items = self.retriever.search(question, top_k=top_k_evidence)

        if not evidence_items:
            return {
                "question": question,
                "evidence_count": 0,
                "synthesis": "No sufficiently relevant empirical feedback was found in the database for this query."
            }

        context_block = "Empirical Learner Evidence Excerpts:\n"
        for idx, item in enumerate(evidence_items, 1):
            rid = item.get("record_id", "N/A")
            src = item.get("source", "unknown")
            cat = item.get("primary_category", "UNCLASSIFIED")
            txt = item.get("sanitized_text", "")
            context_block += f"\n--- Evidence [{idx}] (ID: {rid} | Source: {src} | Category: {cat}) ---\n"
            context_block += f"\"{txt}\"\n"

        user_prompt = f"""Strategic Product Question:
{question}

{context_block}

Synthesize a structured PM Research Brief answering the question based strictly on this learner evidence. Format in clean Markdown with:
1. Executive Answer & Root Cause
2. Quantitative/Qualitative Evidence Summary
3. Verbatim Learner Quotes with Citations
4. Strategic Product Opportunities for Khan Academy
"""

        synthesis_text = ""
        for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": PM_SYNTHESIS_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2000
                )
                synthesis_text = response.choices[0].message.content.strip()
                break
            except Exception as e:
                print(f"[PM Agent] Notice for {model}: {e}. Retrying fallback...")

        return {
            "question": question,
            "evidence_count": len(evidence_items),
            "evidence_citations": [it.get("record_id") for it in evidence_items],
            "evidence_items": evidence_items,
            "synthesis": synthesis_text
        }

if __name__ == "__main__":
    agent = PMResearchAgent()
    q = "Why do students abandon linear equation practice exercises?"
    res = agent.answer_research_question(q, top_k_evidence=6)
    print("\n" + "="*60)
    print("PM SYNTHESIS RESULT:")
    print("="*60)
    print(res["synthesis"])
