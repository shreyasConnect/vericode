"""
Task Registry for registering, retrieving, and cataloging evaluation benchmarks.
"""

from typing import Dict, List, Optional
from vericode.tasks.task_spec import TaskSpec
from vericode.tasks.benchmark import ALL_TASKS


class TaskRegistry:
    """Thread-safe catalog of benchmark task specifications."""

    def __init__(self):
        self._tasks: Dict[str, TaskSpec] = {}
        for task in ALL_TASKS:
            self.register(task)

    def register(self, task: TaskSpec) -> None:
        if task.task_id in self._tasks:
            raise ValueError(f"Task with id {task.task_id} is already registered")
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Optional[TaskSpec]:
        return self._tasks.get(task_id)

    def list_all(self) -> List[TaskSpec]:
        return list(self._tasks.values())

    def filter_by_category(self, category: str) -> List[TaskSpec]:
        return [t for t in self._tasks.values() if t.category.lower() == category.lower()]


GLOBAL_REGISTRY = TaskRegistry()


def get_task(task_id: str) -> Optional[TaskSpec]:
    return GLOBAL_REGISTRY.get(task_id)


def list_tasks() -> List[TaskSpec]:
    return GLOBAL_REGISTRY.list_all()
