"""
Experiment Tracker & Telemetry Instrumentation for A/B Testing
Implements deterministic user variant hashing (50/50 Control vs Treatment)
and standardized event logging for Khan Academy learning experience trials.
"""

import os
import sys
import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

TELEMETRY_LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/telemetry"))
os.makedirs(TELEMETRY_LOG_DIR, exist_ok=True)
TELEMETRY_LOG_FILE = os.path.join(TELEMETRY_LOG_DIR, "experiment_events.jsonl")

class ExperimentTracker:
    CONTROL = "CONTROL"
    TREATMENT = "TREATMENT"
    EXPERIMENT_NAME = "EXP_COGNITIVE_DIAGNOSTICS_V1"

    EVENT_ATTEMPT_FAILED = "attempt_failed_with_diagnosis"
    EVENT_REMEDIATION_ENGAGED = "micro_remediation_engaged"
    EVENT_PREREQ_COMPLETED = "prerequisite_detour_completed"
    EVENT_RETRY_SUCCESS = "post_remediation_retry_success"
    EVENT_SESSION_ABANDONED = "session_abandonment_after_struggle"

    def __init__(self, log_path: str = TELEMETRY_LOG_FILE):
        self.log_path = log_path
        self.events_buffer: List[Dict[str, Any]] = []

    def get_variant(self, user_id: str) -> str:
        """
        Deterministically maps user_id to CONTROL or TREATMENT using SHA-256 hash.
        Guarantees 50/50 uniform distribution across the learner cohort.
        """
        hash_val = int(hashlib.sha256(f"{self.EXPERIMENT_NAME}:{user_id}".encode("utf-8")).hexdigest(), 16)
        bucket = hash_val % 100
        return self.TREATMENT if bucket >= 50 else self.CONTROL

    def log_event(
        self,
        event_type: str,
        user_id: str,
        exercise_id: str,
        topic_slug: str = "linear-equations-variables-both-sides",
        attempt_number: int = 1,
        time_spent_seconds: float = 30.0,
        metadata: Optional[Dict[str, Any]] = None,
        flush_to_disk: bool = False
    ) -> Dict[str, Any]:
        """
        Logs a standardized telemetry event matching the architecture schema.
        """
        variant = self.get_variant(user_id)
        event = {
            "event_id": str(uuid.uuid4()),
            "experiment_name": self.EXPERIMENT_NAME,
            "variant": variant,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "exercise_id": exercise_id,
            "topic_slug": topic_slug,
            "attempt_number": attempt_number,
            "time_spent_seconds": round(time_spent_seconds, 2),
            "metadata": metadata or {}
        }

        self.events_buffer.append(event)

        if flush_to_disk:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")

        return event

    def flush(self):
        """Flushes buffered events to the JSONL log file."""
        if not self.events_buffer:
            return
        with open(self.log_path, "a", encoding="utf-8") as f:
            for ev in self.events_buffer:
                f.write(json.dumps(ev) + "\n")
        self.events_buffer.clear()
