
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class GoalState:
    goal: str
    requirements: List[str]
    covered_requirements: List[str] = field(default_factory=list)
    evidence_summary: List[Dict] = field(default_factory=list)
    step_count: int = 0
    max_steps: int = 10
    halted: bool = False
    halt_reason: str = None

    def is_complete(self) -> bool:
        return set(self.requirements) == set(self.covered_requirements)

    def increment_step(self):
        self.step_count += 1

    def should_force_halt(self) -> bool:
        return self.step_count >= self.max_steps
