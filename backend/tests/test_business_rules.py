"""Tests for the 7 business rule evaluators."""
from app.engine.rules.base import RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry
from tests.conftest import make_ctx


def ev(rule_type: RuleType):
    return RuleEvaluatorRegistry.get(rule_type)


class TestMinYearsInBusiness:
    e = ev(RuleType.MIN_YEARS_IN_BUSINESS)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(years_in_biz=5.0), {"min_years": 2.0}).passed is True

    def test_pass_at_exact_minimum(self):
        assert self.e.evaluate(make_ctx(years_in_biz=2.0), {"min_years": 2.0}).passed is True

    def test_fail_below_minimum(self):
        result = self.e.evaluate(make_ctx(years_in_biz=1.5), {"min_years": 2.0})
        assert result.passed is False
        assert result.actual_value == "1.5"


class TestMinAnnualRevenue:
    e = ev(RuleType.MIN_ANNUAL_REVENUE)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(annual_revenue=500_000), {"min_revenue": 100_000}).passed is True

    def test_fail(self):
        result = self.e.evaluate(make_ctx(annual_revenue=80_000), {"min_revenue": 100_000})
        assert result.passed is False

    def test_skip_when_revenue_not_provided(self):
        result = self.e.evaluate(make_ctx(annual_revenue=None), {"min_revenue": 100_000})
        assert result.skipped is True


class TestAllowedBusinessTypes:
    e = ev(RuleType.ALLOWED_BUSINESS_TYPES)

    def test_pass_when_type_in_list(self):
        ctx = make_ctx(business_type="llc")
        result = self.e.evaluate(ctx, {"types": ["llc", "corporation"]})
        assert result.passed is True

    def test_fail_when_type_not_in_list(self):
        ctx = make_ctx(business_type="sole_proprietor")
        result = self.e.evaluate(ctx, {"types": ["llc", "corporation"]})
        assert result.passed is False

    def test_case_insensitive_match(self):
        ctx = make_ctx(business_type="LLC")
        result = self.e.evaluate(ctx, {"types": ["llc"]})
        assert result.passed is True

    def test_skip_when_no_types_configured(self):
        result = self.e.evaluate(make_ctx(), {"types": []})
        assert result.skipped is True


class TestMinEmployeeCount:
    e = ev(RuleType.MIN_EMPLOYEE_COUNT)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(employee_count=10), {"min_count": 5}).passed is True

    def test_fail(self):
        assert self.e.evaluate(make_ctx(employee_count=3), {"min_count": 5}).passed is False

    def test_skip_when_not_provided(self):
        assert self.e.evaluate(make_ctx(employee_count=None), {"min_count": 5}).skipped is True


class TestMaxEmployeeCount:
    e = ev(RuleType.MAX_EMPLOYEE_COUNT)

    def test_pass(self):
        assert self.e.evaluate(make_ctx(employee_count=50), {"max_count": 100}).passed is True

    def test_fail(self):
        assert self.e.evaluate(make_ctx(employee_count=150), {"max_count": 100}).passed is False

    def test_skip_when_not_provided(self):
        assert self.e.evaluate(make_ctx(employee_count=None), {"max_count": 100}).skipped is True


class TestMinOwnershipPct:
    e = ev(RuleType.MIN_OWNERSHIP_PCT)

    def test_pass(self):
        ctx = make_ctx(guarantors=[{"credit_score": 720, "ownership_pct": 51.0}])
        assert self.e.evaluate(ctx, {"min_pct": 20.0}).passed is True

    def test_fail(self):
        ctx = make_ctx(guarantors=[{"credit_score": 720, "ownership_pct": 10.0}])
        result = self.e.evaluate(ctx, {"min_pct": 20.0})
        assert result.passed is False

    def test_uses_highest_ownership_across_guarantors(self):
        ctx = make_ctx(guarantors=[
            {"credit_score": 700, "ownership_pct": 10.0},
            {"credit_score": 680, "ownership_pct": 60.0},
        ])
        assert self.e.evaluate(ctx, {"min_pct": 51.0}).passed is True

    def test_skip_when_no_ownership_data(self):
        ctx = make_ctx(guarantors=[{"credit_score": 720, "ownership_pct": None}])
        assert self.e.evaluate(ctx, {"min_pct": 20.0}).skipped is True


class TestNaicsCodeAllowlist:
    e = ev(RuleType.NAICS_CODE_ALLOWLIST)

    def test_pass_exact_match(self):
        ctx = make_ctx(naics_code="238910")
        assert self.e.evaluate(ctx, {"codes": ["238910"]}).passed is True

    def test_pass_prefix_match(self):
        ctx = make_ctx(naics_code="238910")
        assert self.e.evaluate(ctx, {"codes": ["23"]}).passed is True

    def test_fail_no_match(self):
        ctx = make_ctx(naics_code="722511")
        result = self.e.evaluate(ctx, {"codes": ["238"]})
        assert result.passed is False

    def test_skip_when_no_naics_on_application(self):
        ctx = make_ctx(naics_code=None)
        assert self.e.evaluate(ctx, {"codes": ["238"]}).skipped is True

    def test_skip_when_no_codes_configured(self):
        assert self.e.evaluate(make_ctx(), {"codes": []}).skipped is True
