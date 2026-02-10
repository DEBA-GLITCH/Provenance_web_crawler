
from dataclasses import dataclass, field
from typing import List, Dict
import time


@dataclass(frozen=True)
class IntegrityEnvelope:
    """
    Append-only integrity judgment.
    Never mutates evidence bytes.
    """

    evidence_id: str
    integrity_score: float
    usable_for_reasoning: bool
    flags: List[str]
    metrics: Dict[str, float]
    validator_version: str
    decision: str  # ALLOW | QUARANTINE
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "evidence_id": self.evidence_id,
            "integrity_score": self.integrity_score,
            "usable_for_reasoning": self.usable_for_reasoning,
            "flags": self.flags,
            "metrics": self.metrics,
            "validator_version": self.validator_version,
            "decision": self.decision,
            "created_at": self.created_at,
        }
