# validators/structure.py

from orchestrator.failure_event import FailureEvent
from orchestrator.execution_context import FailureClass

MIN_BODY_BYTES = 512

JS_ONLY_MARKERS = [
    b"enable javascript",
    b"<noscript>",
    b"captcha",
]

def validate_structure(resp: dict) -> FailureEvent | None:
    body = resp["body"].lower()

    if len(body) < MIN_BODY_BYTES:
        return FailureEvent(FailureClass.SEMANTIC, None, "Body too small")

    for marker in JS_ONLY_MARKERS:
        if marker in body:
            return FailureEvent(FailureClass.SEMANTIC, None, "JS-only placeholder")

    return None
