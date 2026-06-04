"""
Task specification schema and data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TaskSpec:
    task_id: str
    title: str
    category: str  # 'bugfix' | 'feature' | 'refactor' | 'performance'
    difficulty: str  # 'medium' | 'hard'
    description: str
    target_filename: str
    base_code: str
    public_tests: str
    hidden_tests: str
    golden_solution: str
    regression_tests: Optional[str] = None
    performance_budget_ms: Optional[float] = None
    benchmark_code: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "category": self.category,
            "difficulty": self.difficulty,
            "description": self.description,
            "target_filename": self.target_filename,
            "tags": self.tags,
            "has_performance_budget": self.performance_budget_ms is not None,
            "performance_budget_ms": self.performance_budget_ms,
        }
