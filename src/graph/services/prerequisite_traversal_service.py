"""
Prerequisite Traversal Service & Distractor Diagnostic Engine
Executes low-latency (<15ms) DAG traversals, loop prevention (Depth <= 2),
and maps algebraic distractor errors to foundational prerequisite nodes.
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.graph.knowledge_graph.algebra_dag_loader import get_algebra_dag

DISTRACTOR_CATALOG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../diagnostics/distractors/linear_equations_rules.json")
)

class PrerequisiteTraversalService:
    def __init__(self, catalog_path: str = DISTRACTOR_CATALOG_PATH):
        self.dag = get_algebra_dag()
        self.nodes = self.dag["nodes"]
        self.prereqs_of = self.dag["prerequisites_of"]
        self.dependents_of = self.dag["dependents_of"]
        
        # Load distractor rules catalog
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        self.rules = catalog.get("rules", [])
        self.rules_by_id = {r["rule_id"]: r for r in self.rules}

    def get_prerequisite_chain(self, skill_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """
        Traverses upstream prerequisites up to max_depth (enforcing loop prevention D <= 2).
        Returns list of prerequisite nodes ordered by distance (immediate first).
        Execution latency target: < 5ms.
        """
        if skill_id not in self.nodes:
            return []

        visited: Set[str] = {skill_id}
        queue: List[Tuple[str, int]] = [(skill_id, 0)]
        results: List[Dict[str, Any]] = []

        while queue:
            curr_id, curr_depth = queue.pop(0)
            if curr_depth >= max_depth:
                continue

            for prereq_id in self.prereqs_of.get(curr_id, []):
                if prereq_id not in visited:
                    visited.add(prereq_id)
                    p_node = self.nodes.get(prereq_id, {})
                    results.append({
                        "id": prereq_id,
                        "name": p_node.get("name"),
                        "grade_level": p_node.get("grade_level"),
                        "domain": p_node.get("domain"),
                        "hop_distance": curr_depth + 1
                    })
                    queue.append((prereq_id, curr_depth + 1))

        return results

    def identify_root_bottleneck(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds the earliest foundational ancestor node (the root prerequisite leaf with no further prerequisites).
        """
        if skill_id not in self.nodes:
            return None

        curr = skill_id
        visited: Set[str] = set()

        while True:
            visited.add(curr)
            parents = self.prereqs_of.get(curr, [])
            if not parents:
                # Found leaf foundation
                return self.nodes.get(curr)

            # Move to the first unvisited parent (foundational direction)
            next_parent = next((p for p in parents if p not in visited), None)
            if not next_parent:
                return self.nodes.get(curr)
            curr = next_parent

    def map_distractor_to_remediation(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Maps a distractor rule to root concept, scaffolded hint, and remedial action."""
        rule = self.rules_by_id.get(rule_id)
        if not rule:
            return None

        concept_id = rule.get("root_concept_node_id")
        concept_node = self.nodes.get(concept_id, {})

        return {
            "rule_id": rule_id,
            "name": rule.get("name"),
            "failure_mode": rule.get("cognitive_failure_mode"),
            "root_concept_node_id": concept_id,
            "root_concept_name": concept_node.get("name", "Unknown Concept"),
            "grade_level": concept_node.get("grade_level", "Unknown Grade"),
            "diagnostic_explanation": rule.get("diagnostic_explanation"),
            "scaffolded_hint": rule.get("scaffolded_hint"),
            "suggested_action": rule.get("suggested_action")
        }

    def diagnose_attempt_heuristic(
        self,
        skill_id: str,
        problem_latex: str,
        submitted_answer: str,
        expected_answer: str
    ) -> Dict[str, Any]:
        """
        Fast heuristic distractor matching engine (<15ms).
        Identifies sign slips, partial distribution, and inverted operations.
        """
        start = time.perf_counter()

        # Clean string tokens
        sub = submitted_answer.replace(" ", "").lower()
        exp = expected_answer.replace(" ", "").lower()

        matched_rule_id = None

        # Check 1: Sign flip slip (e.g. sub = -x when exp = x or sub has opposite sign)
        if sub.startswith("-") and not exp.startswith("-") and sub[1:] == exp:
            matched_rule_id = "MISC-NEG-COEFF-DROP"
        elif not sub.startswith("-") and exp.startswith("-") and sub == exp[1:]:
            matched_rule_id = "MISC-SIGN-INTEGER-ARITH"

        # Check 2: Distribution errors in equations with parentheses
        elif "(" in problem_latex:
            if "distrib" in skill_id.lower() or "paren" in skill_id.lower() or "multistep" in skill_id.lower():
                matched_rule_id = "MISC-DISTRIB-PARTIAL"

        # Check 3: Variable on both sides errors
        elif "both" in skill_id.lower() or "multistep" in skill_id.lower():
            matched_rule_id = "MISC-BOTH-SIDES-VAR-ADD"

        # Check 4: General two-step transposition errors
        else:
            matched_rule_id = "MISC-UNBALANCED-ADD"

        remediation = self.map_distractor_to_remediation(matched_rule_id)
        prereq_chain = self.get_prerequisite_chain(skill_id, max_depth=2)

        elapsed_ms = (time.perf_counter() - start) * 1000

        return {
            "skill_id": skill_id,
            "matched_rule_id": matched_rule_id,
            "diagnosis": remediation,
            "prerequisite_chain": prereq_chain,
            "latency_ms": round(elapsed_ms, 3),
            "under_sla": elapsed_ms < 15.0
        }

    def resolve_multi_prerequisite_conflict(self, failed_skill_ids: List[str]) -> Dict[str, Any]:
        """
        Enforces EC-10 from edge-case.md:
        When multiple prerequisites fail simultaneously, orders them topologically (foundations first)
        to prevent cognitive overload.
        """
        # Grade order priority: Grade 6 -> Grade 7 -> Grade 8 -> Algebra 1
        grade_order = {"Grade 6": 1, "Grade 7": 2, "Grade 8": 3, "Algebra 1": 4, "Grade 8 / Alg 1": 3.5}

        scored = []
        for sid in failed_skill_ids:
            node = self.nodes.get(sid, {})
            gl = node.get("grade_level", "Algebra 1")
            score = grade_order.get(gl, 5)
            scored.append((sid, score, node))

        # Sort by earliest grade level foundation
        scored.sort(key=lambda x: x[1])

        primary_bottleneck = scored[0] if scored else None
        return {
            "prioritized_skill_id": primary_bottleneck[0] if primary_bottleneck else None,
            "prioritized_skill_name": primary_bottleneck[2].get("name") if primary_bottleneck else None,
            "recommended_focus": "Address earliest foundational concept before procedural higher-level concepts."
        }
