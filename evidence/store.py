# evidence/store.py

import hashlib
import os
import json
import tempfile
from typing import Dict


class EvidenceStore:
    """
    Write-once, content-addressable evidence store.

    - Raw bytes stored as blobs
    - Metadata stored as JSON
    - Integrity envelopes stored append-only (JSONL)
    - Lifecycle state stored explicitly
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.blob_path = os.path.join(base_path, "blobs")
        self.meta_path = os.path.join(base_path, "meta")

        os.makedirs(self.blob_path, exist_ok=True)
        os.makedirs(self.meta_path, exist_ok=True)

    # --------------------------------------------------
    # Evidence write (Phase-1B)
    # --------------------------------------------------

    def write(self, payload: Dict) -> str:
        body: bytes = payload["body"]

        digest = hashlib.sha256(body).hexdigest()

        blob_file = os.path.join(self.blob_path, digest)
        meta_file = os.path.join(self.meta_path, f"{digest}.json")

        # ---- write blob (atomic, write-once) ----
        if not os.path.exists(blob_file):
            with tempfile.NamedTemporaryFile(
                dir=self.blob_path, delete=False
            ) as tmp:
                tmp.write(body)
                tmp.flush()
                os.fsync(tmp.fileno())
                tmp_name = tmp.name

            os.rename(tmp_name, blob_file)

        # ---- write base metadata ----
        if not os.path.exists(meta_file):
            meta = {
                "url": payload["url"],
                "status": payload["status"],
                "headers": payload["headers"],
                "body_sha256": digest,
                "body_size": len(body),
            }

            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())

        return digest

    # --------------------------------------------------
    # Phase-2B: append-only integrity envelope
    # --------------------------------------------------

    def append_envelope(self, evidence_id: str, envelope: Dict) -> None:
        """
        Append-only integrity envelope log (JSONL).

        Guarantees:
        - atomic line writes
        - no overwrite
        - ordered forensic history
        """

        required_fields = {
            "evidence_id",
            "integrity_score",
            "usable_for_reasoning",
            "flags",
            "metrics",
            "validator_version",
            "decision",
            "created_at",
        }

        missing = required_fields - envelope.keys()
        if missing:
            raise ValueError(
                f"Invalid IntegrityEnvelope, missing fields: {missing}"
            )

        envelope_path = os.path.join(
            self.meta_path, f"{evidence_id}.envelopes.jsonl"
        )

        line = json.dumps(envelope, sort_keys=True) + "\n"

        with open(envelope_path, "ab") as f:
            f.write(line.encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())

    # --------------------------------------------------
    # Phase-2B: lifecycle state
    # --------------------------------------------------

    def write_state(self, evidence_id: str, state: str) -> None:
        """
        Persist current lifecycle state.

        This is NOT mutable in-place; it represents
        the latest authoritative state.
        """
        state_file = os.path.join(
            self.meta_path, f"{evidence_id}.state"
        )

        with open(state_file, "w") as f:
            f.write(state)
            f.flush()
            os.fsync(f.fileno())
