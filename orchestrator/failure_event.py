# orchestrator/failure_event.py

from dataclasses import dataclass
from orchestrator.execution_context import FailureClass


@dataclass(frozen=True)
class FailureEvent:
    """
    Immutable description of a failure.
    Produced by tools or validators.
    """

    failure_class: FailureClass
    http_status: int | None
    message: str
    retry_after_seconds: int | None = None
