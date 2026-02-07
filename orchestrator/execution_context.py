# orchestrator/execution_context.py

from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Dict


class FailureClass(str, Enum):
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    SEMANTIC = "semantic"
    UNKNOWN = "unknown"


@dataclass
class ExecutionContext:
    """
    ExecutionContext is the single source of truth for
    whether a task is allowed to continue running.

    Single-writer: Orchestrator ONLY.
    Serializable at all times.
    """

    # ---- immutable ----
    start_time: float = field(default_factory=time.time)

    # ---- mutable counters ----
    elapsed_time_ms: int = 0
    step_count: int = 0

    retry_count_total: int = 0
    retry_count_by_class: Dict[FailureClass, int] = field(
        default_factory=lambda: {fc: 0 for fc in FailureClass}
    )

    evidence_bytes_written: int = 0
    quarantine_count: int = 0
    cost_units_spent: float = 0.0

    # ---- hard limits (config-driven) ----
    max_steps: int = 100
    max_retries: int = 50
    max_elapsed_time_ms: int = 10 * 60 * 1000  # 10 minutes
    max_evidence_bytes: int = 50 * 1024 * 1024  # 50 MB
    max_quarantines: int = 20
    max_cost_units: float = 10.0

    def update_time(self) -> None:
        self.elapsed_time_ms = int((time.time() - self.start_time) * 1000)

    def increment_step(self) -> None:
        self.step_count += 1

    def record_retry(self, failure_class: FailureClass) -> None:
        self.retry_count_total += 1
        self.retry_count_by_class[failure_class] += 1

    def record_evidence(self, byte_count: int) -> None:
        self.evidence_bytes_written += byte_count

    def record_quarantine(self) -> None:
        self.quarantine_count += 1

    def record_cost(self, units: float) -> None:
        self.cost_units_spent += units

    # ---- invariants ----
    def limits_exceeded(self) -> bool:
        return any([
            self.step_count > self.max_steps,
            self.retry_count_total > self.max_retries,
            self.elapsed_time_ms > self.max_elapsed_time_ms,
            self.evidence_bytes_written > self.max_evidence_bytes,
            self.quarantine_count > self.max_quarantines,
            self.cost_units_spent > self.max_cost_units,
        ])

    def snapshot(self) -> dict:
        """
        Minimal but complete snapshot for observability.
        """
        return {
            "elapsed_time_ms": self.elapsed_time_ms,
            "step_count": self.step_count,
            "retry_count_total": self.retry_count_total,
            "retry_count_by_class": {
                k.value: v for k, v in self.retry_count_by_class.items()
            },
            "evidence_bytes_written": self.evidence_bytes_written,
            "quarantine_count": self.quarantine_count,
            "cost_units_spent": self.cost_units_spent,
        }
