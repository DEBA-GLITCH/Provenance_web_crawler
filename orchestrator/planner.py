
import json
from llm.groq_client import call_llm
from orchestrator.action_types import ActionType


PLANNER_SCHEMA = """
Return JSON in this format:

{
  "action": "SEARCH" | "FETCH" | "REASON" | "HALT",
  "query": string | null,
  "url": string | null
}

Rules:
- Choose only one action.
- If action is SEARCH, provide query.
- If FETCH, provide url.
- If REASON or HALT, set query and url to null.
"""


def plan_next_action(state_map: dict) -> dict:

    system_prompt = PLANNER_SCHEMA

    user_prompt = json.dumps(state_map, indent=2)

    result = call_llm(system_prompt, user_prompt)

    if "action" not in result:
        raise ValueError("Planner output invalid")

    return result
