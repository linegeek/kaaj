"""Business-based rule evaluators (7 rules)."""
from typing import Any

from app.engine.rules.base import BaseRuleEvaluator, EvalContext, EvalResult, RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry


@RuleEvaluatorRegistry.register
class MinYearsInBusinessEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_YEARS_IN_BUSINESS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_years: float = parameters.get("min_years", 2.0)
        passed = ctx.years_in_biz >= min_years
        return EvalResult(
            passed=passed,
            reason=(
                f"{ctx.years_in_biz:.1f} years in business "
                f"{'meets' if passed else 'below'} minimum {min_years}"
            ),
            actual_value=str(ctx.years_in_biz),
        )


@RuleEvaluatorRegistry.register
class MinAnnualRevenueEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_ANNUAL_REVENUE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_revenue: float = parameters.get("min_revenue", 100_000)
        if ctx.annual_revenue is None:
            return self.skip("Annual revenue not provided")
        passed = ctx.annual_revenue >= min_revenue
        return EvalResult(
            passed=passed,
            reason=(
                f"Revenue ${ctx.annual_revenue:,.0f} "
                f"{'meets' if passed else 'below'} minimum ${min_revenue:,.0f}"
            ),
            actual_value=str(ctx.annual_revenue),
        )


@RuleEvaluatorRegistry.register
class AllowedBusinessTypesEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.ALLOWED_BUSINESS_TYPES

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = [t.lower() for t in parameters.get("types", [])]
        if not allowed:
            return self.skip("No business type restriction configured")
        biz_type = ctx.business_type.lower()
        passed = biz_type in allowed
        return EvalResult(
            passed=passed,
            reason=(
                f"Business type '{ctx.business_type}' "
                f"{'is' if passed else 'is not'} in allowed list"
            ),
            actual_value=ctx.business_type,
        )


@RuleEvaluatorRegistry.register
class MinEmployeeCountEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_EMPLOYEE_COUNT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_count: int = parameters.get("min_count", 1)
        if ctx.employee_count is None:
            return self.skip("Employee count not provided")
        passed = ctx.employee_count >= min_count
        return EvalResult(
            passed=passed,
            reason=(
                f"{ctx.employee_count} employees "
                f"{'meets' if passed else 'below'} minimum {min_count}"
            ),
            actual_value=str(ctx.employee_count),
        )


@RuleEvaluatorRegistry.register
class MaxEmployeeCountEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_EMPLOYEE_COUNT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_count: int = parameters.get("max_count", 500)
        if ctx.employee_count is None:
            return self.skip("Employee count not provided")
        passed = ctx.employee_count <= max_count
        return EvalResult(
            passed=passed,
            reason=(
                f"{ctx.employee_count} employees "
                f"{'within' if passed else 'exceeds'} maximum {max_count}"
            ),
            actual_value=str(ctx.employee_count),
        )


@RuleEvaluatorRegistry.register
class MinOwnershipPctEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_OWNERSHIP_PCT

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_pct: float = parameters.get("min_pct", 20.0)
        pcts = [g["ownership_pct"] for g in ctx.guarantors if g.get("ownership_pct") is not None]
        if not pcts:
            return self.skip("No guarantor ownership data provided")
        best = max(pcts)
        passed = best >= min_pct
        return EvalResult(
            passed=passed,
            reason=(
                f"Guarantor ownership {best:.1f}% "
                f"{'meets' if passed else 'below'} minimum {min_pct}%"
            ),
            actual_value=str(best),
        )


@RuleEvaluatorRegistry.register
class NaicsCodeAllowlistEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.NAICS_CODE_ALLOWLIST

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        allowed: list[str] = parameters.get("codes", [])
        if not allowed:
            return self.skip("No NAICS code restriction configured")
        if not ctx.naics_code:
            return self.skip("NAICS code not provided on application")
        # Support prefix matching: allowed code "48" matches "484110"
        passed = any(ctx.naics_code.startswith(code) for code in allowed)
        return EvalResult(
            passed=passed,
            reason=(
                f"NAICS {ctx.naics_code} "
                f"{'is' if passed else 'is not'} in allowed list"
            ),
            actual_value=ctx.naics_code,
        )
