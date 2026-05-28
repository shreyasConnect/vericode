"""
Reward computation models for Reinforcement Learning agents in VericodeEnv.
Provides dense shaping signals (AST syntax, public tests) and sparse terminal rewards.
"""

from typing import Dict
from vericode.verifier.base import MultiTierReport, VerificationTier


class RewardModel:
    """Computes dense and sparse rewards from verification reports."""

    def __init__(
        self,
        dense_shaping: bool = True,
        success_reward: float = 1.0,
        step_penalty: float = -0.05,
    ):
        self.dense_shaping = dense_shaping
        self.success_reward = success_reward
        self.step_penalty = step_penalty

    def calculate_reward(self, report: MultiTierReport, is_terminal: bool) -> float:
        if report.overall_passed:
            return self.success_reward

        if not self.dense_shaping:
            return 0.0

        reward = self.step_penalty

        # Dense shaping rewards for intermediate progress
        ast_res = report.get_tier(VerificationTier.AST_GUARD)
        if ast_res and ast_res.passed:
            reward += 0.15

        pub_res = report.get_tier(VerificationTier.PUBLIC_TESTS)
        if pub_res and pub_res.passed:
            reward += 0.35

        hid_res = report.get_tier(VerificationTier.HIDDEN_INVARIANTS)
        if hid_res and hid_res.passed:
            reward += 0.30

        return round(reward, 3)
