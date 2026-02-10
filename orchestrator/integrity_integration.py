from evidence.envelope import IntegrityEnvelope
from evidence.lifecycle import EvidenceState
from validators.integrity import IntegrityResult


def integrate_integrity(
    evidence_id: str,
    integrity: IntegrityResult,
) -> tuple[EvidenceState, IntegrityEnvelope]:
    """
    Turns metrics into enforceable policy.
    No recomputation. No mutation.
    """

    if integrity.usable_for_reasoning:
        state = EvidenceState.RAW_ACCEPTED
        decision = "ALLOW"
    else:
        state = EvidenceState.QUARANTINED_LOW_INTEGRITY
        decision = "QUARANTINE"

    envelope = IntegrityEnvelope(
        evidence_id=evidence_id,
        integrity_score=integrity.integrity_score,
        usable_for_reasoning=integrity.usable_for_reasoning,
        flags=integrity.flags,
        metrics=integrity.metrics,
        validator_version=integrity.validator_version,
        decision=decision,
    )

    return state, envelope
