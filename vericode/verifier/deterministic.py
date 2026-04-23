"""
Multi-Tier Deterministic Verifier Engine.
Executes progressive tiers of verification: AST safety, public acceptance, hidden invariants, and performance budgets.
"""

import time
from typing import Dict, Optional

from vericode.sandbox.executor import SandboxExecutor
from vericode.tasks.task_spec import TaskSpec
from vericode.verifier.ast_guard import inspect_code_ast
from vericode.verifier.base import MultiTierReport, TierResult, VerificationTier


class MultiTierVerifier:
    """Deterministic verifier that accepts only provably correct solutions."""

    def __init__(
        self,
        sandbox: Optional[SandboxExecutor] = None,
        timeout_seconds: float = 10.0,
    ):
        self.sandbox = sandbox or SandboxExecutor(timeout_seconds=timeout_seconds)

    def verify(self, task: TaskSpec, candidate_code: str) -> MultiTierReport:
        t0 = time.perf_counter()
        tier_results = []
        feedback_lines = []

        # ==========================================
        # Tier 1: AST Safety & Anti-Tampering Guard
        # ==========================================
        t_tier0 = time.perf_counter()
        is_safe, violations = inspect_code_ast(candidate_code)
        tier1_duration = (time.perf_counter() - t_tier0) * 1000.0

        if not is_safe:
            violation_details = "; ".join([f"L{v.line_number}: {v.description}" for v in violations])
            tier_results.append(
                TierResult(
                    tier=VerificationTier.AST_GUARD,
                    passed=False,
                    message=f"AST verification failed: {violation_details}",
                    duration_ms=tier1_duration,
                    details={"violations": [v.__dict__ for v in violations]},
                )
            )
            feedback_lines.append(f"[Tier 1 FAILED] Code failed AST safety verification: {violation_details}")
            total_duration = (time.perf_counter() - t0) * 1000.0
            return MultiTierReport(
                task_id=task.task_id,
                overall_passed=False,
                score=0.0,
                tier_results=tier_results,
                total_duration_ms=total_duration,
                feedback="\n".join(feedback_lines),
            )

        tier_results.append(
            TierResult(
                tier=VerificationTier.AST_GUARD,
                passed=True,
                message="AST safety checks passed.",
                duration_ms=tier1_duration,
            )
        )
        feedback_lines.append("[Tier 1 PASSED] AST inspection passed.")

        # ==========================================
        # Tier 2: Public Acceptance Tests
        # ==========================================
        files_for_public = {
            task.target_filename: candidate_code,
            "test_runner.py": task.public_tests,
        }
        res_public = self.sandbox.run_isolated(files_for_public, "test_runner.py")
        tier2_passed = res_public.passed and "ALL_PUBLIC_TESTS_PASSED" in res_public.stdout

        tier_results.append(
            TierResult(
                tier=VerificationTier.PUBLIC_TESTS,
                passed=tier2_passed,
                message="Public acceptance tests passed." if tier2_passed else f"Public test failure: {res_public.stderr or res_public.stdout}",
                duration_ms=res_public.duration_ms,
                details={"stdout": res_public.stdout, "stderr": res_public.stderr},
            )
        )

        if not tier2_passed:
            feedback_lines.append(f"[Tier 2 FAILED] Public tests failed: {res_public.stderr or res_public.stdout}")
            total_duration = (time.perf_counter() - t0) * 1000.0
            return MultiTierReport(
                task_id=task.task_id,
                overall_passed=False,
                score=0.25,
                tier_results=tier_results,
                total_duration_ms=total_duration,
                feedback="\n".join(feedback_lines),
            )

        feedback_lines.append("[Tier 2 PASSED] Public tests passed.")

        # ==========================================
        # Tier 3: Hidden Invariant & Property Tests
        # ==========================================
        files_for_hidden = {
            task.target_filename: candidate_code,
            "hidden_runner.py": task.hidden_tests,
        }
        res_hidden = self.sandbox.run_isolated(files_for_hidden, "hidden_runner.py")
        tier3_passed = res_hidden.passed and "ALL_HIDDEN_TESTS_PASSED" in res_hidden.stdout

        tier_results.append(
            TierResult(
                tier=VerificationTier.HIDDEN_INVARIANTS,
                passed=tier3_passed,
                message="Hidden invariant tests passed." if tier3_passed else f"Hidden invariant failure: {res_hidden.stderr or res_hidden.stdout}",
                duration_ms=res_hidden.duration_ms,
                details={"stdout": res_hidden.stdout, "stderr": res_hidden.stderr},
            )
        )

        if not tier3_passed:
            feedback_lines.append(f"[Tier 3 FAILED] Hidden invariant tests failed: {res_hidden.stderr or res_hidden.stdout}")
            total_duration = (time.perf_counter() - t0) * 1000.0
            return MultiTierReport(
                task_id=task.task_id,
                overall_passed=False,
                score=0.60,
                tier_results=tier_results,
                total_duration_ms=total_duration,
                feedback="\n".join(feedback_lines),
            )

        feedback_lines.append("[Tier 3 PASSED] Hidden invariant tests passed.")

        # ==========================================
        # Tier 4: Performance / Latency Budget (if applicable)
        # ==========================================
        overall_passed = True
        score = 1.0

        if task.performance_budget_ms is not None:
            # Re-run hidden suite duration check or check duration
            perf_passed = res_hidden.duration_ms <= (task.performance_budget_ms * 3.0)  # Total harness runtime
            tier_results.append(
                TierResult(
                    tier=VerificationTier.PERFORMANCE,
                    passed=perf_passed,
                    message=f"Performance latency within budget ({res_hidden.duration_ms:.2f}ms)" if perf_passed else f"Performance budget exceeded: {res_hidden.duration_ms:.2f}ms",
                    duration_ms=res_hidden.duration_ms,
                    details={"budget_ms": task.performance_budget_ms, "actual_ms": res_hidden.duration_ms},
                )
            )
            if not perf_passed:
                overall_passed = False
                score = 0.85
                feedback_lines.append(f"[Tier 4 FAILED] Solution passed correctness but exceeded performance budget.")
            else:
                feedback_lines.append(f"[Tier 4 PASSED] Solution satisfied performance budget.")

        total_duration = (time.perf_counter() - t0) * 1000.0
        return MultiTierReport(
            task_id=task.task_id,
            overall_passed=overall_passed,
            score=score if overall_passed else min(score, 0.85),
            tier_results=tier_results,
            total_duration_ms=total_duration,
            feedback="\n".join(feedback_lines),
        )
