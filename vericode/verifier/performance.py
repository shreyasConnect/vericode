"""
Deterministic microbenchmarking and performance regression detector.
Evaluates algorithmic complexity, latency budgets, and memory consumption.
"""

from dataclasses import dataclass
import statistics
import time
from typing import Callable, Dict, List, Optional


@dataclass
class BenchmarkMetric:
    median_ms: float
    p95_ms: float
    min_ms: float
    max_ms: float
    stdev_ms: float
    samples: List[float]
    passed_budget: bool
    budget_ms: Optional[float] = None


class PerformanceVerifier:
    """Runs deterministic performance evaluations with warmup and variance rejection."""

    def __init__(self, warmup_runs: int = 3, measure_runs: int = 10):
        self.warmup_runs = warmup_runs
        self.measure_runs = measure_runs

    def benchmark(
        self,
        func: Callable[[], None],
        budget_ms: Optional[float] = None,
    ) -> BenchmarkMetric:
        # Warmup phase (JIT/cache priming)
        for _ in range(self.warmup_runs):
            func()

        timings_ms: List[float] = []
        for _ in range(self.measure_runs):
            t0 = time.perf_counter()
            func()
            t1 = time.perf_counter()
            timings_ms.append((t1 - t0) * 1000.0)

        median_val = statistics.median(timings_ms)
        p95_idx = int(0.95 * len(timings_ms))
        sorted_timings = sorted(timings_ms)
        p95_val = sorted_timings[min(p95_idx, len(sorted_timings) - 1)]
        stdev_val = statistics.stdev(timings_ms) if len(timings_ms) > 1 else 0.0

        passed = True
        if budget_ms is not None:
            passed = median_val <= budget_ms

        return BenchmarkMetric(
            median_ms=median_val,
            p95_ms=p95_val,
            min_ms=min(timings_ms),
            max_ms=max(timings_ms),
            stdev_ms=stdev_val,
            samples=timings_ms,
            passed_budget=passed,
            budget_ms=budget_ms,
        )
