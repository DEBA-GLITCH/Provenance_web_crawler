# validators/transport.py

from orchestrator.failure_event import FailureEvent
from orchestrator.execution_context import FailureClass

def validate_transport(resp: dict) -> FailureEvent | None:
    status = resp["status"]

    if status >= 500:
        return FailureEvent(FailureClass.SERVER_ERROR, status, "Server error")

    if status == 429:
        retry_after = resp["headers"].get("Retry-After")
        return FailureEvent(FailureClass.RATE_LIMIT, status, "Rate limited", retry_after)

    if status in (401, 403, 404):
        return FailureEvent(FailureClass.CLIENT_ERROR, status, "Client blocked")

    return None
