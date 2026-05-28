"""Fit score computation.

Formula: base = (passed_weight / total_weight) * 85
         bonus = up to +15 for strong credit, long tenure, high revenue
         score = min(100, base + bonus)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.engine.rules.base import EvalContext, EvalResult, RuleType


@dataclass
class CriteriaCheckResult:
    rule_id: str
    rule_type: str
    rule_name: str
    weight: float
    passed: bool
    reason: str
    actual_value: str | None
    skipped: bool


@dataclass
class FitScoreResult:
    fit_score: float
    passed_count: int
    failed_count: int
    skipped_count: int
    criteria: list[CriteriaCheckResult]


class FitScorer:
    BASE_MAX = 85.0
    BONUS_MAX = 15.0

    def score(
        self,
        ctx: EvalContext,
        rules: list[dict[str, Any]],
    ) -> FitScoreResult:
        """
        Evaluate all rules and produce a fit score.

        Each rule dict must have: id, rule_type, label (optional), weight, parameters.
        """
        from app.engine.rules.base import RuleType
        from app.engine.rules.registry import RuleEvaluatorRegistry

        criteria: list[CriteriaCheckResult] = []
        total_weight = 0.0
        passed_weight = 0.0

        for rule in rules:
            try:
                rule_type = RuleType(rule["rule_type"])
                evaluator = RuleEvaluatorRegistry.get(rule_type)
            except (ValueError, KeyError):
                continue

            result: EvalResult = evaluator.evaluate(ctx, rule.get("parameters", {}))
            weight: float = float(rule.get("weight", 1.0))
            name: str = rule.get("label") or rule_type.value.replace("_", " ").title()

            criteria.append(
                CriteriaCheckResult(
                    rule_id=str(rule["id"]),
                    rule_type=rule_type.value,
                    rule_name=name,
                    weight=weight,
                    passed=result.passed,
                    reason=result.reason,
                    actual_value=result.actual_value,
                    skipped=result.skipped,
                )
            )

            if not result.skipped:
                total_weight += weight
                if result.passed:
                    passed_weight += weight

        # Base score
        if total_weight > 0:
            base = (passed_weight / total_weight) * self.BASE_MAX
        else:
            base = self.BASE_MAX  # no non-skipped rules = full base score

        # Bonus signals
        bonus = 0.0
        best_score = max(
            (g["credit_score"] for g in ctx.guarantors if g.get("credit_score")),
            default=None,
        )
        if best_score and best_score >= 750:
            bonus += 5.0
        if ctx.years_in_biz >= 10:
            bonus += 5.0
        elif ctx.years_in_biz >= 5:
            bonus += 2.5
        if ctx.annual_revenue and ctx.annual_revenue >= 1_000_000:
            bonus += 5.0
        elif ctx.annual_revenue and ctx.annual_revenue >= 500_000:
            bonus += 2.5

        fit_score = round(min(100.0, base + bonus), 2)
        passed_count = sum(1 for c in criteria if c.passed and not c.skipped)
        failed_count = sum(1 for c in criteria if not c.passed and not c.skipped)
        skipped_count = sum(1 for c in criteria if c.skipped)

        return FitScoreResult(
            fit_score=fit_score,
            passed_count=passed_count,
            failed_count=failed_count,
            skipped_count=skipped_count,
            criteria=criteria,
        )
