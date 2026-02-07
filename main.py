# main.py

from tools.http.client import HttpClient
from tools.http.timeouts import TimeoutConfig
from tools.crawl.robots import RobotsPolicy
from tools.crawl.fetch_page import fetch_page
from evidence.store import EvidenceStore
from orchestrator.execution_context import ExecutionContext
from orchestrator.failure_event import FailureEvent

def main():
    # ---- setup ----
    ctx = ExecutionContext()
    http = HttpClient(TimeoutConfig())
    robots = RobotsPolicy(http)
    evidence = EvidenceStore("./evidence_data")

    url = "https://www.udemy.com"

    print(f"\nFetching: {url}\n")

    result = fetch_page(url, http, robots)

    # ---- failure path ----
    if isinstance(result, FailureEvent):
        print("❌ FETCH FAILED")
        print("Failure class:", result.failure_class)
        print("Message:", result.message)
        return

    # ---- success path ----
    evidence_id = evidence.write(result)
    ctx.record_evidence(len(result["body"]))

    print("✅ FETCH SUCCESS")
    print("Evidence ID:", evidence_id)
    print("Bytes stored:", len(result["body"]))

if __name__ == "__main__":
    main()
