"""
TASK-002: Token Bucket Rate Limiter with Burst Control (Feature Implementation).
"""

from vericode.tasks.task_spec import TaskSpec

BASE_CODE = '''"""
Token Bucket Rate Limiter for API Gateways.
TODO: Implement token bucket algorithm with fractional refill and burst management.
"""

import time
from typing import Optional

class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: Maximum burst token capacity (must be > 0).
        refill_rate: Number of tokens replenished per second (must be > 0).
        """
        raise NotImplementedError("TokenBucketLimiter is not implemented")

    def allow(self, tokens: int = 1) -> bool:
        """
        Attempt to consume `tokens`. Return True if allowed and consumed, else False.
        """
        raise NotImplementedError()

    def tokens_available(self) -> float:
        """Return the current number of available tokens (capped at capacity)."""
        raise NotImplementedError()

    def reset(self) -> None:
        """Reset the bucket back to full capacity."""
        raise NotImplementedError()
'''

GOLDEN_SOLUTION = '''"""
Token Bucket Rate Limiter for API Gateways.
Implements token bucket algorithm with high-precision time replenishment and burst bounds.
"""

import threading
import time
from typing import Optional

class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("Refill rate must be positive")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self, current_time: float) -> None:
        elapsed = current_time - self.last_refill
        if elapsed > 0:
            added = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + added)
            self.last_refill = current_time

    def allow(self, tokens: int = 1) -> bool:
        if tokens <= 0:
            raise ValueError("Tokens to consume must be positive")
        with self._lock:
            now = time.time()
            self._refill(now)
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def tokens_available(self) -> float:
        with self._lock:
            now = time.time()
            self._refill(now)
            return self.tokens

    def reset(self) -> None:
        with self._lock:
            self.tokens = self.capacity
            self.last_refill = time.time()
'''

PUBLIC_TESTS = '''
import time
from rate_limiter import TokenBucketLimiter

def test_initial_burst():
    limiter = TokenBucketLimiter(capacity=5, refill_rate=1.0)
    assert limiter.tokens_available() == 5.0
    for _ in range(5):
        assert limiter.allow(1) is True
    assert limiter.allow(1) is False

def test_invalid_params():
    try:
        TokenBucketLimiter(0, 1.0)
        assert False, "Should raise ValueError on 0 capacity"
    except ValueError:
        pass

    limiter = TokenBucketLimiter(5, 1.0)
    try:
        limiter.allow(-1)
        assert False, "Should raise ValueError on negative tokens"
    except ValueError:
        pass

if __name__ == "__main__":
    test_initial_burst()
    test_invalid_params()
    print("ALL_PUBLIC_TESTS_PASSED")
'''

HIDDEN_TESTS = '''
import time
from rate_limiter import TokenBucketLimiter

def test_timed_refill():
    # 10 tokens per second -> 1 token every 100ms
    limiter = TokenBucketLimiter(capacity=2, refill_rate=10.0)
    assert limiter.allow(2) is True
    assert limiter.allow(1) is False

    # Sleep 150ms -> should have ~1.5 tokens, enough for 1
    time.sleep(0.15)
    assert limiter.allow(1) is True
    assert limiter.allow(1) is False

def test_reset():
    limiter = TokenBucketLimiter(capacity=3, refill_rate=0.5)
    assert limiter.allow(3) is True
    assert limiter.allow(1) is False
    limiter.reset()
    assert limiter.allow(2) is True

if __name__ == "__main__":
    test_timed_refill()
    test_reset()
    print("ALL_HIDDEN_TESTS_PASSED")
'''

TASK_002 = TaskSpec(
    task_id="TASK-002",
    title="Token Bucket Rate Limiter with Burst Control",
    category="feature",
    difficulty="medium",
    description=(
        "Implement a production-grade Token Bucket Rate Limiter (`TokenBucketLimiter`) in `rate_limiter.py`. "
        "The limiter must replenish tokens continuously based on elapsed time up to a maximum burst capacity, "
        "reject requests when insufficient tokens remain without deducting quota, and support atomic consumption."
    ),
    target_filename="rate_limiter.py",
    base_code=BASE_CODE,
    public_tests=PUBLIC_TESTS,
    hidden_tests=HIDDEN_TESTS,
    golden_solution=GOLDEN_SOLUTION,
    tags=["rate-limiting", "token-bucket", "algorithms", "backend"],
)
