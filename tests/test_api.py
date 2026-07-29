"""
Tests for FastAPI REST endpoints.
"""

from fastapi.testclient import TestClient
from vericode.api.app import app
from vericode.tasks.registry import GLOBAL_REGISTRY

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_list_tasks_endpoint():
    res = client.get("/api/v1/tasks")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    task_ids = [t["task_id"] for t in data]
    assert "TASK-001" in task_ids


def test_get_single_task():
    res = client.get("/api/v1/tasks/TASK-001")
    assert res.status_code == 200
    data = res.json()
    assert data["task_id"] == "TASK-001"
    assert "ConcurrentLRUCache" in data["base_code"]


def test_verify_submission_endpoint():
    task = GLOBAL_REGISTRY.get("TASK-001")
    payload = {
        "task_id": "TASK-001",
        "code": task.golden_solution,
    }
    res = client.post("/api/v1/verify", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["overall_passed"] is True
    assert data["score"] == 1.0


def test_batch_eval_endpoint():
    task1 = GLOBAL_REGISTRY.get("TASK-001")
    task2 = GLOBAL_REGISTRY.get("TASK-002")
    payload = {
        "submissions": {
            "TASK-001": task1.golden_solution,
            "TASK-002": task2.base_code,  # will fail
        }
    }
    res = client.post("/api/v1/eval/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_tasks"] == 2
    assert data["passed_tasks"] == 1
    assert data["pass_rate"] == 50.0
