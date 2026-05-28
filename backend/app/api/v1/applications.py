from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.application import (
    Application, Business, BusinessCredit, LoanRequest, PersonalGuarantor,
)
from app.schemas.application import (
    ApplicationResponse, ApplicationSummary, BusinessCreate, BusinessCreditCreate,
    GuarantorCreate, GuarantorResponse, LoanRequestCreate,
    BusinessCreditResponse, LoanRequestResponse,
)

router = APIRouter(prefix="/applications", tags=["applications"])


async def _get_full_application(app_id: uuid.UUID, db: AsyncSession) -> Application:
    result = await db.execute(
        select(Application)
        .where(Application.id == app_id)
        .options(
            selectinload(Application.business),
            selectinload(Application.guarantors),
            selectinload(Application.business_credit),
            selectinload(Application.loan_request),
        )
    )
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _derive_equipment_age(loan_request: LoanRequest) -> None:
    if loan_request.equipment_age_yrs is None and loan_request.equipment_year:
        current_year = datetime.now(timezone.utc).year
        loan_request.equipment_age_yrs = float(current_year - loan_request.equipment_year)


@router.get("", response_model=list[ApplicationSummary])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Application)
        .options(
            selectinload(Application.business),
            selectinload(Application.loan_request),
        )
        .order_by(Application.created_at.desc())
    )
    applications = result.scalars().all()

    summaries = []
    for app in applications:
        summaries.append(ApplicationSummary(
            id=app.id,
            status=app.status,
            created_at=app.created_at,
            updated_at=app.updated_at,
            business_name=app.business.business_name if app.business else None,
            owner_name=app.business.owner_name if app.business else None,
            requested_amount=app.loan_request.requested_amount if app.loan_request else None,
            equipment_type=app.loan_request.equipment_type if app.loan_request else None,
        ))
    return summaries


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(body: BusinessCreate, db: AsyncSession = Depends(get_db)):
    app = Application()
    db.add(app)
    await db.flush()

    business = Business(application_id=app.id, **body.model_dump())
    db.add(business)
    await db.flush()

    return await _get_full_application(app.id, db)


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_full_application(app_id, db)


@router.post(
    "/{app_id}/guarantors",
    response_model=GuarantorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_guarantor(
    app_id: uuid.UUID, body: GuarantorCreate, db: AsyncSession = Depends(get_db)
):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    guarantor = PersonalGuarantor(application_id=app_id, **body.model_dump())
    db.add(guarantor)
    await db.flush()
    await db.refresh(guarantor)
    return guarantor


@router.put("/{app_id}/business-credit", response_model=BusinessCreditResponse)
async def upsert_business_credit(
    app_id: uuid.UUID, body: BusinessCreditCreate, db: AsyncSession = Depends(get_db)
):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db.execute(
        select(BusinessCredit).where(BusinessCredit.application_id == app_id)
    )
    bc = result.scalar_one_or_none()

    if bc:
        for field, value in body.model_dump().items():
            setattr(bc, field, value)
    else:
        bc = BusinessCredit(application_id=app_id, **body.model_dump())
        db.add(bc)

    await db.flush()
    await db.refresh(bc)
    return bc


@router.put("/{app_id}/loan-request", response_model=LoanRequestResponse)
async def upsert_loan_request(
    app_id: uuid.UUID, body: LoanRequestCreate, db: AsyncSession = Depends(get_db)
):
    app = await db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    result = await db.execute(
        select(LoanRequest).where(LoanRequest.application_id == app_id)
    )
    lr = result.scalar_one_or_none()

    if lr:
        for field, value in body.model_dump().items():
            setattr(lr, field, value)
        _derive_equipment_age(lr)
    else:
        lr = LoanRequest(application_id=app_id, **body.model_dump())
        _derive_equipment_age(lr)
        db.add(lr)

    await db.flush()
    await db.refresh(lr)
    return lr
