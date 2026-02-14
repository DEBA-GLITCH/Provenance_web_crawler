# orchestrator/research_agent.py

from typing import Set, Dict, List
from orchestrator.goal_state import GoalState
from orchestrator.planner import plan_next_action
from orchestrator.action_types import ActionType
from tools.crawl.fetch_page import fetch_page
from orchestrator.failure_event import FailureEvent
from retrieval.retriever import retrieve_context
from llm.reasoner import grounded_reason


class ResearchAgent:

    def __init__(
        self,
        goal: str,
        execution_context,
        http_client,
        robots_policy,
        evidence_store,
    ):
        self.ctx = execution_context
        self.http = http_client
        self.robots = robots_policy
        self.evidence = evidence_store

        self.state = GoalState(
            goal=goal,
            requirements=[goal],  # placeholder ECC
        )

        # --- Active Constraint Layer ---
        self.visited_urls: Set[str] = set()
        self.previous_queries: Set[str] = set()
        self.last_actions: List[str] = []
        self.no_progress_steps = 0

    # --------------------------------------------------
    # State Map for Planner
    # --------------------------------------------------

    def build_state_map(self) -> Dict:
        return {
            "goal": self.state.goal,
            "requirements": self.state.requirements,
            "covered_requirements": self.state.covered_requirements,
            "evidence_count": len(self.state.evidence_summary),
            "step_count": self.state.step_count,
            "max_steps": self.state.max_steps,
            "recent_actions": self.last_actions[-5:],
        }

    # --------------------------------------------------
    # SEARCH (Stub: integrate your real search tool here)
    # --------------------------------------------------

    def execute_search(self, query: str):

        normalized = query.strip().lower()

        if normalized in self.previous_queries:
            print("⚠️ Duplicate query blocked")
            return

        self.previous_queries.add(normalized)

        print(f"🔎 SEARCH: {query}")

        # TODO: Replace with real search tool
        # For now, fake URL generation
        fake_url = f"https://example.com/search?q={normalized.replace(' ', '+')}"

        # Automatically push into FETCH queue
        self.execute_fetch(fake_url)

    # --------------------------------------------------
    # FETCH
    # --------------------------------------------------

    def execute_fetch(self, url: str):

        if url in self.visited_urls:
            print("⚠️ URL already visited, blocked")
            return

        self.visited_urls.add(url)

        print(f"🌐 FETCH: {url}")

        result = fetch_page(url, self.http, self.robots)

        if isinstance(result, FailureEvent):
            print("❌ Fetch failed:", result.message)
            return

        evidence_id = self.evidence.write(result)
        self.ctx.record_evidence(len(result["body"]))

        print("✅ Evidence stored:", evidence_id)

        # Minimal evidence summary for planner
        self.state.evidence_summary.append({
            "evidence_id": evidence_id,
            "source_url": url,
        })

    # --------------------------------------------------
    # REASON
    # --------------------------------------------------

    def execute_reason(self):

        print("🧠 REASONING...")

        blocks = retrieve_context(
            query=self.state.goal,
            base_path="./evidence_data"
        )

        if not blocks:
            print("⚠️ No usable context found")
            self.no_progress_steps += 1
            return

        result = grounded_reason(self.state.goal, blocks)

        if result["confidence"] > 0.75:
            print("🎯 Goal satisfied with confidence:", result["confidence"])
            self.state.covered_requirements = self.state.requirements.copy()
            self.state.halted = True
            self.state.halt_reason = "GOAL_SATISFIED"
        else:
            print("⚠️ Insufficient confidence:", result["confidence"])
            self.no_progress_steps += 1

    # --------------------------------------------------
    # Stagnation Detection
    # --------------------------------------------------

    def check_stagnation(self):

        if self.no_progress_steps >= 3:
            self.state.halted = True
            self.state.halt_reason = "STAGNATION_DETECTED"

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------

    def run(self):

        print("\n🚀 Autonomous Research Agent Started")
        print("Goal:", self.state.goal)

        while not self.state.halted:

            if self.state.should_force_halt():
                self.state.halted = True
                self.state.halt_reason = "MAX_STEPS_REACHED"
                break

            state_map = self.build_state_map()

            decision = plan_next_action(state_map)

            try:
                action = ActionType(decision["action"])
            except Exception:
                print("❌ Invalid planner action")
                self.state.halted = True
                self.state.halt_reason = "INVALID_PLANNER_ACTION"
                break

            self.last_actions.append(action.value)

            if action == ActionType.HALT:
                self.state.halted = True
                self.state.halt_reason = "PLANNER_HALTED"
                break

            if action == ActionType.SEARCH:
                self.execute_search(decision.get("query", ""))

            elif action == ActionType.FETCH:
                self.execute_fetch(decision.get("url", ""))

            elif action == ActionType.REASON:
                self.execute_reason()

            self.state.increment_step()

            self.check_stagnation()

        print("\n=== AGENT HALTED ===")
        print("Reason:", self.state.halt_reason)
        print("Steps:", self.state.step_count)

        return {
            "halt_reason": self.state.halt_reason,
            "steps_taken": self.state.step_count,
        }
