
ANSWER_SCHEMA_DESCRIPTION = """
You must return JSON with the following structure:

{
  "answer": string,
  "claims": [
    {
      "statement": string,
      "chunk_id": string,
      "evidence_id": string
    }
  ]
}

Rules:
- Do NOT invent chunk_id.
- Only use chunk_ids provided in context.
- Every claim must cite a valid chunk_id.
- If insufficient evidence, return:

{
  "answer": "INSUFFICIENT_EVIDENCE",
  "claims": []
}
"""
