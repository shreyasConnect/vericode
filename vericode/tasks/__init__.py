"""
Benchmark tasks subsystem.
"""

from vericode.tasks.task_spec import TaskSpec
from vericode.tasks.registry import TaskRegistry, GLOBAL_REGISTRY, get_task, list_tasks

__all__ = [
    "TaskSpec",
    "TaskRegistry",
    "GLOBAL_REGISTRY",
    "get_task",
    "list_tasks",
]
