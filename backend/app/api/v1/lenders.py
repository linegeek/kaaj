from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.lender import EligibilityRule, Lender, LenderProgram
from app.schemas.lender import (
    LenderCreate, LenderDetail, LenderResponse, LenderUpdate,
    ProgramCreate, ProgramDetail, ProgramResponse, ProgramUpdate,
    RuleCreate, RuleResponse, RuleUpdate,
)

router = APIRouter(prefix="/lenders", tags=["lenders"])


# ---- Lenders ----------------------------------------------------------------

@router.get("", response_model=list[LenderResponse])
async def list_lenders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Lender).order_by(Lender.name))
    return result.scalars().all()


@router.post("", response_model=LenderResponse, status_code=status.HTTP_201_CREATED)
async def create_lender(body: LenderCreate, db: AsyncSession = Depends(get_db)):
    lender = Lender(**body.model_dump())
    db.add(lender)
    await db.flush()
    await db.refresh(lender)
    return lender


@router.get("/{lender_id}", response_model=LenderDetail)
async def get_lender(lender_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Lender)
        .where(Lender.id == lender_id)
        .options(selectinload(Lender.programs))
    )
    lender = result.scalar_one_or_none()
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    return lender


@router.put("/{lender_id}", response_model=LenderResponse)
async def update_lender(
    lender_id: uuid.UUID, body: LenderUpdate, db: AsyncSession = Depends(get_db)
):
    lender = await db.get(Lender, lender_id)
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(lender, field, value)
    await db.flush()
    await db.refresh(lender)
    return lender


@router.delete("/{lender_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lender(lender_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lender = await db.get(Lender, lender_id)
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    await db.delete(lender)


# ---- Programs ---------------------------------------------------------------

@router.get("/{lender_id}/programs", response_model=list[ProgramResponse])
async def list_programs(lender_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LenderProgram)
        .where(LenderProgram.lender_id == lender_id)
        .order_by(LenderProgram.name)
    )
    return result.scalars().all()


@router.post(
    "/{lender_id}/programs",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program(
    lender_id: uuid.UUID, body: ProgramCreate, db: AsyncSession = Depends(get_db)
):
    lender = await db.get(Lender, lender_id)
    if not lender:
        raise HTTPException(status_code=404, detail="Lender not found")
    program = LenderProgram(lender_id=lender_id, **body.model_dump())
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return program


@router.get("/{lender_id}/programs/{program_id}", response_model=ProgramDetail)
async def get_program(
    lender_id: uuid.UUID, program_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LenderProgram)
        .where(LenderProgram.id == program_id, LenderProgram.lender_id == lender_id)
        .options(selectinload(LenderProgram.rules))
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


@router.put("/{lender_id}/programs/{program_id}", response_model=ProgramResponse)
async def update_program(
    lender_id: uuid.UUID,
    program_id: uuid.UUID,
    body: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LenderProgram).where(
            LenderProgram.id == program_id, LenderProgram.lender_id == lender_id
        )
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(program, field, value)
    await db.flush()
    await db.refresh(program)
    return program


@router.delete(
    "/{lender_id}/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_program(
    lender_id: uuid.UUID, program_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LenderProgram).where(
            LenderProgram.id == program_id, LenderProgram.lender_id == lender_id
        )
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    await db.delete(program)


# ---- Rules ------------------------------------------------------------------

@router.get(
    "/{lender_id}/programs/{program_id}/rules", response_model=list[RuleResponse]
)
async def list_rules(
    lender_id: uuid.UUID, program_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(EligibilityRule)
        .join(LenderProgram)
        .where(
            EligibilityRule.program_id == program_id,
            LenderProgram.lender_id == lender_id,
        )
        .order_by(EligibilityRule.rule_type)
    )
    return result.scalars().all()


@router.post(
    "/{lender_id}/programs/{program_id}/rules",
    response_model=RuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rule(
    lender_id: uuid.UUID,
    program_id: uuid.UUID,
    body: RuleCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LenderProgram).where(
            LenderProgram.id == program_id, LenderProgram.lender_id == lender_id
        )
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    rule = EligibilityRule(program_id=program_id, **body.model_dump())
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return rule


@router.put(
    "/{lender_id}/programs/{program_id}/rules/{rule_id}",
    response_model=RuleResponse,
)
async def update_rule(
    lender_id: uuid.UUID,
    program_id: uuid.UUID,
    rule_id: uuid.UUID,
    body: RuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EligibilityRule)
        .join(LenderProgram)
        .where(
            EligibilityRule.id == rule_id,
            EligibilityRule.program_id == program_id,
            LenderProgram.lender_id == lender_id,
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(rule, field, value)
    await db.flush()
    await db.refresh(rule)
    return rule


@router.delete(
    "/{lender_id}/programs/{program_id}/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rule(
    lender_id: uuid.UUID,
    program_id: uuid.UUID,
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EligibilityRule)
        .join(LenderProgram)
        .where(
            EligibilityRule.id == rule_id,
            EligibilityRule.program_id == program_id,
            LenderProgram.lender_id == lender_id,
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
