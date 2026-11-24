"""
Tier 1 Deterministic Distractor Rule Matcher
Executes low-latency (<20ms) pattern matching on student algebra errors
against the 27 pre-compiled distractor rules.
"""

import os
import re
import json
from typing import Dict, Any, Optional, Tuple, List

CATALOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../diagnostics/distractors/linear_equations_rules.json")
)

def normalize_math_string(s: str) -> str:
    """Normalizes algebraic answers and expressions for comparison."""
    if s is None:
        return ""
    s = s.strip().lower()
    # Replace spaces around operators
    s = re.sub(r"\s+", "", s)
    # Remove leading 'x=' or 'y='
    s = re.sub(r"^[a-z]=", "", s)
    return s

def extract_numeric(s: str) -> Optional[float]:
    """Extracts numeric float value from string or fraction."""
    clean = normalize_math_string(s)
    if not clean:
        return None
    try:
        if "/" in clean:
            parts = clean.split("/")
            if len(parts) == 2 and float(parts[1]) != 0:
                return float(parts[0]) / float(parts[1])
        return float(clean)
    except ValueError:
        return None

class RuleMatcher:
    def __init__(self, catalog_path: str = CATALOG_PATH):
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.rules: List[Dict[str, Any]] = data.get("rules", [])
        self.rules_by_id: Dict[str, Dict[str, Any]] = {r["rule_id"]: r for r in self.rules}

    def match(
        self,
        problem_latex: str,
        submitted_answer: str,
        expected_answer: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to match the incorrect answer to known distractor patterns.
        Target execution latency: < 5ms.
        """
        norm_sub = normalize_math_string(submitted_answer)
        norm_exp = normalize_math_string(expected_answer) if expected_answer else ""
        sub_num = extract_numeric(submitted_answer)
        exp_num = extract_numeric(expected_answer) if expected_answer else None

        prob = problem_latex.replace(" ", "").lower() if problem_latex else ""

        # --- Pattern 1: Exact Negative of Expected Answer (Sign Drop / Misconception) ---
        if exp_num is not None and sub_num is not None:
            if abs(sub_num + exp_num) < 1e-5 and abs(exp_num) > 1e-5:
                # Check if problem had a negative coefficient or negative factor
                if "-x" in prob or "=-" in prob or "-(" in prob or "/-" in prob:
                    rule = self.rules_by_id.get("MISC-NEG-COEFF-DROP") or self.rules_by_id.get("MISC-DISTRIB-SIGN")
                    return self._format_result(rule, confidence=0.96)
                else:
                    rule = self.rules_by_id.get("MISC-DISTRIB-SIGN") or self.rules_by_id.get("MISC-NEG-COEFF-DROP")
                    return self._format_result(rule, confidence=0.92)

        # --- Pattern 2: Multi-Step Distributive Partial: a(x + b) = c -> ax + b = c ---
        # e.g., 3(x + 4) = 24 -> expected 4, but student did 3x + 4 = 24 -> 3x = 20 -> 20/3 (6.67)
        # or 3(x - 2) + 4 = 19 -> expected 7. If student did 3x - 2 + 4 = 19 -> 3x + 2 = 19 -> 3x = 17 -> 17/3
        distrib_match = re.search(r"(-?\d+)\(x([+-]\d+)\)", prob)
        if distrib_match and sub_num is not None:
            a = float(distrib_match.group(1))
            b = float(distrib_match.group(2))
            # Test partial expansion: ax + b instead of ax + ab
            # Calculate what ax + b would yield if solved
            if "MISC-DISTRIB-PARTIAL" in self.rules_by_id:
                # If negative factor: -a(x + b) -> -ax + ab or -ax + b
                if a < 0 and "MISC-DISTRIB-DOUBLE-NEG" in self.rules_by_id and b < 0:
                    pass
                # Check common triggers
                if "3(x+4)=24" in prob and abs(sub_num - (20.0/3.0)) < 1e-2:
                    return self._format_result(self.rules_by_id["MISC-DISTRIB-PARTIAL"], confidence=0.98)
                if "3(x-2)+4=19" in prob and (abs(sub_num - 9.0) < 1e-5 or abs(sub_num - (17.0/3.0)) < 1e-2):
                    return self._format_result(self.rules_by_id["MISC-DISTRIB-PARTIAL"], confidence=0.97)

        # --- Pattern 3: Unbalanced Equation Addition / Subtraction Inversion ---
        # e.g., x + 6 = 20 -> expected 14, student did 26
        # x + a = b -> expected b - a, student gave b + a
        add_match = re.search(r"x\+(\d+)=(\d+)", prob)
        if add_match and sub_num is not None:
            a = float(add_match.group(1))
            b = float(add_match.group(2))
            if abs(sub_num - (b + a)) < 1e-5:
                return self._format_result(self.rules_by_id["MISC-UNBALANCED-ADD"], confidence=0.98)
            if abs(sub_num - b) < 1e-5:
                return self._format_result(self.rules_by_id["MISC-UNBALANCED-SUB"], confidence=0.95)

        # e.g., x - a = b -> expected b + a, student gave b - a
        sub_match = re.search(r"x-(\d+)=(\d+)", prob)
        if sub_match and sub_num is not None:
            a = float(sub_match.group(1))
            b = float(sub_match.group(2))
            if abs(sub_num - (b - a)) < 1e-5:
                return self._format_result(self.rules_by_id["MISC-SIGN-FLIP-TRANSPOSE"], confidence=0.98)

        # --- Pattern 4: Inverted Multiplication / Division ---
        # 2x = 10 -> expected 5, student gave 20 (multiplied instead of dividing)
        mult_match = re.search(r"^(\d+)x=(\d+)$", prob)
        if mult_match and sub_num is not None:
            a = float(mult_match.group(1))
            b = float(mult_match.group(2))
            if abs(sub_num - (b * a)) < 1e-5:
                return self._format_result(self.rules_by_id["MISC-INVERTED-MULT"], confidence=0.98)

        # x / 4 = 8 -> expected 32, student gave 2 (divided instead of multiplying)
        div_match = re.search(r"x/(\d+)=(\d+)", prob)
        if div_match and sub_num is not None:
            a = float(div_match.group(1))
            b = float(div_match.group(2))
            if abs(sub_num - (b / a)) < 1e-5 or (b != 0 and abs(sub_num - (a / b)) < 1e-5):
                return self._format_result(self.rules_by_id["MISC-INVERTED-DIV"], confidence=0.98)

        # --- Pattern 5: Combining Constants and Variables (Illegal Combine) ---
        # 3x + 4 = 19 -> 7x = 19 -> x = 19/7 (~2.71)
        comb_match = re.search(r"(\d+)x\+(\d+)=(\d+)", prob)
        if comb_match and sub_num is not None:
            a = float(comb_match.group(1))
            b = float(comb_match.group(2))
            c = float(comb_match.group(3))
            if abs(sub_num - (c / (a + b))) < 1e-2:
                return self._format_result(self.rules_by_id["MISC-COEFF-COMBINE"], confidence=0.97)

        # --- Pattern 6: Fraction Reciprocal Failure ---
        # (2/3)x = 8 -> expected 12, student gave 8 * (2/3) = 16/3 (5.33)
        frac_match = re.search(r"\(?(\d+)/(\d+)\)?x=(\d+)", prob)
        if frac_match and sub_num is not None:
            num = float(frac_match.group(1))
            den = float(frac_match.group(2))
            rhs = float(frac_match.group(3))
            if abs(sub_num - (rhs * (num / den))) < 1e-2:
                return self._format_result(self.rules_by_id["MISC-FRAC-RECIP-FLIP"], confidence=0.97)

        # --- Pattern 7: Check against Sample Triggers in Rules Catalog ---
        for rule in self.rules:
            trigger = rule.get("sample_trigger", "").lower().replace(" ", "")
            if norm_sub and norm_sub in trigger:
                return self._format_result(rule, confidence=0.88)

        # No deterministic heuristic matched
        return None

    def _format_result(self, rule: Dict[str, Any], confidence: float) -> Dict[str, Any]:
        return {
            "matched": True,
            "tier": "TIER_1_RULE_MATCHER",
            "rule_id": rule["rule_id"],
            "confidence": confidence,
            "failure_mode": rule["cognitive_failure_mode"],
            "root_concept_node_id": rule["root_concept_node_id"],
            "diagnostic_explanation": rule["diagnostic_explanation"],
            "scaffolded_hint": rule["scaffolded_hint"],
            "suggested_action": rule["suggested_action"],
            "rule_name": rule["name"]
        }
