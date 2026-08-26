"""
Vericode Command-Line Interface.
"""

import argparse
import json
import sys
from typing import Optional
from vericode.tasks.registry import GLOBAL_REGISTRY
from vericode.verifier.deterministic import MultiTierVerifier


def cmd_list(args):
    tasks = GLOBAL_REGISTRY.list_all()
    print("\n" + "=" * 80)
    print(f"{'TASK ID':<12} | {'CATEGORY':<12} | {'DIFFICULTY':<10} | {'TITLE'}")
    print("-" * 80)
    for t in tasks:
        print(f"{t.task_id:<12} | {t.category:<12} | {t.difficulty:<10} | {t.title}")
    print("=" * 80 + "\n")


def cmd_show(args):
    task = GLOBAL_REGISTRY.get(args.task_id)
    if not task:
        print(f"Error: Task '{args.task_id}' not found.")
        sys.exit(1)

    print("\n" + "=" * 80)
    print(f"Task: {task.task_id} - {task.title}")
    print(f"Category: {task.category} | Difficulty: {task.difficulty}")
    print(f"Target File: {task.target_filename}")
    print("-" * 80)
    print(task.description)
    print("=" * 80 + "\n")


def cmd_verify(args):
    task = GLOBAL_REGISTRY.get(args.task_id)
    if not task:
        print(f"Error: Task '{args.task_id}' not found.")
        sys.exit(1)

    with open(args.code_file, "r", encoding="utf-8") as f:
        candidate_code = f.read()

    verifier = MultiTierVerifier()
    print(f"\nRunning deterministic multi-tier verifier on {task.task_id}...")
    report = verifier.verify(task, candidate_code)

    status_str = "PASSED" if report.overall_passed else "FAILED"
    print(f"\nResult: {status_str} (Score: {report.score:.2f})")
    print(f"Total Duration: {report.total_duration_ms:.2f} ms\n")
    print("Tier Breakdown:")
    for tr in report.tier_results:
        mark = "✓" if tr.passed else "✗"
        print(f"  [{mark}] {tr.tier.value:<18} ({tr.duration_ms:.1f}ms): {tr.message}")

    print("\nFeedback:\n" + report.feedback + "\n")
    if not report.overall_passed:
        sys.exit(1)


def cmd_bench(args):
    verifier = MultiTierVerifier()
    tasks = GLOBAL_REGISTRY.list_all()
    mode = "Golden Solutions" if args.golden else "Base Code"
    print(f"\nRunning benchmark suite using: {mode}")
    print("=" * 85)
    print(f"{'TASK ID':<10} | {'CATEGORY':<12} | {'RESULT':<8} | {'SCORE':<6} | {'TIME (ms)':<10} | {'FEEDBACK'}")
    print("-" * 85)

    passed_count = 0
    for task in tasks:
        code = task.golden_solution if args.golden else task.base_code
        report = verifier.verify(task, code)
        if report.overall_passed:
            passed_count += 1
        res_str = "PASS" if report.overall_passed else "FAIL"
        first_line = report.feedback.splitlines()[-1] if report.feedback else ""
        print(f"{task.task_id:<10} | {task.category:<12} | {res_str:<8} | {report.score:<6.2f} | {report.total_duration_ms:<10.1f} | {first_line[:30]}")

    print("=" * 85)
    print(f"Summary: {passed_count}/{len(tasks)} passed ({passed_count/len(tasks)*100.0:.1f}%)\n")


def cmd_serve(args):
    import uvicorn
    print(f"Starting Vericode Evaluation API server on port {args.port}...")
    uvicorn.run("vericode.api.app:app", host="0.0.0.0", port=args.port, reload=args.reload)


def main():
    parser = argparse.ArgumentParser(description="Vericode RL Benchmark & Deterministic Verifier CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = subparsers.add_parser("list", help="List all benchmark tasks")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = subparsers.add_parser("show", help="Show task details")
    p_show.add_argument("task_id", help="Task ID (e.g. TASK-001)")
    p_show.set_defaults(func=cmd_show)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify a code submission against a task")
    p_verify.add_argument("--task", dest="task_id", required=True, help="Task ID")
    p_verify.add_argument("--code-file", required=True, help="Path to code file")
    p_verify.set_defaults(func=cmd_verify)

    # bench
    p_bench = subparsers.add_parser("bench", help="Run benchmark suite")
    p_bench.add_argument("--golden", action="store_true", help="Evaluate golden solutions")
    p_bench.add_argument("--base", action="store_true", help="Evaluate baseline skeleton solutions")
    p_bench.set_defaults(func=cmd_bench)

    # serve
    p_serve = subparsers.add_parser("serve", help="Run FastAPI evaluation service")
    p_serve.add_argument("--port", type=int, default=8000, help="Port to listen on")
    p_serve.add_argument("--reload", action="store_true", help="Enable auto-reload")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
