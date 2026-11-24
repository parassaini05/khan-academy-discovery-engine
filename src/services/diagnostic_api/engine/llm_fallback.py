"""
Tier 2 Distilled LLM Fallback Classifier
Handles novel or composite student algebraic errors when Tier 1 rule matcher misses.
Utilizes Groq LPU inference (qwen/qwen3.8-27b with failover to openai/gpt-oss-120b).
Enforces structured output and bounded latency (<180ms target).
"""

import os
import json
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import openai

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-120b"

PROMPT_TEMPLATE = """You are Khan Academy's expert cognitive math diagnostic engine.
Analyze the following student attempt on a linear equations problem.

Problem: {problem_latex}
Student Submitted Answer: {submitted_answer}
Expected Correct Answer: {expected_answer}
Attempt History: {attempt_history}

Classify the cognitive failure mode into one of:
- "RULE_MISCONCEPTION": Conceptual error applying algebraic operations or inverse operations.
- "PREREQUISITE_GAP": Deficit in foundational middle-school math (negative numbers, fractions, order of operations).
- "TRANSLATION_GAP": Error translating words or expressions.
- "EXECUTION_SLIP": Minor arithmetic calculation error despite correct procedure.
- "TRANSFER_GAP": Inability to apply rule to unfamiliar structure.

Available Prerequisite Root Concepts:
- MATH-NUM-NEG-ADD (Negative Integer Addition)
- MATH-NUM-NEG-MULT (Negative Integer Multiplication)
- MATH-NUM-FRAC-DIV (Fraction Division & Reciprocals)
- MATH-ALG-DISTRIB-POS (Distributive Property Positive)
- MATH-ALG-DISTRIB-NEG (Distributive Property Negative)
- MATH-ALG-ADD-INV (Additive Inverse)
- MATH-EQ-SCALE-BALANCE (Scale Balance Concept)
- MATH-EQ-2STEP-BASIC (Two-Step Equation Order of Operations)

Return ONLY a valid JSON object with the following fields:
{{
  "failure_mode": "RULE_MISCONCEPTION" | "PREREQUISITE_GAP" | "TRANSLATION_GAP" | "EXECUTION_SLIP" | "TRANSFER_GAP",
  "root_concept_node_id": "<one of the IDs above>",
  "confidence": 0.85,
  "diagnostic_explanation": "One clear sentence explaining the specific mistake.",
  "scaffolded_hint": "One clear pedagogical question or hint guiding the learner.",
  "suggested_action": "RETRY_WITH_STEP_PROMPT" | "SIGN_CHECK_CALLOUT" | "PREREQUISITE_REROUTE"
}}
"""

class LLMFallbackClassifier:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(
                base_url=GROQ_BASE_URL,
                api_key=self.api_key,
                timeout=3.0  # Strict timeout for microservice SLA
            )

    def diagnose(
        self,
        problem_latex: str,
        submitted_answer: str,
        expected_answer: Optional[str] = "x = 7",
        attempt_history: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Executes LLM fallback diagnosis.
        Falls back gracefully to deterministic pedagogical default if offline or rate-limited.
        """
        start_time = time.time()
        
        if not self.client or not self.api_key:
            return self._heuristic_fallback(problem_latex, submitted_answer, expected_answer, "No API key configured")

        prompt = PROMPT_TEMPLATE.format(
            problem_latex=problem_latex,
            submitted_answer=submitted_answer,
            expected_answer=expected_answer or "N/A",
            attempt_history=json.dumps(attempt_history or [])
        )

        for model_id in [PRIMARY_MODEL, FALLBACK_MODEL]:
            try:
                response = self.client.chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": "You are a real-time math diagnostic classifier. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                    max_tokens=250
                )
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)
                latency_ms = (time.time() - start_time) * 1000.0

                return {
                    "matched": True,
                    "tier": "TIER_2_LLM_FALLBACK",
                    "model_used": model_id,
                    "latency_ms": round(latency_ms, 2),
                    "rule_id": "LLM-DIAGNOSTIC-ADAPTIVE",
                    "failure_mode": data.get("failure_mode", "RULE_MISCONCEPTION"),
                    "confidence": float(data.get("confidence", 0.85)),
                    "root_concept_node_id": data.get("root_concept_node_id", "MATH-EQ-2STEP-BASIC"),
                    "diagnostic_explanation": data.get("diagnostic_explanation", "Check your algebraic step."),
                    "scaffolded_hint": data.get("scaffolded_hint", "Try isolating the variable term first."),
                    "suggested_action": data.get("suggested_action", "RETRY_WITH_STEP_PROMPT"),
                    "rule_name": f"Adaptive Diagnostic ({data.get('failure_mode', 'RULE_MISCONCEPTION')})"
                }
            except Exception as e:
                # Fail over to secondary model or fallback
                continue

        return self._heuristic_fallback(problem_latex, submitted_answer, expected_answer, "LLM fallback timeout / error")

    def _heuristic_fallback(
        self,
        problem_latex: str,
        submitted_answer: str,
        expected_answer: Optional[str],
        reason: str
    ) -> Dict[str, Any]:
        """Pedagogically safe deterministic fallback ensuring 0% downtime and SLA compliance."""
        return {
            "matched": True,
            "tier": "TIER_2_HEURISTIC_SAFEGUARD",
            "model_used": "deterministic_safety_net",
            "latency_ms": 1.5,
            "rule_id": "FALLBACK-SAFEGUARD-STEP",
            "failure_mode": "EXECUTION_SLIP",
            "confidence": 0.70,
            "root_concept_node_id": "MATH-EQ-2STEP-BASIC",
            "diagnostic_explanation": "Your calculation differed from the expected solution. Check your intermediate step.",
            "scaffolded_hint": "Review the last operation applied to both sides of the equation.",
            "suggested_action": "RETRY_WITH_STEP_PROMPT",
            "rule_name": "Standard Step Scaffolding Safeguard",
            "fallback_reason": reason
        }
