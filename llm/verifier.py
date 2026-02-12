
from typing import List, Dict
from retrieval.context_block import ContextBlock
from difflib import SequenceMatcher


SIMILARITY_THRESHOLD = 0.82


def verify_claims(
    llm_output: dict,
    context_blocks: List[ContextBlock],
) -> dict:
    """
    Validates LLM claims against provided context blocks.
    """

    valid_chunk_ids = {b.chunk_id: b for b in context_blocks}

    verified_claims = []
    conflicts = []

    for claim in llm_output.get("claims", []):

        chunk_id = claim.get("chunk_id")
        statement = claim.get("statement")

        if chunk_id not in valid_chunk_ids:
            continue  # reject hallucinated chunk

        block = valid_chunk_ids[chunk_id]

        similarity = similarity_score(statement, block.chunk_text)

        if similarity < SIMILARITY_THRESHOLD:
            continue  # reject weak grounding

        verified_claims.append({
            "statement": statement,
            "chunk_id": chunk_id,
            "evidence_id": block.evidence_id,
            "similarity_score": round(similarity, 4),
        })

    if not verified_claims:
        return {
            "answer": "INSUFFICIENT_GROUNDED_CLAIMS",
            "claims": [],
            "confidence": 0.0,
            "conflicts": [],
        }

    confidence = compute_confidence(verified_claims)

    return {
        "answer": llm_output["answer"],
        "claims": verified_claims,
        "confidence": confidence,
        "conflicts": conflicts,
    }


def similarity_score(a: str, b: str) -> float:
    """
    Deterministic normalized similarity.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def compute_confidence(claims: List[Dict]) -> float:
    """
    Heuristic confidence computation.
    """

    if not claims:
        return 0.0

    avg_similarity = sum(c["similarity_score"] for c in claims) / len(claims)

    diversity_bonus = min(len({c["evidence_id"] for c in claims}) * 0.05, 0.15)

    score = avg_similarity * 0.85 + diversity_bonus

    return round(min(score, 1.0), 4)
