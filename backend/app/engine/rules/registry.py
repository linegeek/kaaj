"""Auto-discovery registry for rule evaluators."""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.engine.rules.base import RuleType, BaseRuleEvaluator

if TYPE_CHECKING:
    pass


class RuleEvaluatorRegistry:
    _evaluators: dict[RuleType, BaseRuleEvaluator] = {}

    @classmethod
    def register(cls, evaluator_cls: type[BaseRuleEvaluator]) -> type[BaseRuleEvaluator]:
        instance = evaluator_cls()
        cls._evaluators[evaluator_cls.rule_type] = instance
        return evaluator_cls

    @classmethod
    def get(cls, rule_type: RuleType) -> BaseRuleEvaluator:
        if rule_type not in cls._evaluators:
            raise ValueError(f"No evaluator registered for rule type: {rule_type!r}")
        return cls._evaluators[rule_type]

    @classmethod
    def all_types(cls) -> list[RuleType]:
        return list(cls._evaluators.keys())

    @classmethod
    def ensure_loaded(cls) -> None:
        """Import all evaluator modules to trigger their @register decorators."""
        import app.engine.rules.credit      # noqa: F401
        import app.engine.rules.business    # noqa: F401
        import app.engine.rules.equipment   # noqa: F401
        import app.engine.rules.geographic  # noqa: F401
