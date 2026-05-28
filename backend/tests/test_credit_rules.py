"""Tests for the 6 credit rule evaluators."""
import pytest
from app.engine.rules.base import RuleType
from app.engine.rules.registry import RuleEvaluatorRegistry
from tests.conftest import make_ctx


def evaluator(rule_type: RuleType):
    return RuleEvaluatorRegistry.get(rule_type)


# ---- MIN_CREDIT_SCORE -------------------------------------------------------

class TestMinCreditScore:
    ev = evaluator(RuleType.MIN_CREDIT_SCORE)

    def test_pass_when_score_meets_minimum(self):
        ctx = make_ctx(guarantors=[{"credit_score": 720, "ownership_pct": 100}])
        result = self.ev.evaluate(ctx, {"min_score": 650})
        assert result.passed is True
        assert "720" in result.reason

    def test_pass_when_score_equals_minimum(self):
        ctx = make_ctx(guarantors=[{"credit_score": 650, "ownership_pct": 100}])
        result = self.ev.evaluate(ctx, {"min_score": 650})
        assert result.passed is True

    def test_fail_when_score_below_minimum(self):
        ctx = make_ctx(guarantors=[{"credit_score": 580, "ownership_pct": 100}])
        result = self.ev.evaluate(ctx, {"min_score": 650})
        assert result.passed is False
        assert result.actual_value == "580"

    def test_skip_when_no_guarantors(self):
        ctx = make_ctx(guarantors=[])
        result = self.ev.evaluate(ctx, {"min_score": 650})
        assert result.skipped is True
        assert result.passed is True  # skip counts as non-failure

    def test_skip_when_credit_score_is_none(self):
        ctx = make_ctx(guarantors=[{"credit_score": None, "ownership_pct": 100}])
        result = self.ev.evaluate(ctx, {"min_score": 650})
        assert result.skipped is True

    def test_uses_best_score_across_multiple_guarantors(self):
        ctx = make_ctx(guarantors=[
            {"credit_score": 580, "ownership_pct": 50},
            {"credit_score": 720, "ownership_pct": 50},
        ])
        result = self.ev.evaluate(ctx, {"min_score": 700})
        assert result.passed is True
        assert result.actual_value == "720"


# ---- MAX_BANKRUPTCIES -------------------------------------------------------

class TestMaxBankruptcies:
    ev = evaluator(RuleType.MAX_BANKRUPTCIES)

    def test_pass_when_zero_bankruptcies(self):
        ctx = make_ctx(bankruptcies=0)
        result = self.ev.evaluate(ctx, {"max_count": 0})
        assert result.passed is True

    def test_fail_when_bankruptcies_exceed_limit(self):
        ctx = make_ctx(bankruptcies=1)
        result = self.ev.evaluate(ctx, {"max_count": 0})
        assert result.passed is False
        assert result.actual_value == "1"

    def test_pass_when_within_limit(self):
        ctx = make_ctx(bankruptcies=1)
        result = self.ev.evaluate(ctx, {"max_count": 1})
        assert result.passed is True

    def test_fail_when_over_limit(self):
        ctx = make_ctx(bankruptcies=2)
        result = self.ev.evaluate(ctx, {"max_count": 1})
        assert result.passed is False


# ---- MIN_FICO_SBSS ----------------------------------------------------------

class TestMinFicoSbss:
    ev = evaluator(RuleType.MIN_FICO_SBSS)

    def test_pass_when_score_meets_minimum(self):
        ctx = make_ctx(fico_sbss=160)
        result = self.ev.evaluate(ctx, {"min_score": 140})
        assert result.passed is True

    def test_fail_when_score_below_minimum(self):
        ctx = make_ctx(fico_sbss=120)
        result = self.ev.evaluate(ctx, {"min_score": 140})
        assert result.passed is False

    def test_skip_when_no_sbss_score(self):
        ctx = make_ctx(fico_sbss=None)
        result = self.ev.evaluate(ctx, {"min_score": 140})
        assert result.skipped is True


# ---- MIN_EXPERIAN_INTELLISCORE ----------------------------------------------

class TestMinExperianIntelliscore:
    ev = evaluator(RuleType.MIN_EXPERIAN_INTELLISCORE)

    def test_pass(self):
        ctx = make_ctx(experian_intelliscore=75)
        result = self.ev.evaluate(ctx, {"min_score": 60})
        assert result.passed is True

    def test_fail(self):
        ctx = make_ctx(experian_intelliscore=45)
        result = self.ev.evaluate(ctx, {"min_score": 60})
        assert result.passed is False

    def test_skip_when_none(self):
        ctx = make_ctx(experian_intelliscore=None)
        result = self.ev.evaluate(ctx, {"min_score": 60})
        assert result.skipped is True


# ---- MIN_DUNS_PAYDEX --------------------------------------------------------

class TestMinDunsPaydex:
    ev = evaluator(RuleType.MIN_DUNS_PAYDEX)

    def test_pass(self):
        ctx = make_ctx(duns_paydex=80)
        result = self.ev.evaluate(ctx, {"min_score": 70})
        assert result.passed is True

    def test_fail(self):
        ctx = make_ctx(duns_paydex=60)
        result = self.ev.evaluate(ctx, {"min_score": 70})
        assert result.passed is False

    def test_skip_when_none(self):
        ctx = make_ctx(duns_paydex=None)
        result = self.ev.evaluate(ctx, {"min_score": 70})
        assert result.skipped is True


# ---- MAX_DEROGATORY_MARKS ---------------------------------------------------

class TestMaxDerogatoryMarks:
    ev = evaluator(RuleType.MAX_DEROGATORY_MARKS)

    def test_pass_when_no_marks(self):
        ctx = make_ctx(liens=0, judgments=0)
        result = self.ev.evaluate(ctx, {"max_count": 2})
        assert result.passed is True

    def test_pass_at_limit(self):
        ctx = make_ctx(liens=1, judgments=1)
        result = self.ev.evaluate(ctx, {"max_count": 2})
        assert result.passed is True

    def test_fail_when_over_limit(self):
        ctx = make_ctx(liens=2, judgments=1)
        result = self.ev.evaluate(ctx, {"max_count": 2})
        assert result.passed is False
        assert result.actual_value == "3"

    def test_combines_liens_and_judgments(self):
        ctx = make_ctx(liens=3, judgments=0)
        result = self.ev.evaluate(ctx, {"max_count": 2})
        assert result.passed is False
