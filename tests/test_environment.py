"""
Tests for VericodeEnv RL gym interface.
"""

from vericode.env.code_env import VericodeEnv
from vericode.tasks.registry import GLOBAL_REGISTRY


def test_env_initialization_and_reset():
    env = VericodeEnv(task_id="TASK-001")
    obs, info = env.reset()
    assert obs["task_id"] == "TASK-001"
    assert "ConcurrentLRUCache" in obs["current_code"]
    assert obs["step_count"] == 0
    assert info["difficulty"] == "medium"


def test_env_step_with_golden_solution():
    task = GLOBAL_REGISTRY.get("TASK-001")
    env = VericodeEnv(task_id="TASK-001", max_steps=3)
    env.reset()

    action = {
        "action_type": "replace_code",
        "code": task.golden_solution,
    }
    obs, reward, terminated, truncated, info = env.step(action)

    assert terminated is True
    assert reward > 0.8
    assert info["overall_passed"] is True
    assert info["score"] == 1.0


def test_env_truncation_on_max_steps():
    env = VericodeEnv(task_id="TASK-002", max_steps=2)
    env.reset()

    # Step 1 with broken code
    obs, reward, term1, trunc1, _ = env.step({"action_type": "replace_code", "code": "# bad code"})
    assert term1 is False
    assert trunc1 is False

    # Step 2 reaching max_steps
    obs, reward, term2, trunc2, _ = env.step({"action_type": "replace_code", "code": "# still bad"})
    assert trunc2 is True
