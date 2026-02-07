# evidence/store.py

import hashlib
import os
import json

class EvidenceStore:
    """
    Write-once, content-addressable storage.

    Binary body is stored raw.
    Metadata is stored as JSON.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.blob_path = os.path.join(base_path, "blobs")
        self.meta_path = os.path.join(base_path, "meta")

        os.makedirs(self.blob_path, exist_ok=True)
        os.makedirs(self.meta_path, exist_ok=True)

    def write(self, payload: dict) -> str:
        body: bytes = payload["body"]

        # ---- content hash from raw bytes ----
        digest = hashlib.sha256(body).hexdigest()

        blob_file = os.path.join(self.blob_path, digest)
        meta_file = os.path.join(self.meta_path, f"{digest}.json")

        # ---- write binary blob (write-once) ----
        if not os.path.exists(blob_file):
            tmp = blob_file + ".tmp"
            with open(tmp, "wb") as f:
                f.write(body)
                f.flush()
                os.fsync(f.fileno())
            os.rename(tmp, blob_file)

        # ---- write metadata (headers, url, status) ----
        meta = {
            "url": payload["url"],
            "status": payload["status"],
            "headers": payload["headers"],
            "body_sha256": digest,
            "body_size": len(body),
        }

        if not os.path.exists(meta_file):
            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())

        return digest
