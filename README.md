# ⚡ Vericode

> **Reproducible Reinforcement Learning Benchmark & Deterministic Verifier Harness for Code Intelligence**

[![CI](https://github.com/shreyasconnect/vericode/actions/workflows/ci.yml/badge.svg)](https://github.com/shreyasconnect/vericode/actions)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Determinism](https://img.shields.io/badge/tests-deterministic-success.svg)](https://github.com/shreyasconnect/vericode)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 Motivation

Evaluating whether an AI code-generation model or Reinforcement Learning agent can truly solve real-world engineering problems requires far more than surface-level unit tests. In unconstrained code evaluation, models routinely encounter failure modes:
1. **Test-Tampering & Cheating**: Models inject mocks (`unittest.mock.patch`), overwrite assertion handlers, or manipulate `sys.modules` to artificially pass tests.
2. **Non-Deterministic Flakiness**: Concurrent code and stochastic timing yield false positives or flakiness.
3. **Overfitting to Public Specifications**: Candidates satisfy the public prompt while failing critical edge cases, memory limits, or invariant contracts.
4. **Algorithmic Inefficiency**: Solutions pass functional tests despite failing $O(N)$ or latency requirements.

**Vericode** solves this by providing an end-to-end framework:
- **Reproducible Gymnasium Environment (`VericodeEnv`)** for training RL code-synthesis agents.
- **Multi-Tier Deterministic Verifier** rejecting cheating, regressions, edge-case failures, and latency breaches.
- **Curated Benchmark Bank with Golden Reference Solutions** spanning concurrency bug fixing, rate limiter implementation, dependency graph refactoring, and zero-copy streaming log parsing.
- **Ephemeral Process Sandboxing** ensuring strict process isolation and timeout enforcement.
- **FastAPI Remote Evaluation Service & Rich CLI**.

---

## 🏗️ Architecture

```
                 +-----------------------------------+
                 |        AI / RL Coding Agent       |
                 +-----------------+-----------------+
                                   | (Actions: Code / Diff)
                                   v
+-------------------------------------------------------------------------+
|                              VericodeEnv                                |
|                        (Gymnasium RL Interface)                         |
+----------------------------------+--------------------------------------+
                                   |
                                   v
+-------------------------------------------------------------------------+
|                       MultiTierVerifier Pipeline                        |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | [Tier 1] AST Safety & Anti-Tamper Guard                            |  |
|  |   - Parse AST: Block eval/exec, sys.modules tampering, mock hacks |  |
|  +---------------------------------+---------------------------------+  |
|                                    v                                    |
|  +---------------------------------+---------------------------------+  |
|  | [Tier 2] Public Acceptance Specification Tests                    |  |
|  +---------------------------------+---------------------------------+  |
|                                    v                                    |
|  +---------------------------------+---------------------------------+  |
|  | [Tier 3] Hidden Deterministic Invariants & Stress Property Tests    |  |
|  |   - Fixed seed (seed=42), concurrent race condition fuzzers       |  |
|  +---------------------------------+---------------------------------+  |
|                                    v                                    |
|  +---------------------------------+---------------------------------+  |
|  | [Tier 4] Latency & Performance Budget Verifier                    |  |
|  |   - Warmup iterations, median/p95 latency enforcement             |  |
|  +-------------------------------------------------------------------+  |
+----------------------------------+--------------------------------------+
                                   |
                                   v
+-------------------------------------------------------------------------+
|                   SandboxExecutor (Ephemeral Process)                   |
|       - Subprocess tempdir isolation, timeout limits, stream capture    |
+-------------------------------------------------------------------------+
```

---

## 📦 Benchmark Tasks Catalog

Each benchmark problem is curated with a problem statement, buggy or stub baseline code, public specification tests, hidden deterministic verifiers, and an **expert golden reference solution**:

| Task ID | Title | Category | Difficulty | Verification Focus |
|---|---|---|---|---|
| `TASK-001` | **Concurrent LRU Cache** | Bug Fix | Medium | Multi-threaded locking, race conditions, atomic eviction |
| `TASK-002` | **Token Bucket Rate Limiter** | Feature | Medium | Continuous time replenishment, burst quota, boundary handling |
| `TASK-003` | **Dependency Graph Sorter** | Refactor | Hard | Kahn's algorithm, recursion elimination, cycle extraction |
| `TASK-004` | **Streaming NDJSON Log Parser** | Performance | Medium | Memory zero-copy, generator streaming, latency budget (<180ms) |

---

## 🚀 Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/shreyasconnect/vericode.git
cd vericode

# Install in editable mode
pip install -e .

# Or install dev dependencies
pip install -r requirements-dev.txt
```

### 2. Command Line Interface (CLI)

#### List Benchmark Tasks
```bash
python -m vericode list
```

#### Inspect Task Details
```bash
python -m vericode show TASK-001
```

#### Run Golden Benchmark Validation
```bash
python -m vericode bench --golden
```
Output:
```text
Running benchmark suite using: Golden Solutions
=====================================================================================
TASK ID    | CATEGORY     | RESULT   | SCORE  | TIME (ms)  | FEEDBACK
-------------------------------------------------------------------------------------
TASK-001   | bugfix       | PASS     | 1.00   | 58.2       | [Tier 3 PASSED] Hidden invar
TASK-002   | feature      | PASS     | 1.00   | 210.4      | [Tier 3 PASSED] Hidden invar
TASK-003   | refactor     | PASS     | 1.00   | 84.1       | [Tier 3 PASSED] Hidden invar
TASK-004   | performance  | PASS     | 1.00   | 142.3      | [Tier 4 PASSED] Solution sat
=====================================================================================
Summary: 4/4 passed (100.0%)
```

#### Verify a Custom Solution
```bash
python -m vericode verify --task TASK-001 --code-file solution.py
```

#### Start Remote Evaluation REST API
```bash
python -m vericode serve --port 8000
```

---

## 🤖 Using the RL Environment (`VericodeEnv`)

Train agents using the standard Gym agent-environment loop:

```python
from vericode.env.code_env import VericodeEnv

# Initialize environment for a specific benchmark task
env = VericodeEnv(task_id="TASK-001", max_steps=5, dense_rewards=True)
obs, info = env.reset()

print("Current Task:", obs["title"])
print("Buggy Code:\n", obs["current_code"][:200])

# Agent generates a candidate fix
candidate_patch = """# Your agent's proposed implementation"""

# Execute environment step
action = {
    "action_type": "replace_code",
    "code": candidate_patch,
}
obs, reward, terminated, truncated, info = env.step(action)

print(f"Step Reward: {reward}")
print(f"Passed: {info['overall_passed']}")
print(f"Verifier Feedback:\n{obs['last_feedback']}")
```

---

## 🌐 REST API Endpoints

When running `python -m vericode serve`, access the interactive OpenAPI documentation at `http://localhost:8000/docs`:

- `GET /health` - Service health status.
- `GET /api/v1/tasks` - List all available benchmark tasks.
- `GET /api/v1/tasks/{task_id}` - Fetch task prompt, target filename, and public tests.
- `POST /api/v1/verify` - Submit candidate code for deterministic multi-tier verification.
- `POST /api/v1/eval/batch` - Batch evaluate an agent across multiple benchmark tasks.

---

## 🧪 Running Tests

Vericode comes with a test suite verifying the verifiers, AST guards, sandbox timeouts, and task solutions:

```bash
pytest -v tests/
```

---

## 📊 Benchmark Baseline Results

| Benchmark Task | Unmodified Base Code | Golden Reference Solution |
|---|---|---|
| `TASK-001: Concurrent LRU Cache` | ❌ FAILED (KeyError under thread contention) | ✅ **100% PASS** (RLock synchronization) |
| `TASK-002: Token Bucket Rate Limiter` | ❌ FAILED (NotImplementedError) | ✅ **100% PASS** (Continuous time replenishment) |
| `TASK-003: Dependency Graph Sorter` | ❌ FAILED (RecursionError on deep chains) | ✅ **100% PASS** (Kahn's iterative BFS) |
| `TASK-004: Streaming NDJSON Parser` | ❌ FAILED (Exceeds latency budget) | ✅ **100% PASS** (Zero-copy stream generator) |

---

## 📜 License

Distributed under the Apache 2.0 License. See `LICENSE` for details.
