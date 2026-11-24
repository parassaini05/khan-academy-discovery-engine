"""
Graph Client for Runtime Diagnostic Microservice
Integrates with the 42-node Knowledge Graph DAG and distractor catalog.
"""

from typing import Dict, Any, List, Optional
from src.graph.services.prerequisite_traversal_service import PrerequisiteTraversalService

class DiagnosticGraphClient:
    def __init__(self):
        self.service = PrerequisiteTraversalService()

    def get_remediation_package(self, rule_id: str, skill_id: str) -> Dict[str, Any]:
        """Resolves distractor rule to remedial copy, root concept, and prerequisite path."""
        remediation = self.service.map_distractor_to_remediation(rule_id)
        prereq_chain = self.service.get_prerequisite_chain(skill_id, max_depth=2)
        root_leaf = self.service.identify_root_bottleneck(skill_id)

        return {
            "remediation": remediation,
            "prerequisite_chain": prereq_chain,
            "root_foundation": root_leaf
        }
