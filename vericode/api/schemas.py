"""
Pydantic schemas for the Vericode REST API.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskSummaryResponse(BaseModel):
    task_id: str
    title: str
    category: str
    difficulty: str
    description: str
    target_filename: str
    tags: List[str]


class TaskDetailResponse(TaskSummaryResponse):
    base_code: str
    public_tests: str


class VerifyRequest(BaseModel):
    task_id: str
    code: str


class TierResultSchema(BaseModel):
    tier: str
    passed: bool
    message: str
    duration_ms: float


class VerifyResponse(BaseModel):
    task_id: str
    overall_passed: bool
    score: float
    total_duration_ms: float
    feedback: str
    tiers: List[TierResultSchema]


class BatchEvalRequest(BaseModel):
    submissions: Dict[str, str] = Field(..., description="Map of task_id to code implementation")


class BatchEvalResponse(BaseModel):
    total_tasks: int
    passed_tasks: int
    pass_rate: float
    results: Dict[str, VerifyResponse]
