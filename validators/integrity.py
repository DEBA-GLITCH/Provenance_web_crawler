
import math
from collections import Counter
from typing import Dict, List


class IntegrityResult:
    """
    Deterministic integrity assessment.
    This object is attached as metadata, never mutates evidence.
    """

    def __init__(
        self,
        integrity_score: float,
        usable_for_reasoning: bool,
        flags: List[str],
        metrics: Dict[str, float],
        validator_version: str = "integrity_v1",
    ):
        self.integrity_score = integrity_score
        self.usable_for_reasoning = usable_for_reasoning
        self.flags = flags
        self.metrics = metrics
        self.validator_version = validator_version

    def to_dict(self) -> dict:
        return {
            "integrity_score": self.integrity_score,
            "usable_for_reasoning": self.usable_for_reasoning,
            "flags": self.flags,
            "metrics": self.metrics,
            "validator_version": self.validator_version,
        }


class IntegrityEvaluator:
    """
    Signal-quality gates operating on raw bytes.
    NO parsing. NO NLP. NO semantics.
    """

    # ---- tunable thresholds ----
    MIN_SCORE = 0.45
    MAX_REPETITION_RATIO = 0.35
    MIN_UNIQUE_RATIO = 0.08
    ENTROPY_RANGE = (3.5, 7.5)  # bits per byte

    @staticmethod
    def evaluate(raw: bytes) -> IntegrityResult:
        flags = []
        metrics = {}

        length = len(raw)
        metrics["byte_length"] = length

        if length == 0:
            return IntegrityEvaluator._fail(
                "empty_content", metrics
            )

        entropy = IntegrityEvaluator._shannon_entropy(raw)
        metrics["entropy"] = entropy

        if entropy < IntegrityEvaluator.ENTROPY_RANGE[0]:
            flags.append("low_entropy_template_like")

        if entropy > IntegrityEvaluator.ENTROPY_RANGE[1]:
            flags.append("high_entropy_noise_like")

        repetition_ratio = IntegrityEvaluator._repetition_ratio(raw)
        metrics["repetition_ratio"] = repetition_ratio

        if repetition_ratio > IntegrityEvaluator.MAX_REPETITION_RATIO:
            flags.append("excessive_repetition")

        unique_ratio = IntegrityEvaluator._unique_byte_ratio(raw)
        metrics["unique_byte_ratio"] = unique_ratio

        if unique_ratio < IntegrityEvaluator.MIN_UNIQUE_RATIO:
            flags.append("low_unique_content")

        integrity_score = IntegrityEvaluator._compose_score(
            entropy,
            repetition_ratio,
            unique_ratio,
        )

        usable = (
            integrity_score >= IntegrityEvaluator.MIN_SCORE
            and len(flags) == 0
        )

        return IntegrityResult(
            integrity_score=integrity_score,
            usable_for_reasoning=usable,
            flags=flags,
            metrics=metrics,
        )

    # ---------- helpers ----------

    @staticmethod
    def _fail(reason: str, metrics: Dict[str, float]) -> IntegrityResult:
        return IntegrityResult(
            integrity_score=0.0,
            usable_for_reasoning=False,
            flags=[reason],
            metrics=metrics,
        )

    @staticmethod
    def _shannon_entropy(data: bytes) -> float:
        """
        Bits per byte.
        """
        counts = Counter(data)
        total = len(data)

        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)

        return entropy

    @staticmethod
    def _repetition_ratio(data: bytes) -> float:
        """
        Measures dominance of most common byte.
        """
        counts = Counter(data)
        most_common = counts.most_common(1)[0][1]
        return most_common / len(data)

    @staticmethod
    def _unique_byte_ratio(data: bytes) -> float:
        return len(set(data)) / len(data)
