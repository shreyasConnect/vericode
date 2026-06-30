"""
TASK-001: Thread-Safe Concurrent LRU Cache (Concurrency Bug Fix).
"""

from vericode.tasks.task_spec import TaskSpec

BASE_CODE = '''"""
Thread-unsafe LRU Cache Implementation.
BUG: Race condition during concurrent get/put/eviction operations and telemetry counter corruption.
"""

from collections import OrderedDict
from typing import Any, Optional

class ConcurrentLRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            cur_miss = self.miss_count
            self.miss_count = cur_miss + 1
            return None
        self.cache.move_to_end(key)
        cur_hit = self.hit_count
        self.hit_count = cur_hit + 1
        return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def size(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        self.cache.clear()
        self.hit_count = 0
        self.miss_count = 0
'''

GOLDEN_SOLUTION = '''"""
Thread-Safe Concurrent LRU Cache Implementation.
FIX: Synchronized using reentrant locks to guarantee atomicity and invariant retention under contention.
"""

from collections import OrderedDict
import threading
from typing import Any, Optional

class ConcurrentLRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.cache = OrderedDict()
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self.cache:
                self.miss_count += 1
                return None
            self.cache.move_to_end(key)
            self.hit_count += 1
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    def size(self) -> int:
        with self._lock:
            return len(self.cache)

    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
            self.hit_count = 0
            self.miss_count = 0
'''

PUBLIC_TESTS = '''
from lru_cache import ConcurrentLRUCache

def test_basic_get_put():
    cache = ConcurrentLRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    assert cache.get("b") == 2
    assert cache.hit_count == 2
    assert cache.get("missing") is None
    assert cache.miss_count == 1

def test_eviction():
    cache = ConcurrentLRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3

def test_delete():
    cache = ConcurrentLRUCache(2)
    cache.put("x", 42)
    assert cache.delete("x") is True
    assert cache.delete("x") is False
    assert cache.get("x") is None

if __name__ == "__main__":
    test_basic_get_put()
    test_eviction()
    test_delete()
    print("ALL_PUBLIC_TESTS_PASSED")
'''

HIDDEN_TESTS = '''
from concurrent.futures import ThreadPoolExecutor
import random
import sys
import time
from lru_cache import ConcurrentLRUCache

def test_concurrent_stress():
    sys.setswitchinterval(0.00001)
    capacity = 15
    cache = ConcurrentLRUCache(capacity)
    ops_per_worker = 200
    num_workers = 6
    errors = []

    def worker(worker_id):
        rnd = random.Random(42 + worker_id)
        for i in range(ops_per_worker):
            op = rnd.choice(["get", "put", "delete", "size"])
            key = f"key_{rnd.randint(0, 10)}"
            try:
                if op == "get":
                    cache.get(key)
                elif op == "put":
                    cache.put(key, f"val_{i}")
                elif op == "delete":
                    cache.delete(key)
                elif op == "size":
                    sz = cache.size()
                    if sz > capacity:
                        errors.append(f"Capacity exceeded: {sz} > {capacity}")
            except Exception as e:
                errors.append(f"Worker {worker_id} exception on {op}: {type(e).__name__} - {e}")

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker, w) for w in range(num_workers)]
        for f in futures:
            f.result()

    assert len(errors) == 0, f"Encountered concurrency errors: {errors[:5]}"
    assert cache.size() <= capacity, f"Final cache size {cache.size()} exceeds {capacity}"

def test_concurrent_telemetry_atomicity():
    sys.setswitchinterval(0.00001)
    cache = ConcurrentLRUCache(20)
    cache.put("shared", 999)
    total_calls = 500
    workers = 5

    def reader():
        for _ in range(total_calls // workers):
            cache.get("shared")
            cache.get("non_existent")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(reader) for _ in range(workers)]
        for f in futures:
            f.result()

    expected_hits = total_calls
    expected_misses = total_calls
    assert cache.hit_count == expected_hits, f"Hit count corruption: {cache.hit_count} != {expected_hits}"
    assert cache.miss_count == expected_misses, f"Miss count corruption: {cache.miss_count} != {expected_misses}"

if __name__ == "__main__":
    test_concurrent_stress()
    test_concurrent_telemetry_atomicity()
    print("ALL_HIDDEN_TESTS_PASSED")
'''

TASK_001 = TaskSpec(
    task_id="TASK-001",
    title="Thread-Safe Concurrent LRU Cache",
    category="bugfix",
    difficulty="medium",
    description=(
        "Fix concurrency race conditions in ConcurrentLRUCache where multi-threaded reads, "
        "writes, and evictions cause dictionary mutation exceptions (KeyError / RuntimeError) "
        "and violation of capacity constraints. Ensure all operations remain thread-safe without deadlocks."
    ),
    target_filename="lru_cache.py",
    base_code=BASE_CODE,
    public_tests=PUBLIC_TESTS,
    hidden_tests=HIDDEN_TESTS,
    golden_solution=GOLDEN_SOLUTION,
    tags=["concurrency", "lru-cache", "multithreading", "data-structures"],
)
