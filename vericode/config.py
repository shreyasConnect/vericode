"""
Global configuration constants and environment presets for Vericode.
"""

from dataclasses import dataclass
import os

@dataclass(frozen=True)
class VericodeConfig:
    DEFAULT_TIMEOUT_SECONDS: float = 10.0
    BENCHMARK_TIMEOUT_SECONDS: float = 30.0
    MAX_MEMORY_MB: int = 512
    DEFAULT_RANDOM_SEED: int = 42
    MAX_EPISODE_STEPS: int = 10
    PYTHON_EXECUTABLE: str = os.environ.get("VERICODE_PYTHON", "py -3.9")
    STRICT_AST_SECURITY: bool = True
    WARMUP_ITERATIONS: int = 3
    BENCHMARK_ITERATIONS: int = 15

CONFIG = VericodeConfig()
