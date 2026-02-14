
import argparse
from tools.http.client import HttpClient
from tools.http.timeouts import TimeoutConfig
from tools.crawl.robots import RobotsPolicy
from evidence.store import EvidenceStore
from orchestrator.execution_context import ExecutionContext
from orchestrator.research_agent import ResearchAgent


def main():

    parser = argparse.ArgumentParser(
        description="Provenance Autonomous Research Agent"
    )
    parser.add_argument(
        "--goal",
        required=True,
        help="Research goal for the agent"
    )
    args = parser.parse_args()

    # ---- core infrastructure setup ----
    ctx = ExecutionContext()
    http = HttpClient(TimeoutConfig())
    robots = RobotsPolicy(http)
    evidence = EvidenceStore("./evidence_data")

    # ---- initialize research agent ----
    agent = ResearchAgent(
        goal=args.goal,
        execution_context=ctx,
        http_client=http,
        robots_policy=robots,
        evidence_store=evidence,
    )

    # ---- run agent loop ----
    result = agent.run()

    print("\n=== AGENT HALTED ===")
    print("Reason:", result.get("halt_reason"))
    print("Steps taken:", result.get("steps_taken"))


if __name__ == "__main__":
    main()
