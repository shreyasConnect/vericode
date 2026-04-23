"""
Base types and report structures for the multi-tier deterministic verification system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class VerificationTier(str, Enum):
    AST_GUARD = "ast_guard"
    REGRESSION = "regression"
    PUBLIC_TESTS = "public_tests"
    HIDDEN_INVARIANTS = "hidden_invariants"
    PERFORMANCE = "performance"


@dataclass
class TierResult:
    tier: VerificationTier
    passed: bool
    message: str
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiTierReport:
    task_id: str
    overall_passed: bool
    score: float  # Normalized 0.0 to 1.0
    tier_results: List[TierResult] = field(default_factory=list)
    total_duration_ms: float = 0.0
    feedback: str = ""

    def get_tier(self, tier: VerificationTier) -> Optional[TierResult]:
        for res in self.tier_results:
            if res.tier == tier:
                return res
        return None
