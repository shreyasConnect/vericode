# Vericode Architecture & Verification Pipeline

Vericode is a deterministic evaluation harness and Reinforcement Learning environment designed for evaluating code-generation and bug-fixing AI models.

## High-Level Architecture

```mermaid
flowchart TD
    subgraph Agent [AI Agent / Model]
        A1[LLM / Policy Network]
        A2[Unified Diff / Code Patch]
    end

    subgraph VericodeCore [Vericode Framework]
        E[VericodeEnv / Gym Interface]
        R[TaskRegistry]
        V[MultiTierVerifier]
        S[SandboxExecutor]
    end

    subgraph Tiers [Multi-Tier Deterministic Verifier]
        T1["Tier 1: AST Safety & Anti-Tamper Guard"]
        T2["Tier 2: Public Specification Tests"]
        T3["Tier 3: Hidden Deterministic Invariants"]
        T4["Tier 4: Performance / Latency Budget"]
    end

    subgraph Execution [Isolated Ephemeral Execution]
        SB["Ephemeral Workspace / Subprocess Isolation"]
        ST["Standard Output & Error Capture"]
        TM["Resource & Timeout Enforcer"]
    end

    A1 -->|Generates Patch| A2
    A2 -->|Action Step| E
    E -->|Lookup Task Spec| R
    E -->|Dispatch Verification| V
    V --> T1
    T1 -->|Pass| T2
    T2 -->|Pass| T3
    T3 -->|Pass| T4
    T2 & T3 & T4 -->|Execute In Sandbox| S
    S --> SB
    SB --> ST
    SB --> TM
    V -->|MultiTierReport & Dense Rewards| E
    E -->|Observation + Reward| A1
```

## Multi-Tier Verification Philosophy

1. **Tier 1 (AST Safety & Anti-Cheating)**:
   - In AI evaluation, models frequently discover cheat vectors (e.g. importing `unittest.mock.patch`, modifying `sys.modules`, altering globals, or calling `eval`/`exec`).
   - Vericode strictly parses the AST of the proposed code and blocks dynamic code injection and prohibited libraries before any execution occurs.

2. **Tier 2 (Public Specification Tests)**:
   - Evaluates whether the proposed code meets the user-facing contract.

3. **Tier 3 (Hidden Deterministic Invariants & Property Tests)**:
   - Code that merely overfits public tests is caught here.
   - Uses deterministic seeds (`seed=42`) with high concurrency stress testing, edge cases, boundary conditions, and deep structural recursions.

4. **Tier 4 (Performance & Latency Budget)**:
   - For optimization and refactoring tasks, asymptotic speedup must be statistically validated across warmup and measurement iterations.
