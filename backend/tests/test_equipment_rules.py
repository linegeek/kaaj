"""Tests for the 7 equipment rule evaluators."""
from app.engine.rules.base import RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry
from tests.conftest import make_ctx


def ev(rule_type: RuleType):
    return RuleEvaluatorRegistry.get(rule_type)


class TestAllowedEquipmentTypes:
    e = ev(RuleType.ALLOWED_EQUIPMENT_TYPES)

    def test_pass_when_type_in_list(self):
        ctx = make_ctx(equipment_type="construction")
        assert self.e.evaluate(ctx, {"types": ["construction", "heavy_equipment"]}).passed is True

    def test_fail_when_type_not_in_list(self):
        ctx = make_ctx(equipment_type="restaurant")
        result = self.e.evaluate(ctx, {"types": ["construction", "heavy_equipment"]})
        assert result.passed is False
        assert result.actual_value == "restaurant"

    def test_case_insensitive(self):
        ctx = make_ctx(equipment_type="CONSTRUCTION")
        assert self.e.evaluate(ctx, {"types": ["construction"]}).passed is True

    def test_skip_when_no_types_configured(self):
        assert self.e.evaluate(make_ctx(), {"types": []}).skipped is True


class TestMaxEquipmentAge:
    e = ev(RuleType.MAX_EQUIPMENT_AGE_YRS)

    def test_pass_within_limit(self):
        assert self.e.evaluate(make_ctx(equipment_age_yrs=3.0), {"max_age_yrs": 10.0}).passed is True

    def test_pass_at_limit(self):
        assert self.e.evaluate(make_ctx(equipment_age_yrs=10.0), {"max_age_yrs": 10.0}).passed is True

    def test_fail_over_limit(self):
        result = self.e.evaluate(make_ctx(equipment_age_yrs=12.0), {"max_age_yrs": 10.0})
        assert result.passed is False
        assert result.actual_value == "12.0"

    def test_skip_when_age_not_provided(self):
        assert self.e.evaluate(make_ctx(equipment_age_yrs=None), {"max_age_yrs": 10.0}).skipped is True


class TestMinLoanAmount:
    e = ev(RuleType.MIN_LOAN_AMOUNT)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(requested_amount=150_000), {"min_amount": 25_000}).passed is True

    def test_fail(self):
        result = self.e.evaluate(make_ctx(requested_amount=5_000), {"min_amount": 25_000})
        assert result.passed is False

    def test_pass_at_exact_minimum(self):
        assert self.e.evaluate(make_ctx(requested_amount=25_000), {"min_amount": 25_000}).passed is True


class TestMaxLoanAmount:
    e = ev(RuleType.MAX_LOAN_AMOUNT)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(requested_amount=100_000), {"max_amount": 500_000}).passed is True

    def test_fail(self):
        result = self.e.evaluate(make_ctx(requested_amount=750_000), {"max_amount": 500_000})
        assert result.passed is False

    def test_pass_at_exact_maximum(self):
        assert self.e.evaluate(make_ctx(requested_amount=500_000), {"max_amount": 500_000}).passed is True


class TestMaxTermMonths:
    e = ev(RuleType.MAX_TERM_MONTHS)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(requested_term_mo=60), {"max_months": 84}).passed is True

    def test_fail(self):
        result = self.e.evaluate(make_ctx(requested_term_mo=96), {"max_months": 84})
        assert result.passed is False
        assert result.actual_value == "96"

    def test_pass_at_limit(self):
        assert self.e.evaluate(make_ctx(requested_term_mo=84), {"max_months": 84}).passed is True


class TestMinDownPaymentPct:
    e = ev(RuleType.MIN_DOWN_PAYMENT_PCT)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(down_payment_pct=20.0), {"min_pct": 10.0}).passed is True

    def test_fail(self):
        result = self.e.evaluate(make_ctx(down_payment_pct=5.0), {"min_pct": 10.0})
        assert result.passed is False

    def test_skip_when_not_provided(self):
        assert self.e.evaluate(make_ctx(down_payment_pct=None), {"min_pct": 10.0}).skipped is True


class TestAllowedEquipmentConditions:
    e = ev(RuleType.ALLOWED_EQUIPMENT_CONDITIONS)

    def test_pass_when_condition_allowed(self):
        ctx = make_ctx(equipment_condition="used")
        assert self.e.evaluate(ctx, {"conditions": ["new", "used"]}).passed is True

    def test_fail_when_condition_not_allowed(self):
        ctx = make_ctx(equipment_condition="refurbished")
        result = self.e.evaluate(ctx, {"conditions": ["new", "used"]})
        assert result.passed is False

    def test_case_insensitive(self):
        ctx = make_ctx(equipment_condition="USED")
        assert self.e.evaluate(ctx, {"conditions": ["used"]}).passed is True

    def test_skip_when_condition_not_provided(self):
        ctx = make_ctx(equipment_condition=None)
        assert self.e.evaluate(ctx, {"conditions": ["new"]}).skipped is True

    def test_skip_when_no_conditions_configured(self):
        assert self.e.evaluate(make_ctx(), {"conditions": []}).skipped is True
