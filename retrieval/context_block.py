
from dataclasses import dataclass


@dataclass(frozen=True)
class ContextBlock:
    """
    Atomic unit of evidence passed to the LLM.
    """

    chunk_id: str
    evidence_id: str
    source_url: str
    chunk_text: str
    integrity_score: float
