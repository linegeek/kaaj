from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class RuleBase(BaseModel):
    rule_type: str
    label: str | None = None
    weight: float = 1.0
    parameters: dict[str, Any] = {}
    is_active: bool = True


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    label: str | None = None
    weight: float | None = None
    parameters: dict[str, Any] | None = None
    is_active: bool | None = None


class RuleResponse(RuleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    program_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProgramBase(BaseModel):
    name: str
    description: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    is_active: bool = True


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    is_active: bool | None = None


class ProgramResponse(ProgramBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    lender_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProgramDetail(ProgramResponse):
    rules: list[RuleResponse] = []


class LenderBase(BaseModel):
    name: str
    contact_email: str | None = None
    contact_phone: str | None = None
    notes: str | None = None
    is_active: bool = True


class LenderCreate(LenderBase):
    pass


class LenderUpdate(BaseModel):
    name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class LenderResponse(LenderBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LenderDetail(LenderResponse):
    programs: list[ProgramResponse] = []
