"""Shared fixtures for rule evaluator tests."""
import pytest
from app.engine.rules.base import EvalContext
from app.engine.rules.registry import RuleEvaluatorRegistry

# Ensure all evaluators are registered before any test runs
RuleEvaluatorRegistry.ensure_loaded()


def make_ctx(**overrides) -> EvalContext:
    """Build a fully-populated EvalContext with sensible defaults."""
    defaults = dict(
        guarantors=[{"credit_score": 720, "ownership_pct": 100.0, "full_name": "Jane Smith"}],
        business_name="Acme Construction LLC",
        business_type="llc",
        state="TX",
        years_in_biz=5.0,
        annual_revenue=500_000.0,
        employee_count=12,
        naics_code="238910",
        fico_sbss=160,
        experian_intelliscore=75,
        duns_paydex=80,
        bankruptcies=0,
        liens=0,
        judgments=0,
        requested_amount=150_000.0,
        requested_term_mo=60,
        equipment_type="construction",
        equipment_age_yrs=3.0,
        equipment_condition="used",
        state_of_operation="TX",
        down_payment_pct=10.0,
    )
    defaults.update(overrides)
    return EvalContext(**defaults)
