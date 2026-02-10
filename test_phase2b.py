

from validators.integrity import IntegrityEvaluator
from orchestrator.integrity_integration import integrate_integrity
from evidence.store import EvidenceStore

# Fake raw page
raw_bytes = b"<html><body>Hello world</body></html>"

store = EvidenceStore("./evidence_data")

# Simulate payload (Phase-1B)
payload = {
    "url": "https://example.com",
    "status": 200,
    "headers": {},
    "body": raw_bytes,
}

# Phase-1B
evidence_id = store.write(payload)

# Phase-2A
integrity = IntegrityEvaluator.evaluate(raw_bytes)

# Phase-2B
state, envelope = integrate_integrity(evidence_id, integrity)

store.append_envelope(evidence_id, envelope.to_dict())
store.write_state(evidence_id, state.value)

print("Evidence ID:", evidence_id)
print("State:", state)
print("Integrity score:", integrity.integrity_score)
