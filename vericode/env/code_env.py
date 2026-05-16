"""
VericodeEnv: Reproducible Gymnasium-compatible RL Environment for Code Generation & Refactoring.
"""

from typing import Any, Dict, Optional, Tuple
from vericode.env.rewards import RewardModel
from vericode.tasks.registry import TaskRegistry, GLOBAL_REGISTRY
from vericode.tasks.task_spec import TaskSpec
from vericode.verifier.deterministic import MultiTierVerifier


class VericodeEnv:
    """
    Reinforcement Learning Environment for code synthesis and debugging agents.
    Complies with standard Agent-Environment interface (reset, step, render).
    """

    def __init__(
        self,
        task_id: Optional[str] = "TASK-001",
        registry: Optional[TaskRegistry] = None,
        max_steps: int = 5,
        dense_rewards: bool = True,
    ):
        self.registry = registry or GLOBAL_REGISTRY
        self.default_task_id = task_id
        self.max_steps = max_steps
        self.verifier = MultiTierVerifier()
        self.reward_model = RewardModel(dense_shaping=dense_rewards)

        self.current_task: Optional[TaskSpec] = None
        self.current_code: str = ""
        self.step_count: int = 0
        self.last_feedback: str = ""
        self.done: bool = False

    def reset(
        self,
        task_id: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        target_id = task_id or self.default_task_id
        self.current_task = self.registry.get(target_id)
        if not self.current_task:
            raise ValueError(f"Task '{target_id}' not found in registry")

        self.current_code = self.current_task.base_code
        self.step_count = 0
        self.last_feedback = "Task initialized with base template."
        self.done = False

        obs = self._get_observation()
        info = {"task_id": self.current_task.task_id, "difficulty": self.current_task.difficulty}
        return obs, info

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, bool, Dict[str, Any]]:
        """
        Execute an agent action.
        Action format:
          {"action_type": "replace_code", "code": str}
        """
        if self.done:
            raise RuntimeError("Cannot step in terminated environment. Call reset() first.")

        self.step_count += 1
        action_type = action.get("action_type", "replace_code")

        if action_type in ("replace_code", "apply_code"):
            self.current_code = action.get("code", self.current_code)

        # Run deterministic verification
        report = self.verifier.verify(self.current_task, self.current_code)
        self.last_feedback = report.feedback

        terminated = report.overall_passed
        truncated = self.step_count >= self.max_steps
        self.done = terminated or truncated

        reward = self.reward_model.calculate_reward(report, is_terminal=self.done)

        obs = self._get_observation()
        info = {
            "overall_passed": report.overall_passed,
            "score": report.score,
            "step_count": self.step_count,
            "tier_reports": [
                {"tier": tr.tier.value, "passed": tr.passed, "message": tr.message}
                for tr in report.tier_results
            ],
        }

        return obs, reward, terminated, truncated, info

    def _get_observation(self) -> Dict[str, Any]:
        return {
            "task_id": self.current_task.task_id,
            "title": self.current_task.title,
            "category": self.current_task.category,
            "description": self.current_task.description,
            "target_filename": self.current_task.target_filename,
            "current_code": self.current_code,
            "step_count": self.step_count,
            "last_feedback": self.last_feedback,
        }

    def render(self) -> str:
        return (
            f"=== VericodeEnv Step {self.step_count}/{self.max_steps} ===\n"
            f"Task: {self.current_task.task_id} ({self.current_task.title})\n"
            f"Feedback: {self.last_feedback}\n"
        )
