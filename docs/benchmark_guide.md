# Vericode Benchmark Suite Guide

This guide describes the core benchmark tasks included in Vericode, their learning objectives, and verification criteria.

## Tasks Overview

| Task ID | Title | Category | Difficulty | Verification Focus |
|---|---|---|---|---|
| `TASK-001` | Concurrent LRU Cache | Bug Fix | Medium | Multi-threaded locking, deadlock freedom, atomic eviction |
| `TASK-002` | Token Bucket Rate Limiter | Feature | Medium | Continuous time replenishment, burst quota, boundary handling |
| `TASK-003` | Dependency Graph Sorter | Refactor | Hard | Kahn's algorithm, recursion elimination, cycle extraction |
| `TASK-004` | Streaming NDJSON Log Parser | Performance | Medium | Memory zero-copy, generator streaming, latency budget (<180ms) |

---

### TASK-001: Thread-Safe Concurrent LRU Cache
- **Base Flaw**: Unsynchronized `OrderedDict` raises `KeyError` or `RuntimeError: OrderedDict mutated during iteration` under concurrent read/write stress.
- **Verification**: 8 worker threads performing 800 operations concurrently. Invariants checked: zero uncaught exceptions, strict capacity bounds (`size <= capacity`).

### TASK-002: Token Bucket Rate Limiter with Burst Control
- **Base Flaw**: Unimplemented stub raising `NotImplementedError`.
- **Verification**: Floating-point clock replenishment calculation, burst capacity consumption, rejection on insufficient tokens without deducting.

### TASK-003: Dependency Graph Sorter & Cycle Detection Refactor
- **Base Flaw**: Legacy recursive DFS crashes with `RecursionError` on deep graphs (>1000 nodes).
- **Verification**: 2,500-node linear chains to test recursion immunity; diamond DAG resolution; cycle detection raising `CycleDetectedError`.

### TASK-004: Zero-Copy Streaming NDJSON Log Parser
- **Base Flaw**: Regex string-splitting allocates redundant memory buffers and takes >250ms on large payloads.
- **Verification**: Parses 4,000 JSON lines in under 200ms with error resilience against corrupted lines.
