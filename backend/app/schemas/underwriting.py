from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class CriteriaCheckResponse(BaseModel):
    rule_type: str
    rule_name: str
    weight: float
    passed: bool
    reason: str | None = None
    actual_value: str | None = None
    skipped: bool = False


class ProgramResultResponse(BaseModel):
    lender_id: uuid.UUID
    lender_name: str
    program_id: uuid.UUID
    program_name: str
    fit_score: float
    passed_count: int
    failed_count: int
    skipped_count: int
    criteria: list[CriteriaCheckResponse] = []


class UnderwritingRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    results: list[Any] | None = None
    created_at: datetime


class TriggerRequest(BaseModel):
    application_id: uuid.UUID
