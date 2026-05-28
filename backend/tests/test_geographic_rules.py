"""Tests for the 6 geographic rule evaluators."""
from app.engine.rules.base import RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry
from tests.conftest import make_ctx


def ev(rule_type: RuleType):
    return RuleEvaluatorRegistry.get(rule_type)


class TestAllowedStates:
    e = ev(RuleType.ALLOWED_STATES)

    def test_pass_when_state_in_list(self):
        ctx = make_ctx(state_of_operation="TX")
        assert self.e.evaluate(ctx, {"states": ["TX", "CA", "FL"]}).passed is True

    def test_fail_when_state_not_in_list(self):
        ctx = make_ctx(state_of_operation="NY")
        result = self.e.evaluate(ctx, {"states": ["TX", "CA", "FL"]})
        assert result.passed is False

    def test_falls_back_to_business_state_when_operation_state_missing(self):
        ctx = make_ctx(state="TX", state_of_operation=None)
        assert self.e.evaluate(ctx, {"states": ["TX"]}).passed is True

    def test_case_insensitive_input(self):
        ctx = make_ctx(state_of_operation="tx")
        assert self.e.evaluate(ctx, {"states": ["TX"]}).passed is True

    def test_skip_when_no_states_configured(self):
        assert self.e.evaluate(make_ctx(), {"states": []}).skipped is True


class TestExcludedStates:
    e = ev(RuleType.EXCLUDED_STATES)

    def test_pass_when_state_not_excluded(self):
        ctx = make_ctx(state_of_operation="TX")
        assert self.e.evaluate(ctx, {"states": ["NY", "CA"]}).passed is True

    def test_fail_when_state_is_excluded(self):
        ctx = make_ctx(state_of_operation="NY")
        result = self.e.evaluate(ctx, {"states": ["NY", "CA"]})
        assert result.passed is False
        assert result.actual_value == "NY"

    def test_skip_when_no_exclusions_configured(self):
        assert self.e.evaluate(make_ctx(), {"states": []}).skipped is True


class TestMinCreditScoreByState:
    e = ev(RuleType.MIN_CREDIT_SCORE_BY_STATE)

    def test_pass_when_score_meets_state_minimum(self):
        ctx = make_ctx(state_of_operation="TX", guarantors=[{"credit_score": 680, "ownership_pct": 100}])
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 650, "CA": 700}})
        assert result.passed is True

    def test_fail_when_score_below_state_minimum(self):
        ctx = make_ctx(state_of_operation="CA", guarantors=[{"credit_score": 680, "ownership_pct": 100}])
        result = self.e.evaluate(ctx, {"state_minimums": {"CA": 700}})
        assert result.passed is False

    def test_skip_when_no_rule_for_this_state(self):
        ctx = make_ctx(state_of_operation="MT")
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 650}})
        assert result.skipped is True

    def test_skip_when_no_credit_score(self):
        ctx = make_ctx(state_of_operation="TX", guarantors=[])
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 650}})
        assert result.skipped is True


class TestMaxLoanAmountByState:
    e = ev(RuleType.MAX_LOAN_AMOUNT_BY_STATE)

    def test_pass_when_within_state_limit(self):
        ctx = make_ctx(state_of_operation="TX", requested_amount=200_000)
        result = self.e.evaluate(ctx, {"state_maximums": {"TX": 500_000}})
        assert result.passed is True

    def test_fail_when_over_state_limit(self):
        ctx = make_ctx(state_of_operation="TX", requested_amount=600_000)
        result = self.e.evaluate(ctx, {"state_maximums": {"TX": 500_000}})
        assert result.passed is False

    def test_skip_when_no_limit_for_state(self):
        ctx = make_ctx(state_of_operation="WY")
        result = self.e.evaluate(ctx, {"state_maximums": {"TX": 500_000}})
        assert result.skipped is True


class TestMinYearsInBusinessByState:
    e = ev(RuleType.MIN_YEARS_IN_BUSINESS_BY_STATE)

    def test_pass(self):
        ctx = make_ctx(state_of_operation="TX", years_in_biz=5.0)
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 3.0}})
        assert result.passed is True

    def test_fail(self):
        ctx = make_ctx(state_of_operation="TX", years_in_biz=1.0)
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 3.0}})
        assert result.passed is False

    def test_skip_when_no_rule_for_state(self):
        ctx = make_ctx(state_of_operation="AK")
        result = self.e.evaluate(ctx, {"state_minimums": {"TX": 3.0}})
        assert result.skipped is True


class TestAllowedStatesForEquipment:
    e = ev(RuleType.ALLOWED_STATES_FOR_EQUIPMENT)

    def test_pass_when_operation_state_allowed(self):
        ctx = make_ctx(state_of_operation="TX")
        assert self.e.evaluate(ctx, {"states": ["TX", "OK"]}).passed is True

    def test_fail_when_operation_state_not_allowed(self):
        ctx = make_ctx(state_of_operation="CA")
        result = self.e.evaluate(ctx, {"states": ["TX", "OK"]})
        assert result.passed is False

    def test_skip_when_operation_state_not_specified(self):
        ctx = make_ctx(state_of_operation=None)
        result = self.e.evaluate(ctx, {"states": ["TX"]})
        assert result.skipped is True

    def test_does_not_fall_back_to_business_state(self):
        # Unlike ALLOWED_STATES, this rule only uses state_of_operation
        ctx = make_ctx(state="TX", state_of_operation=None)
        result = self.e.evaluate(ctx, {"states": ["TX"]})
        assert result.skipped is True
