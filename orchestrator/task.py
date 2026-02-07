# orchestrator/task.py

from orchestrator.execution_context import ExecutionContext
from orchestrator.failure_event import FailureEvent
from orchestrator.retry_policy import RetryPolicy, RetryDecision


class TaskOrchestrator:
    """
    Demonstrates how ExecutionContext + RetryPolicy interact.
    """

    def __init__(self, ctx: ExecutionContext):
        self.ctx = ctx

    def handle_failure(self, failure: FailureEvent) -> RetryDecision:
        self.ctx.update_time()
        decision = RetryPolicy.decide(self.ctx, failure)

        if decision in (
            RetryDecision.RETRY_NOW,
            RetryDecision.RETRY_BACKOFF,
        ):
            self.ctx.record_retry(failure.failure_class)

        if decision == RetryDecision.QUARANTINE_AND_CONTINUE:
            self.ctx.record_quarantine()

        return decision


  