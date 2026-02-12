
import json
from typing import List
from retrieval.context_block import ContextBlock
from llm.groq_client import call_llm
from llm.schema import ANSWER_SCHEMA_DESCRIPTION


def build_prompt(query: str, blocks: List[ContextBlock]) -> tuple[str, str]:
    """
    Build deterministic structured prompt.
    """

    context_payload = []

    for b in blocks:
        context_payload.append({
            "chunk_id": b.chunk_id,
            "evidence_id": b.evidence_id,
            "source_url": b.source_url,
            "text": b.chunk_text,
        })

    system_prompt = ANSWER_SCHEMA_DESCRIPTION

    user_prompt = json.dumps({
        "question": query,
        "context_blocks": context_payload
    }, indent=2)

    return system_prompt, user_prompt


def grounded_reason(query: str, blocks: List[ContextBlock]) -> dict:
    """
    Executes GROQ reasoning with strict schema.
    """

    if not blocks:
        return {
            "answer": "INSUFFICIENT_EVIDENCE",
            "claims": []
        }

    system_prompt, user_prompt = build_prompt(query, blocks)

    result = call_llm(system_prompt, user_prompt)

    # basic structure validation
    if "answer" not in result or "claims" not in result:
        raise ValueError("Invalid LLM schema")

    return result
