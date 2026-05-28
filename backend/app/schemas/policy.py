from __future__ import annotations
import uuid
from typing import Any
from pydantic import BaseModel


class ParsedRulePreview(BaseModel):
    rule_type: str
    label: str | None = None
    weight: float = 1.0
    parameters: dict[str, Any] = {}


class ParsedProgramPreview(BaseModel):
    name: str
    description: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    rules: list[ParsedRulePreview] = []


class ParsedLenderPreview(BaseModel):
    lender_name: str
    notes: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    programs: list[ParsedProgramPreview] = []


class PolicyImportRequest(BaseModel):
    lender_id: uuid.UUID
    preview: ParsedLenderPreview
