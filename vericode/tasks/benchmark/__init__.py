"""
Benchmark tasks catalog.
"""

from vericode.tasks.benchmark.task_001 import TASK_001
from vericode.tasks.benchmark.task_002 import TASK_002
from vericode.tasks.benchmark.task_003 import TASK_003
from vericode.tasks.benchmark.task_004 import TASK_004

ALL_TASKS = [
    TASK_001,
    TASK_002,
    TASK_003,
    TASK_004,
]

__all__ = [
    "ALL_TASKS",
    "TASK_001",
    "TASK_002",
    "TASK_003",
    "TASK_004",
]
