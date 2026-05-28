"""Geographic rule evaluators (6 rules)."""
from typing import Any

from app.engine.rules.base import BaseRuleEvaluator, EvalContext, EvalResult, RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry


def _operation_state(ctx: EvalContext) -> str:
    """Return state of equipment operation, falling back to business state."""
    return (ctx.state_of_operation or ctx.state).upper()


def _best_credit_score(ctx: EvalContext) -> int | None:
    scores = [g["credit_score"] for g in ctx.guarantors if g.get("credit_score") is not None]
    return max(scores) if scores else None


@RuleEvaluatorRegistry.register
class AllowedStatesEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.ALLOWED_STATES

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = [s.upper() for s in parameters.get("states", [])]
        if not allowed:
            return self.skip("No state restriction configured")
        state = _operation_state(ctx)
        passed = state in allowed
        return EvalResult(
            passed=passed,
            reason=f"State {state} {'is' if passed else 'is not'} in allowed states",
            actual_value=state,
        )


@RuleEvaluatorRegistry.register
class ExcludedStatesEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.EXCLUDED_STATES

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        excluded: list[str] = [s.upper() for s in parameters.get("states", [])]
        if not excluded:
            return self.skip("No state exclusion configured")
        state = _operation_state(ctx)
        passed = state not in excluded
        return EvalResult(
            passed=passed,
            reason=f"State {state} {'is not' if passed else 'is'} in excluded states",
            actual_value=state,
        )


@RuleEvaluatorRegistry.register
class MinCreditScoreByStateEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_CREDIT_SCORE_BY_STATE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        state_minimums: dict[str, int] = {
            k.upper(): v for k, v in parameters.get("state_minimums", {}).items()
        }
        state = _operation_state(ctx)
        if state not in state_minimums:
            return self.skip(f"No state-specific credit rule for {state}")
        min_score = state_minimums[state]
        score = _best_credit_score(ctx)
        if score is None:
            return self.skip("No credit score on file")
        passed = score >= min_score
        return EvalResult(
            passed=passed,
            reason=(
                f"Score {score} {'meets' if passed else 'below'} "
                f"{state}-specific minimum {min_score}"
            ),
            actual_value=str(score),
        )


@RuleEvaluatorRegistry.register
class MaxLoanAmountByStateEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_LOAN_AMOUNT_BY_STATE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        state_maximums: dict[str, float] = {
            k.upper(): v for k, v in parameters.get("state_maximums", {}).items()
        }
        state = _operation_state(ctx)
        if state not in state_maximums:
            return self.skip(f"No state-specific loan limit for {state}")
        max_amount = state_maximums[state]
        passed = ctx.requested_amount <= max_amount
        return EvalResult(
            passed=passed,
            reason=(
                f"Loan ${ctx.requested_amount:,.0f} "
                f"{'within' if passed else 'exceeds'} {state} limit ${max_amount:,.0f}"
            ),
            actual_value=str(ctx.requested_amount),
        )


@RuleEvaluatorRegistry.register
class MinYearsInBusinessByStateEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_YEARS_IN_BUSINESS_BY_STATE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        state_minimums: dict[str, float] = {
            k.upper(): v for k, v in parameters.get("state_minimums", {}).items()
        }
        state = _operation_state(ctx)
        if state not in state_minimums:
            return self.skip(f"No state-specific seasoning rule for {state}")
        min_years = state_minimums[state]
        passed = ctx.years_in_biz >= min_years
        return EvalResult(
            passed=passed,
            reason=(
                f"{ctx.years_in_biz:.1f} yrs {'meets' if passed else 'below'} "
                f"{state}-specific minimum {min_years} yrs"
            ),
            actual_value=str(ctx.years_in_biz),
        )


@RuleEvaluatorRegistry.register
class AllowedStatesForEquipmentEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.ALLOWED_STATES_FOR_EQUIPMENT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = [s.upper() for s in parameters.get("states", [])]
        if not allowed:
            return self.skip("No equipment operation state restriction configured")
        # This rule always uses state_of_operation, not business state
        if not ctx.state_of_operation:
            return self.skip("State of equipment operation not specified")
        state = ctx.state_of_operation.upper()
        passed = state in allowed
        return EvalResult(
            passed=passed,
            reason=(
                f"Equipment operation state {state} "
                f"{'is' if passed else 'is not'} in allowed states"
            ),
            actual_value=state,
        )
