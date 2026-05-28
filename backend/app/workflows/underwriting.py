"""
Underwriting workflow - evaluates an application against all active lender programs.

Steps: validate -> derive -> fetch -> evaluate -> aggregate -> persist

Hatchet runs these as a DAG. If Hatchet is unavailable, _run_sync_fallback()
executes all steps in-process so local dev works without the full stack.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload


# --------------------------------------------------------------------------- #
# Step implementations (pure functions, called by both Hatchet and fallback)  #
# --------------------------------------------------------------------------- #

def _step_validate(application: Any) -> None:
    """Raise if the application is missing data required for underwriting."""
    if application.business is None:
        raise ValueError("Application has no business information")
    if application.loan_request is None:
        raise ValueError("Application has no loan request")


def _step_derive(application: Any) -> dict[str, Any]:
    """Compute derived fields not stored directly on the models."""
    lr = application.loan_request
    derived: dict[str, Any] = {}

    # Derive equipment age from year if age not explicitly set
    if lr.equipment_age_yrs is None and lr.equipment_year:
        current_year = datetime.now(timezone.utc).year
        derived["equipment_age_yrs"] = float(current_year - lr.equipment_year)

    # Fall back to business state when state_of_operation is not set
    if not lr.state_of_operation and application.business:
        derived["state_of_operation"] = application.business.state

    return derived


def _build_eval_context(application: Any, derived: dict[str, Any]) -> Any:
    """Assemble an EvalContext from the application ORM objects."""
    from app.engine.rules.base import EvalContext

    biz = application.business
    bc = application.business_credit
    lr = application.loan_request

    guarantors = [
        {
            "credit_score": g.credit_score,
            "ownership_pct": g.ownership_pct,
            "full_name": g.full_name,
        }
        for g in (application.guarantors or [])
    ]

    return EvalContext(
        guarantors=guarantors,
        business_name=biz.business_name if biz else "",
        business_type=biz.business_type if biz else "",
        state=biz.state if biz else "",
        years_in_biz=biz.years_in_biz if biz else 0.0,
        annual_revenue=biz.annual_revenue if biz else None,
        employee_count=biz.employee_count if biz else None,
        naics_code=biz.naics_code if biz else None,
        fico_sbss=bc.fico_sbss if bc else None,
        experian_intelliscore=bc.experian_intelliscore if bc else None,
        duns_paydex=bc.duns_paydex if bc else None,
        bankruptcies=bc.bankruptcies if bc else 0,
        liens=bc.liens if bc else 0,
        judgments=bc.judgments if bc else 0,
        requested_amount=lr.requested_amount if lr else 0.0,
        requested_term_mo=lr.requested_term_mo if lr else 0,
        equipment_type=lr.equipment_type if lr else "",
        equipment_age_yrs=derived.get("equipment_age_yrs", lr.equipment_age_yrs if lr else None),
        equipment_condition=lr.equipment_condition if lr else None,
        state_of_operation=derived.get(
            "state_of_operation", lr.state_of_operation if lr else None
        ),
        down_payment_pct=lr.down_payment_pct if lr else None,
    )


def _step_fetch_programs(session: Any) -> list[Any]:
    """Return all active programs with their active rules (sync helper)."""
    from app.models.lender import LenderProgram, EligibilityRule, Lender
    import asyncio

    async def _fetch():
        result = await session.execute(
            select(LenderProgram)
            .join(Lender)
            .where(LenderProgram.is_active == True, Lender.is_active == True)  # noqa: E712
            .options(
                selectinload(LenderProgram.rules),
                selectinload(LenderProgram.lender),
            )
        )
        return result.scalars().all()

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_fetch())


def _step_evaluate(programs: list[Any], ctx: Any) -> list[dict[str, Any]]:
    """Score each program and return a list of result dicts sorted by fit_score desc."""
    from app.engine.scorer import FitScorer

    scorer = FitScorer()
    results: list[dict[str, Any]] = []

    for program in programs:
        active_rules = [r for r in program.rules if r.is_active]
        rule_dicts = [
            {
                "id": str(r.id),
                "rule_type": r.rule_type,
                "label": r.label,
                "weight": r.weight,
                "parameters": r.parameters or {},
            }
            for r in active_rules
        ]

        score_result = scorer.score(ctx, rule_dicts)

        results.append(
            {
                "lender_id": str(program.lender_id),
                "lender_name": program.lender.name,
                "program_id": str(program.id),
                "program_name": program.name,
                "fit_score": score_result.fit_score,
                "passed_count": score_result.passed_count,
                "failed_count": score_result.failed_count,
                "skipped_count": score_result.skipped_count,
                "criteria": [
                    {
                        "rule_id": c.rule_id,
                        "rule_type": c.rule_type,
                        "rule_name": c.rule_name,
                        "weight": c.weight,
                        "passed": c.passed,
                        "reason": c.reason,
                        "actual_value": c.actual_value,
                        "skipped": c.skipped,
                    }
                    for c in score_result.criteria
                ],
            }
        )

    results.sort(key=lambda r: r["fit_score"], reverse=True)
    return results


async def _step_persist(
    session: Any,
    run_id: uuid.UUID,
    results: list[dict[str, Any]],
) -> None:
    """Write final status and CriteriaCheckResult rows to the database."""
    from app.models.underwriting import UnderwritingRun, CriteriaCheckResult

    run = await session.get(UnderwritingRun, run_id)
    if run is None:
        raise ValueError(f"UnderwritingRun {run_id} not found")

    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    run.results = results

    for program_result in results:
        for c in program_result["criteria"]:
            check = CriteriaCheckResult(
                id=uuid.uuid4(),
                run_id=run_id,
                rule_id=uuid.UUID(c["rule_id"]) if c.get("rule_id") else None,
                program_id=uuid.UUID(program_result["program_id"]),
                lender_id=uuid.UUID(program_result["lender_id"]),
                rule_type=c["rule_type"],
                rule_name=c["rule_name"],
                weight=c["weight"],
                passed=c["passed"],
                reason=c["reason"],
                actual_value=c.get("actual_value"),
            )
            session.add(check)

    await session.commit()


# --------------------------------------------------------------------------- #
# Sync fallback (no Hatchet required)                                         #
# --------------------------------------------------------------------------- #

async def _run_sync_fallback(run_id: uuid.UUID, session: Any) -> None:
    """Execute the full underwriting pipeline in-process without Hatchet."""
    from app.models.underwriting import UnderwritingRun
    from app.models.lender import LenderProgram, Lender
    from app.engine.scorer import FitScorer

    # Mark as running
    run = await session.get(UnderwritingRun, run_id)
    if run is None:
        raise ValueError(f"UnderwritingRun {run_id} not found")
    run.status = "running"
    run.started_at = datetime.now(timezone.utc)
    await session.commit()

    try:
        # Load application with all relationships
        from app.models.application import Application
        result = await session.execute(
            select(Application)
            .where(Application.id == run.application_id)
            .options(
                selectinload(Application.business),
                selectinload(Application.guarantors),
                selectinload(Application.business_credit),
                selectinload(Application.loan_request),
            )
        )
        application = result.scalar_one()

        # Steps
        _step_validate(application)
        derived = _step_derive(application)
        ctx = _build_eval_context(application, derived)

        # Fetch active programs
        prog_result = await session.execute(
            select(LenderProgram)
            .join(Lender)
            .where(LenderProgram.is_active == True, Lender.is_active == True)  # noqa: E712
            .options(
                selectinload(LenderProgram.rules),
                selectinload(LenderProgram.lender),
            )
        )
        programs = prog_result.scalars().all()

        scored_results = _step_evaluate(programs, ctx)
        await _step_persist(session, run_id, scored_results)

    except Exception as exc:
        run = await session.get(UnderwritingRun, run_id)
        if run:
            run.status = "failed"
            run.completed_at = datetime.now(timezone.utc)
            run.error_message = str(exc)
            await session.commit()
        raise


# --------------------------------------------------------------------------- #
# Hatchet workflow definition                                                  #
# --------------------------------------------------------------------------- #

def register_workflow() -> None:
    """Register the underwriting workflow with Hatchet. Called from the worker."""
    try:
        from app.workflows.hatchet_client import hatchet
        from hatchet_sdk import Context
    except Exception:
        return

    @hatchet.workflow(name="underwriting", on_events=["underwriting:run"])
    class UnderwritingWorkflow:

        @hatchet.step(name="validate")
        async def validate(self, context: Context) -> dict:
            from app.core.database import AsyncSessionLocal
            from app.models.application import Application
            payload = context.workflow_input()
            run_id = uuid.UUID(payload["run_id"])

            async with AsyncSessionLocal() as session:
                from app.models.underwriting import UnderwritingRun
                run = await session.get(UnderwritingRun, run_id)
                run.status = "running"
                run.started_at = datetime.now(timezone.utc)
                await session.commit()

                result = await session.execute(
                    select(Application)
                    .where(Application.id == run.application_id)
                    .options(
                        selectinload(Application.business),
                        selectinload(Application.loan_request),
                    )
                )
                application = result.scalar_one()
                _step_validate(application)

            return {"run_id": str(run_id), "application_id": str(run.application_id)}

        @hatchet.step(name="derive", parents=["validate"])
        async def derive(self, context: Context) -> dict:
            from app.core.database import AsyncSessionLocal
            from app.models.application import Application
            payload = context.step_output("validate")
            application_id = uuid.UUID(payload["application_id"])

            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Application)
                    .where(Application.id == application_id)
                    .options(
                        selectinload(Application.business),
                        selectinload(Application.guarantors),
                        selectinload(Application.business_credit),
                        selectinload(Application.loan_request),
                    )
                )
                application = result.scalar_one()
                derived = _step_derive(application)

            return {**payload, "derived": derived}

        @hatchet.step(name="fetch", parents=["derive"])
        async def fetch(self, context: Context) -> dict:
            from app.core.database import AsyncSessionLocal
            from app.models.lender import LenderProgram, Lender
            payload = context.step_output("derive")

            async with AsyncSessionLocal() as session:
                prog_result = await session.execute(
                    select(LenderProgram)
                    .join(Lender)
                    .where(
                        LenderProgram.is_active == True,  # noqa: E712
                        Lender.is_active == True,         # noqa: E712
                    )
                    .options(
                        selectinload(LenderProgram.rules),
                        selectinload(LenderProgram.lender),
                    )
                )
                programs = prog_result.scalars().all()
                programs_data = [
                    {
                        "id": str(p.id),
                        "lender_id": str(p.lender_id),
                        "lender_name": p.lender.name,
                        "name": p.name,
                        "rules": [
                            {
                                "id": str(r.id),
                                "rule_type": r.rule_type,
                                "label": r.label,
                                "weight": r.weight,
                                "parameters": r.parameters or {},
                            }
                            for r in p.rules
                            if r.is_active
                        ],
                    }
                    for p in programs
                ]

            return {**payload, "programs": programs_data}

        @hatchet.step(name="evaluate", parents=["fetch"])
        async def evaluate(self, context: Context) -> dict:
            from app.core.database import AsyncSessionLocal
            from app.models.application import Application
            from app.engine.scorer import FitScorer
            payload = context.step_output("fetch")
            application_id = uuid.UUID(payload["application_id"])
            derived = payload.get("derived", {})

            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Application)
                    .where(Application.id == application_id)
                    .options(
                        selectinload(Application.business),
                        selectinload(Application.guarantors),
                        selectinload(Application.business_credit),
                        selectinload(Application.loan_request),
                    )
                )
                application = result.scalar_one()

            ctx = _build_eval_context(application, derived)
            scorer = FitScorer()
            results: list[dict] = []

            for p in payload["programs"]:
                score_result = scorer.score(ctx, p["rules"])
                results.append(
                    {
                        "lender_id": p["lender_id"],
                        "lender_name": p["lender_name"],
                        "program_id": p["id"],
                        "program_name": p["name"],
                        "fit_score": score_result.fit_score,
                        "passed_count": score_result.passed_count,
                        "failed_count": score_result.failed_count,
                        "skipped_count": score_result.skipped_count,
                        "criteria": [
                            {
                                "rule_id": c.rule_id,
                                "rule_type": c.rule_type,
                                "rule_name": c.rule_name,
                                "weight": c.weight,
                                "passed": c.passed,
                                "reason": c.reason,
                                "actual_value": c.actual_value,
                                "skipped": c.skipped,
                            }
                            for c in score_result.criteria
                        ],
                    }
                )

            results.sort(key=lambda r: r["fit_score"], reverse=True)
            return {**payload, "results": results}

        @hatchet.step(name="persist", parents=["evaluate"])
        async def persist(self, context: Context) -> dict:
            from app.core.database import AsyncSessionLocal
            payload = context.step_output("evaluate")
            run_id = uuid.UUID(payload["run_id"])

            async with AsyncSessionLocal() as session:
                await _step_persist(session, run_id, payload["results"])

            return {"run_id": str(run_id), "status": "completed"}

    return UnderwritingWorkflow
