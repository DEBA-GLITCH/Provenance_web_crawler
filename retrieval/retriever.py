
import os
import json
from typing import List
from retrieval.context_block import ContextBlock
from retrieval.chunker import deterministic_chunk, chunk_id
from retrieval.html_cleaner import extract_main_content


MAX_CONTEXT_BLOCKS = 5


def _load_state(meta_path: str, evidence_id: str) -> str:
    state_file = os.path.join(meta_path, f"{evidence_id}.state")
    if not os.path.exists(state_file):
        return None

    with open(state_file, "r") as f:
        return f.read().strip()


def _load_metadata(meta_path: str, evidence_id: str) -> dict:
    with open(os.path.join(meta_path, f"{evidence_id}.json"), "r") as f:
        return json.load(f)


def _load_blob(blob_path: str, evidence_id: str) -> bytes:
    with open(os.path.join(blob_path, evidence_id), "rb") as f:
        return f.read()


def retrieve_context(
    query: str,
    base_path: str,
) -> List[ContextBlock]:
    """
    Returns top-K context blocks from RAW_ACCEPTED evidence only.
    """

    blob_path = os.path.join(base_path, "blobs")
    meta_path = os.path.join(base_path, "meta")

    blocks: List[ContextBlock] = []

    for filename in os.listdir(meta_path):
        if not filename.endswith(".json"):
            continue

        evidence_id = filename.replace(".json", "")
        state = _load_state(meta_path, evidence_id)

        if state != "RAW_ACCEPTED":
            continue

        meta = _load_metadata(meta_path, evidence_id)
        raw = _load_blob(blob_path, evidence_id)

        # Try to clean HTML first
        text = extract_main_content(raw)
        
        # Fallback to raw text if cleaning fails or returns empty
        if not text:
            text = raw.decode("utf-8", errors="ignore")

        chunks = deterministic_chunk(text)

        for chunk in chunks:
            score = lexical_overlap_score(query, chunk)

            if score > 0:
                blocks.append(
                    ContextBlock(
                        chunk_id=chunk_id(evidence_id, chunk),
                        evidence_id=evidence_id,
                        source_url=meta["url"],
                        chunk_text=chunk,
                        integrity_score=1.0,  # integrity already validated
                    )
                )

    # simple lexical ranking
    blocks.sort(
        key=lambda b: lexical_overlap_score(query, b.chunk_text),
        reverse=True,
    )

    return blocks[:MAX_CONTEXT_BLOCKS]


def lexical_overlap_score(query: str, text: str) -> float:
    """
    Deterministic lexical scoring.
    No embeddings yet.
    """
    q_tokens = set(query.lower().split())
    t_tokens = set(text.lower().split())

    if not q_tokens:
        return 0.0

    overlap = q_tokens.intersection(t_tokens)
    return len(overlap) / len(q_tokens)
