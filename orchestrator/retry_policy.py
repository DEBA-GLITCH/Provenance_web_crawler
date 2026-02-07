# orchestrator/retry_policy.py

from enum import Enum
from orchestrator.execution_context import ExecutionContext, FailureClass
from orchestrator.failure_event import FailureEvent


class RetryDecision(str, Enum):
    RETRY_NOW = "retry_now"
    RETRY_BACKOFF = "retry_backoff"
    HALT_TASK = "halt_task"
    QUARANTINE_AND_CONTINUE = "quarantine_and_continue"


class RetryPolicy:
    """
    Pure decision engine.
    No mutation. No side effects.
    """

    @staticmethod
    def decide(ctx: ExecutionContext, failure: FailureEvent) -> RetryDecision:
        # ---- absolute halts ----
        if ctx.limits_exceeded():
            return RetryDecision.HALT_TASK

        # ---- semantic failures are not retryable ----
        if failure.failure_class == FailureClass.SEMANTIC:
            return RetryDecision.QUARANTINE_AND_CONTINUE

        # ---- rate limiting ----
        if failure.failure_class == FailureClass.RATE_LIMIT:
            if ctx.retry_count_total >= ctx.max_retries:
                return RetryDecision.HALT_TASK
            return RetryDecision.RETRY_BACKOFF

        # ---- server/network errors ----
        if failure.failure_class in (
            FailureClass.NETWORK,
            FailureClass.SERVER_ERROR,
        ):
            return RetryDecision.RETRY_BACKOFF

        # ---- client errors (401/403/404 etc.) ----
        if failure.failure_class == FailureClass.CLIENT_ERROR:
            return RetryDecision.HALT_TASK

        return RetryDecision.HALT_TASK
