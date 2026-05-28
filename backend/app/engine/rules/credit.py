"""Credit-based rule evaluators (6 rules)."""
from typing import Any

from app.engine.rules.base import BaseRuleEvaluator, EvalContext, EvalResult, RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry


def _best_credit_score(ctx: EvalContext) -> int | None:
    scores = [g["credit_score"] for g in ctx.guarantors if g.get("credit_score") is not None]
    return max(scores) if scores else None


@RuleEvaluatorRegistry.register
class MinCreditScoreEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_CREDIT_SCORE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_score: int = parameters.get("min_score", 600)
        score = _best_credit_score(ctx)
        if score is None:
            return self.skip("No credit score on file")
        passed = score >= min_score
        return EvalResult(
            passed=passed,
            reason=f"Score {score} {'meets' if passed else 'below'} minimum {min_score}",
            actual_value=str(score),
        )


@RuleEvaluatorRegistry.register
class MaxBankruptciesEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_BANKRUPTCIES

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_count: int = parameters.get("max_count", 0)
        count = ctx.bankruptcies
        passed = count <= max_count
        return EvalResult(
            passed=passed,
            reason=f"{count} bankruptcies {'within' if passed else 'exceeds'} limit of {max_count}",
            actual_value=str(count),
        )


@RuleEvaluatorRegistry.register
class MinFicoSbssEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_FICO_SBSS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_score: int = parameters.get("min_score", 140)
        if ctx.fico_sbss is None:
            return self.skip("No FICO SBSS score on file")
        passed = ctx.fico_sbss >= min_score
        return EvalResult(
            passed=passed,
            reason=f"FICO SBSS {ctx.fico_sbss} {'meets' if passed else 'below'} minimum {min_score}",
            actual_value=str(ctx.fico_sbss),
        )


@RuleEvaluatorRegistry.register
class MinExperianIntelliscoreEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_EXPERIAN_INTELLISCORE

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_score: int = parameters.get("min_score", 50)
        if ctx.experian_intelliscore is None:
            return self.skip("No Experian Intelliscore on file")
        passed = ctx.experian_intelliscore >= min_score
        return EvalResult(
            passed=passed,
            reason=(
                f"Intelliscore {ctx.experian_intelliscore} "
                f"{'meets' if passed else 'below'} minimum {min_score}"
            ),
            actual_value=str(ctx.experian_intelliscore),
        )


@RuleEvaluatorRegistry.register
class MinDunsPaydexEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MIN_DUNS_PAYDEX

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        min_score: int = parameters.get("min_score", 70)
        if ctx.duns_paydex is None:
            return self.skip("No D&B PAYDEX score on file")
        passed = ctx.duns_paydex >= min_score
        return EvalResult(
            passed=passed,
            reason=f"PAYDEX {ctx.duns_paydex} {'meets' if passed else 'below'} minimum {min_score}",
            actual_value=str(ctx.duns_paydex),
        )


@RuleEvaluatorRegistry.register
class MaxDerogatoryMarksEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.MAX_DEROGATORY_MARKS

    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        max_count: int = parameters.get("max_count", 2)
        total = ctx.liens + ctx.judgments
        passed = total <= max_count
        return EvalResult(
            passed=passed,
            reason=(
                f"{total} derogatory marks (liens + judgments) "
                f"{'within' if passed else 'exceeds'} limit of {max_count}"
            ),
            actual_value=str(total),
        )
