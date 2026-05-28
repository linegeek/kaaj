from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.application import Application
from app.models.underwriting import UnderwritingRun
from app.schemas.underwriting import TriggerRequest, UnderwritingRunResponse

router = APIRouter(prefix="/underwriting", tags=["underwriting"])


@router.post("/run", response_model=UnderwritingRunResponse, status_code=201)
async def trigger_underwriting(body: TriggerRequest, db: AsyncSession = Depends(get_db)):
    app = await db.get(Application, body.application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    run = UnderwritingRun(application_id=body.application_id)
    db.add(run)
    await db.flush()
    await db.refresh(run)

    # Update application status
    app.status = "underwriting"

    # Try Hatchet first; fall back to in-process execution
    try:
        from app.workflows.hatchet_client import hatchet
        await hatchet.admin.run_workflow(
            "underwriting",
            {"run_id": str(run.id)},
        )
    except Exception:
        # Hatchet unavailable - run synchronously in background task
        import asyncio
        from app.workflows.underwriting import _run_sync_fallback
        from app.core.database import AsyncSessionLocal

        async def _run_in_background():
            async with AsyncSessionLocal() as bg_session:
                await _run_sync_fallback(run.id, bg_session)

        asyncio.create_task(_run_in_background())

    return run


@router.get("/runs/{run_id}", response_model=UnderwritingRunResponse)
async def get_run(run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    run = await db.get(UnderwritingRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Underwriting run not found")
    return run
