"""Tests for FitScorer — weighted scoring and bonus logic."""
import uuid
import pytest
from app.engine.scorer import FitScorer
from tests.conftest import make_ctx


def make_rule(rule_type: str, parameters: dict, weight: float = 1.0, label: str | None = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "rule_type": rule_type,
        "label": label,
        "weight": weight,
        "parameters": parameters,
    }


scorer = FitScorer()


class TestBaseScoringFormula:
    def test_all_rules_pass_gives_full_base_score(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 700, "ownership_pct": 100}],
            years_in_biz=3.0,
            annual_revenue=200_000,
        )
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, weight=2.0),
            make_rule("MIN_YEARS_IN_BUSINESS", {"min_years": 2.0}, weight=1.0),
            make_rule("MAX_BANKRUPTCIES", {"max_count": 0}, weight=1.0),
        ]
        result = scorer.score(ctx, rules)
        assert result.passed_count == 3
        assert result.failed_count == 0
        # base = 85, no bonus qualifications for 700 credit / 3 yrs / 200k revenue
        assert result.fit_score == pytest.approx(85.0, abs=0.01)

    def test_all_rules_fail_gives_zero_base_score(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 500, "ownership_pct": 100}],
            years_in_biz=0.5,
            annual_revenue=50_000,
            bankruptcies=2,
        )
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 700}),
            make_rule("MIN_YEARS_IN_BUSINESS", {"min_years": 2.0}),
            make_rule("MAX_BANKRUPTCIES", {"max_count": 0}),
        ]
        result = scorer.score(ctx, rules)
        assert result.failed_count == 3
        assert result.fit_score == pytest.approx(0.0, abs=0.01)

    def test_half_weighted_rules_pass_gives_half_base(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 720, "ownership_pct": 100}],
            requested_amount=600_000,  # will fail MAX_LOAN_AMOUNT
        )
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, weight=1.0),   # pass
            make_rule("MAX_LOAN_AMOUNT", {"max_amount": 500_000}, weight=1.0),  # fail
        ]
        result = scorer.score(ctx, rules)
        assert result.passed_count == 1
        assert result.failed_count == 1
        # base = (1/2) * 85 = 42.5
        assert result.fit_score == pytest.approx(42.5, abs=0.01)

    def test_weighted_rules_use_weight_not_count(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 720, "ownership_pct": 100}],
            requested_amount=600_000,
        )
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, weight=3.0),  # pass, weight 3
            make_rule("MAX_LOAN_AMOUNT", {"max_amount": 500_000}, weight=1.0),  # fail, weight 1
        ]
        result = scorer.score(ctx, rules)
        # base = (3/4) * 85 = 63.75
        assert result.fit_score == pytest.approx(63.75, abs=0.01)

    def test_skipped_rules_not_counted_in_total_weight(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 720, "ownership_pct": 100}],
            fico_sbss=None,  # FICO rule will skip
        )
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, weight=1.0),  # pass
            make_rule("MIN_FICO_SBSS", {"min_score": 140}, weight=2.0),     # skip
        ]
        result = scorer.score(ctx, rules)
        assert result.skipped_count == 1
        assert result.passed_count == 1
        # Only credit rule counts: (1/1) * 85 = 85
        assert result.fit_score == pytest.approx(85.0, abs=0.01)

    def test_no_active_rules_gives_full_base_score(self):
        ctx = make_ctx()
        result = scorer.score(ctx, [])
        assert result.fit_score == pytest.approx(85.0, abs=0.01)


class TestBonusLogic:
    def test_high_credit_score_adds_bonus(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 780, "ownership_pct": 100}],
            years_in_biz=3.0,
            annual_revenue=200_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, weight=1.0)]
        result = scorer.score(ctx, rules)
        # base=85, credit bonus=+5
        assert result.fit_score == pytest.approx(90.0, abs=0.01)

    def test_long_tenure_adds_bonus(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 700, "ownership_pct": 100}],
            years_in_biz=12.0,
            annual_revenue=200_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650})]
        result = scorer.score(ctx, rules)
        # base=85, tenure bonus=+5
        assert result.fit_score == pytest.approx(90.0, abs=0.01)

    def test_medium_tenure_adds_partial_bonus(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 700, "ownership_pct": 100}],
            years_in_biz=7.0,
            annual_revenue=200_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650})]
        result = scorer.score(ctx, rules)
        # base=85, tenure bonus=+2.5
        assert result.fit_score == pytest.approx(87.5, abs=0.01)

    def test_high_revenue_adds_bonus(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 700, "ownership_pct": 100}],
            years_in_biz=3.0,
            annual_revenue=1_500_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650})]
        result = scorer.score(ctx, rules)
        # base=85, revenue bonus=+5
        assert result.fit_score == pytest.approx(90.0, abs=0.01)

    def test_medium_revenue_adds_partial_bonus(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 700, "ownership_pct": 100}],
            years_in_biz=3.0,
            annual_revenue=600_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650})]
        result = scorer.score(ctx, rules)
        # base=85, revenue bonus=+2.5
        assert result.fit_score == pytest.approx(87.5, abs=0.01)

    def test_all_bonuses_combined_and_capped_at_100(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 800, "ownership_pct": 100}],
            years_in_biz=15.0,
            annual_revenue=2_000_000,
        )
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650})]
        result = scorer.score(ctx, rules)
        # base=85, credit=+5, tenure=+5, revenue=+5 = 100 (capped)
        assert result.fit_score == 100.0

    def test_score_does_not_exceed_100_even_with_all_bonuses(self):
        ctx = make_ctx(
            guarantors=[{"credit_score": 850, "ownership_pct": 100}],
            years_in_biz=20.0,
            annual_revenue=5_000_000,
        )
        result = scorer.score(ctx, [])
        assert result.fit_score <= 100.0


class TestResultStructure:
    def test_criteria_contains_entry_per_rule(self):
        ctx = make_ctx()
        rules = [
            make_rule("MIN_CREDIT_SCORE", {"min_score": 650}),
            make_rule("MIN_YEARS_IN_BUSINESS", {"min_years": 2.0}),
        ]
        result = scorer.score(ctx, rules)
        assert len(result.criteria) == 2

    def test_criteria_rule_name_uses_label_when_provided(self):
        ctx = make_ctx(guarantors=[{"credit_score": 720, "ownership_pct": 100}])
        rules = [make_rule("MIN_CREDIT_SCORE", {"min_score": 650}, label="My Credit Rule")]
        result = scorer.score(ctx, rules)
        assert result.criteria[0].rule_name == "My Credit Rule"

    def test_unknown_rule_type_is_silently_skipped(self):
        ctx = make_ctx()
        rules = [
            make_rule("NONEXISTENT_RULE_TYPE", {}),
            make_rule("MIN_YEARS_IN_BUSINESS", {"min_years": 2.0}),
        ]
        result = scorer.score(ctx, rules)
        # Only the valid rule produces a criteria entry
        assert len(result.criteria) == 1
