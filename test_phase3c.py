# test_phase3c.py

from retrieval.retriever import retrieve_context
from llm.reasoner import grounded_reason

query = "What is example.com used for?"

blocks = retrieve_context(query, "./evidence_data")

result = grounded_reason(query, blocks)

print(result)
