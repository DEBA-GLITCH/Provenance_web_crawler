
import hashlib
from typing import List


MAX_CHUNK_CHARS = 1200  # deterministic limit


def deterministic_chunk(text: str) -> List[str]:
    """
    Structure-aware deterministic chunking.
    Splits on paragraph boundaries, caps size.
    """

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        # Handle oversized paragraphs
        if len(para) > MAX_CHUNK_CHARS:
            # If current has content, flush it first
            if current:
                chunks.append(current.strip())
                current = ""
            
            # Split big paragraph into hard chunks
            for i in range(0, len(para), MAX_CHUNK_CHARS):
                chunks.append(para[i:i + MAX_CHUNK_CHARS])
            
            continue

        if len(current) + len(para) <= MAX_CHUNK_CHARS:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = para + "\n\n"

    if current:
        chunks.append(current.strip())

    return chunks


def chunk_id(evidence_id: str, chunk_text: str) -> str:
    """
    Stable chunk identifier derived from content.
    """
    digest = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
    return f"{evidence_id}:{digest[:16]}"
