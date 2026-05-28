"""Equipment-based rule evaluators (7 rules)."""
from typing import Any

from app.engine.rules.base import BaseRuleEvaluator, EvalContext, EvalResult, RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry


@RuleEvaluatorRegistry.register
class AllowedEquipmentTypesEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.ALLOWED_EQUIPMENT_TYPES

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = [t.lower() for t in parameters.get("types", [])]
        if not allowed:
            return self.skip("No equipment type restriction configured")
        eq_type = ctx.equipment_type.lower()
        passed = eq_type in allowed
        return EvalResult(
            passed=passed,
            reason=(
                f"Equipment type '{ctx.equipment_type}' "
                f"{'is' if passed else 'is not'} in allowed list"
            ),
            actual_value=ctx.equipment_type,
        )


@RuleEvaluatorRegistry.register
class MaxEquipmentAgeEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_EQUIPMENT_AGE_YRS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_age: float = parameters.get("max_age_yrs", 10.0)
        if ctx.equipment_age_yrs is None:
            return self.skip("Equipment age not provided")
        passed = ctx.equipment_age_yrs <= max_age
        return EvalResult(
            passed=passed,
            reason=(
                f"Equipment age {ctx.equipment_age_yrs:.1f} yrs "
                f"{'within' if passed else 'exceeds'} maximum {max_age} yrs"
            ),
            actual_value=str(ctx.equipment_age_yrs),
        )


@RuleEvaluatorRegistry.register
class MinLoanAmountEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_LOAN_AMOUNT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_amount: float = parameters.get("min_amount", 10_000)
        passed = ctx.requested_amount >= min_amount
        return EvalResult(
            passed=passed,
            reason=(
                f"Loan ${ctx.requested_amount:,.0f} "
                f"{'meets' if passed else 'below'} minimum ${min_amount:,.0f}"
            ),
            actual_value=str(ctx.requested_amount),
        )


@RuleEvaluatorRegistry.register
class MaxLoanAmountEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_LOAN_AMOUNT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_amount: float = parameters.get("max_amount", 500_000)
        passed = ctx.requested_amount <= max_amount
        return EvalResult(
            passed=passed,
            reason=(
                f"Loan ${ctx.requested_amount:,.0f} "
                f"{'within' if passed else 'exceeds'} maximum ${max_amount:,.0f}"
            ),
            actual_value=str(ctx.requested_amount),
        )


@RuleEvaluatorRegistry.register
class MaxTermMonthsEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_TERM_MONTHS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_months: int = parameters.get("max_months", 84)
        passed = ctx.requested_term_mo <= max_months
        return EvalResult(
            passed=passed,
            reason=(
                f"Term {ctx.requested_term_mo} months "
                f"{'within' if passed else 'exceeds'} maximum {max_months} months"
            ),
            actual_value=str(ctx.requested_term_mo),
        )


@RuleEvaluatorRegistry.register
class MinDownPaymentPctEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_DOWN_PAYMENT_PCT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_pct: float = parameters.get("min_pct", 10.0)
        if ctx.down_payment_pct is None:
            return self.skip("Down payment not provided")
        passed = ctx.down_payment_pct >= min_pct
        return EvalResult(
            passed=passed,
            reason=(
                f"Down payment {ctx.down_payment_pct:.1f}% "
                f"{'meets' if passed else 'below'} minimum {min_pct}%"
            ),
            actual_value=str(ctx.down_payment_pct),
        )


@RuleEvaluatorRegistry.register
class AllowedEquipmentConditionsEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.ALLOWED_EQUIPMENT_CONDITIONS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = [c.lower() for c in parameters.get("conditions", [])]
        if not allowed:
            return self.skip("No equipment condition restriction configured")
        if not ctx.equipment_condition:
            return self.skip("Equipment condition not provided")
        condition = ctx.equipment_condition.lower()
        passed = condition in allowed
        return EvalResult(
            passed=passed,
            reason=(
                f"Equipment condition '{ctx.equipment_condition}' "
                f"{'is' if passed else 'is not'} in allowed list"
            ),
            actual_value=ctx.equipment_condition,
        )
