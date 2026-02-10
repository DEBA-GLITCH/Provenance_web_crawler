
from evidence.lifecycle import EvidenceState


def allow_reasoning(evidence_state: EvidenceState) -> bool:
    """
    The ONLY place that answers:
    'May this evidence enter a reasoning context?'
    """
    return evidence_state == EvidenceState.RAW_ACCEPTED
