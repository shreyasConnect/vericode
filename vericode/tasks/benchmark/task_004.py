"""
TASK-004: Zero-Copy Streaming NDJSON Log Parser (Performance Optimization).
"""

from vericode.tasks.task_spec import TaskSpec

BASE_CODE = '''"""
NDJSON Log Parser.
BOTTLENECK: High allocation overhead and regex scanning make this too slow
for high-throughput streaming environments.
"""

import json
import re
from typing import Any, Dict, Iterator, List

class NDJSONParser:
    def __init__(self):
        self.raw_records: List[str] = []

    def parse_stream(self, stream_data: str) -> List[Dict[str, Any]]:
        # Inefficient implementation: regex splitting and duplicated memory buffers
        self.raw_records = re.split(r'\\r?\\n', stream_data)
        parsed = []
        for line in self.raw_records:
            cleaned = line.strip()
            if not cleaned:
                continue
            try:
                obj = json.loads(cleaned)
                if isinstance(obj, dict):
                    parsed.append(obj)
            except Exception:
                continue
        return parsed
'''

GOLDEN_SOLUTION = '''"""
NDJSON Log Parser.
OPTIMIZED: Generator-based streaming with zero unnecessary intermediate buffer copies.
"""

import json
from typing import Any, Dict, Iterator, List

class NDJSONParser:
    def parse_stream(self, stream_data: str) -> List[Dict[str, Any]]:
        parsed: List[Dict[str, Any]] = []
        for line in stream_data.splitlines():
            line_str = line.strip()
            if not line_str or line_str[0] != '{':
                continue
            try:
                obj = json.loads(line_str)
                if isinstance(obj, dict):
                    parsed.append(obj)
            except Exception:
                continue
        return parsed

    def parse_generator(self, stream_data: str) -> Iterator[Dict[str, Any]]:
        for line in stream_data.splitlines():
            line_str = line.strip()
            if not line_str or line_str[0] != '{':
                continue
            try:
                obj = json.loads(line_str)
                if isinstance(obj, dict):
                    yield obj
            except Exception:
                continue
'''

PUBLIC_TESTS = '''
import json
from log_parser import NDJSONParser

def test_basic_parsing():
    parser = NDJSONParser()
    data = '{"id": 1, "status": "ok"}\\n{"id": 2, "status": "error"}\\n'
    records = parser.parse_stream(data)
    assert len(records) == 2
    assert records[0]["id"] == 1
    assert records[1]["status"] == "error"

def test_empty_and_corrupt_lines():
    parser = NDJSONParser()
    data = '\\n{"valid": true}\\ncorrupt_json_line\\n\\n{"valid": false}\\n'
    records = parser.parse_stream(data)
    assert len(records) == 2
    assert records[0]["valid"] is True
    assert records[1]["valid"] is False

if __name__ == "__main__":
    test_basic_parsing()
    test_empty_and_corrupt_lines()
    print("ALL_PUBLIC_TESTS_PASSED")
'''

HIDDEN_TESTS = '''
import json
import time
from log_parser import NDJSONParser

def test_large_payload_and_latency():
    # Generate 2,000 log lines
    lines = [json.dumps({"seq": i, "level": "INFO", "msg": f"event_{i}"}) for i in range(2000)]
    payload = "\\n".join(lines)

    parser = NDJSONParser()
    t0 = time.perf_counter()
    records = parser.parse_stream(payload)
    t1 = time.perf_counter()

    elapsed_ms = (t1 - t0) * 1000.0
    assert len(records) == 2000
    assert records[0]["seq"] == 0
    assert records[-1]["seq"] == 1999
    # Must parse 2000 lines within 100ms
    assert elapsed_ms < 100.0, f"Parser too slow: {elapsed_ms:.2f}ms"

if __name__ == "__main__":
    test_large_payload_and_latency()
    print("ALL_HIDDEN_TESTS_PASSED")
'''

TASK_004 = TaskSpec(
    task_id="TASK-004",
    title="Zero-Copy Streaming NDJSON Log Parser",
    category="performance",
    difficulty="medium",
    description=(
        "Optimize the high-throughput `NDJSONParser.parse_stream` in `log_parser.py`. "
        "The legacy implementation wastes CPU time with inefficient regex splitting and string copying. "
        "The optimized parser must skip corrupt/non-JSON lines gracefully and pass strict throughput latency budgets."
    ),
    target_filename="log_parser.py",
    base_code=BASE_CODE,
    public_tests=PUBLIC_TESTS,
    hidden_tests=HIDDEN_TESTS,
    golden_solution=GOLDEN_SOLUTION,
    performance_budget_ms=1000.0,
    tags=["ndjson", "streaming", "performance-optimization", "zero-copy"],
)
