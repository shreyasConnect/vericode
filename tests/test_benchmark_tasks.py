"""
Integration tests for benchmark catalog and golden solutions.
"""

from vericode.tasks.registry import GLOBAL_REGISTRY
from vericode.verifier.deterministic import MultiTierVerifier


def test_registry_contains_all_tasks():
    tasks = GLOBAL_REGISTRY.list_all()
    assert len(tasks) >= 4
    task_ids = {t.task_id for t in tasks}
    assert "TASK-001" in task_ids
    assert "TASK-002" in task_ids
    assert "TASK-003" in task_ids
    assert "TASK-004" in task_ids


def test_task_001_golden_passes():
    task = GLOBAL_REGISTRY.get("TASK-001")
    verifier = MultiTierVerifier(timeout_seconds=10.0)
    report = verifier.verify(task, task.golden_solution)
    assert report.overall_passed is True
    assert report.score == 1.0


def test_task_002_golden_passes():
    task = GLOBAL_REGISTRY.get("TASK-002")
    verifier = MultiTierVerifier(timeout_seconds=10.0)
    report = verifier.verify(task, task.golden_solution)
    assert report.overall_passed is True
    assert report.score == 1.0


def test_task_003_golden_passes():
    task = GLOBAL_REGISTRY.get("TASK-003")
    verifier = MultiTierVerifier(timeout_seconds=10.0)
    report = verifier.verify(task, task.golden_solution)
    assert report.overall_passed is True
    assert report.score == 1.0


def test_task_004_golden_passes():
    task = GLOBAL_REGISTRY.get("TASK-004")
    verifier = MultiTierVerifier(timeout_seconds=10.0)
    report = verifier.verify(task, task.golden_solution)
    assert report.overall_passed is True
    assert report.score == 1.0


def test_base_code_fails_verification():
    # Base code of TASK-002 has NotImplementedError
    task = GLOBAL_REGISTRY.get("TASK-002")
    verifier = MultiTierVerifier(timeout_seconds=5.0)
    report = verifier.verify(task, task.base_code)
    assert report.overall_passed is False
    assert report.score < 1.0
