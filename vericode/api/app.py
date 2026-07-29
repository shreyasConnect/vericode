"""
FastAPI application for the Vericode benchmark and evaluation service.
"""

from typing import List
from fastapi import FastAPI, HTTPException
from vericode.api.schemas import (
    BatchEvalRequest,
    BatchEvalResponse,
    TaskDetailResponse,
    TaskSummaryResponse,
    TierResultSchema,
    VerifyRequest,
    VerifyResponse,
)
from vericode.tasks.registry import GLOBAL_REGISTRY
from vericode.verifier.deterministic import MultiTierVerifier

app = FastAPI(
    title="Vericode Benchmark API",
    description="Deterministic Evaluation & Verifier API for Reinforcement Learning Code Agents",
    version="1.0.0",
)

verifier = MultiTierVerifier()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "vericode-api", "version": "1.0.0"}


@app.get("/api/v1/tasks", response_model=List[TaskSummaryResponse])
def get_all_tasks():
    tasks = GLOBAL_REGISTRY.list_all()
    return [
        TaskSummaryResponse(
            task_id=t.task_id,
            title=t.title,
            category=t.category,
            difficulty=t.difficulty,
            description=t.description,
            target_filename=t.target_filename,
            tags=t.tags,
        )
        for t in tasks
    ]


@app.get("/api/v1/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task_by_id(task_id: str):
    task = GLOBAL_REGISTRY.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return TaskDetailResponse(
        task_id=task.task_id,
        title=task.title,
        category=task.category,
        difficulty=task.difficulty,
        description=task.description,
        target_filename=task.target_filename,
        tags=task.tags,
        base_code=task.base_code,
        public_tests=task.public_tests,
    )


@app.post("/api/v1/verify", response_model=VerifyResponse)
def verify_submission(req: VerifyRequest):
    task = GLOBAL_REGISTRY.get(req.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{req.task_id}' not found")

    report = verifier.verify(task, req.code)
    return VerifyResponse(
        task_id=report.task_id,
        overall_passed=report.overall_passed,
        score=report.score,
        total_duration_ms=report.total_duration_ms,
        feedback=report.feedback,
        tiers=[
            TierResultSchema(
                tier=tr.tier.value,
                passed=tr.passed,
                message=tr.message,
                duration_ms=tr.duration_ms,
            )
            for tr in report.tier_results
        ],
    )


@app.post("/api/v1/eval/batch", response_model=BatchEvalResponse)
def batch_evaluate(req: BatchEvalRequest):
    results = {}
    passed_count = 0

    for task_id, code in req.submissions.items():
        task = GLOBAL_REGISTRY.get(task_id)
        if not task:
            continue
        report = verifier.verify(task, code)
        if report.overall_passed:
            passed_count += 1
        results[task_id] = VerifyResponse(
            task_id=report.task_id,
            overall_passed=report.overall_passed,
            score=report.score,
            total_duration_ms=report.total_duration_ms,
            feedback=report.feedback,
            tiers=[
                TierResultSchema(
                    tier=tr.tier.value,
                    passed=tr.passed,
                    message=tr.message,
                    duration_ms=tr.duration_ms,
                )
                for tr in report.tier_results
            ],
        )

    total = len(req.submissions)
    pass_rate = (passed_count / total) * 100.0 if total > 0 else 0.0

    return BatchEvalResponse(
        total_tasks=total,
        passed_tasks=passed_count,
        pass_rate=pass_rate,
        results=results,
    )
