from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BusinessCreate(BaseModel):
    business_name: str
    dba_name: str | None = None
    owner_name: str
    owner_email: str
    owner_phone: str | None = None
    state: str
    business_type: str
    years_in_biz: float
    naics_code: str | None = None
    annual_revenue: float | None = None
    employee_count: int | None = None


class BusinessResponse(BusinessCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID


class GuarantorCreate(BaseModel):
    full_name: str
    ssn_last4: str | None = None
    credit_score: int | None = None
    ownership_pct: float | None = None


class GuarantorResponse(GuarantorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID


class BusinessCreditCreate(BaseModel):
    fico_sbss: int | None = None
    experian_intelliscore: int | None = None
    duns_paydex: int | None = None
    bankruptcies: int = 0
    liens: int = 0
    judgments: int = 0
    years_in_file: float | None = None


class BusinessCreditResponse(BusinessCreditCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID


class LoanRequestCreate(BaseModel):
    requested_amount: float
    requested_term_mo: int
    equipment_type: str
    equipment_description: str | None = None
    equipment_year: int | None = None
    equipment_condition: str | None = None
    state_of_operation: str | None = None
    down_payment_pct: float | None = None


class LoanRequestResponse(LoanRequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    application_id: uuid.UUID
    equipment_age_yrs: float | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    business: BusinessResponse | None = None
    guarantors: list[GuarantorResponse] = []
    business_credit: BusinessCreditResponse | None = None
    loan_request: LoanRequestResponse | None = None


class ApplicationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime
    business_name: str | None = None
    owner_name: str | None = None
    requested_amount: float | None = None
    equipment_type: str | None = None
