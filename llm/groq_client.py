
import os
import json
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in .env")

client = Groq(api_key=GROQ_API_KEY)


def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """
    Deterministic LLM call.
    Temperature forced to 0.
    """

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = response.choices[0].message.content

    try:
        if not content:
            raise ValueError("LLM returned empty content")
            
        return json.loads(content)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"❌ LLM JSON Error: {e}")
        # Return a safe fallback to prevent crash
        return {"error": "Invalid JSON from LLM", "raw": content}
