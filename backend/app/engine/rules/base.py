"""Base types for the rule engine."""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RuleType(str, Enum):
    # Credit
    MIN_CREDIT_SCORE = "MIN_CREDIT_SCORE"
    MAX_BANKRUPTCIES = "MAX_BANKRUPTCIES"
    MIN_FICO_SBSS = "MIN_FICO_SBSS"
    MIN_EXPERIAN_INTELLISCORE = "MIN_EXPERIAN_INTELLISCORE"
    MIN_DUNS_PAYDEX = "MIN_DUNS_PAYDEX"
    MAX_DEROGATORY_MARKS = "MAX_DEROGATORY_MARKS"
    # Business
    MIN_YEARS_IN_BUSINESS = "MIN_YEARS_IN_BUSINESS"
    MIN_ANNUAL_REVENUE = "MIN_ANNUAL_REVENUE"
    ALLOWED_BUSINESS_TYPES = "ALLOWED_BUSINESS_TYPES"
    MIN_EMPLOYEE_COUNT = "MIN_EMPLOYEE_COUNT"
    MAX_EMPLOYEE_COUNT = "MAX_EMPLOYEE_COUNT"
    MIN_OWNERSHIP_PCT = "MIN_OWNERSHIP_PCT"
    NAICS_CODE_ALLOWLIST = "NAICS_CODE_ALLOWLIST"
    # Equipment
    ALLOWED_EQUIPMENT_TYPES = "ALLOWED_EQUIPMENT_TYPES"
    MAX_EQUIPMENT_AGE_YRS = "MAX_EQUIPMENT_AGE_YRS"
    MIN_LOAN_AMOUNT = "MIN_LOAN_AMOUNT"
    MAX_LOAN_AMOUNT = "MAX_LOAN_AMOUNT"
    MAX_TERM_MONTHS = "MAX_TERM_MONTHS"
    MIN_DOWN_PAYMENT_PCT = "MIN_DOWN_PAYMENT_PCT"
    ALLOWED_EQUIPMENT_CONDITIONS = "ALLOWED_EQUIPMENT_CONDITIONS"
    # Geographic
    ALLOWED_STATES = "ALLOWED_STATES"
    EXCLUDED_STATES = "EXCLUDED_STATES"
    MIN_CREDIT_SCORE_BY_STATE = "MIN_CREDIT_SCORE_BY_STATE"
    MAX_LOAN_AMOUNT_BY_STATE = "MAX_LOAN_AMOUNT_BY_STATE"
    MIN_YEARS_IN_BUSINESS_BY_STATE = "MIN_YEARS_IN_BUSINESS_BY_STATE"
    ALLOWED_STATES_FOR_EQUIPMENT = "ALLOWED_STATES_FOR_EQUIPMENT"


# Human-readable metadata for each rule type used by the API and frontend
RULE_TYPE_META: dict[RuleType, dict[str, Any]] = {
    RuleType.MIN_CREDIT_SCORE: {
        "label": "Minimum Credit Score",
        "category": "credit",
        "param_schema": {"min_score": "integer"},
    },
    RuleType.MAX_BANKRUPTCIES: {
        "label": "Maximum Bankruptcies",
        "category": "credit",
        "param_schema": {"max_count": "integer"},
    },
    RuleType.MIN_FICO_SBSS: {
        "label": "Minimum FICO SBSS",
        "category": "credit",
        "param_schema": {"min_score": "integer"},
    },
    RuleType.MIN_EXPERIAN_INTELLISCORE: {
        "label": "Minimum Experian Intelliscore",
        "category": "credit",
        "param_schema": {"min_score": "integer"},
    },
    RuleType.MIN_DUNS_PAYDEX: {
        "label": "Minimum D&B PAYDEX",
        "category": "credit",
        "param_schema": {"min_score": "integer"},
    },
    RuleType.MAX_DEROGATORY_MARKS: {
        "label": "Maximum Derogatory Marks",
        "category": "credit",
        "param_schema": {"max_count": "integer"},
    },
    RuleType.MIN_YEARS_IN_BUSINESS: {
        "label": "Minimum Years in Business",
        "category": "business",
        "param_schema": {"min_years": "number"},
    },
    RuleType.MIN_ANNUAL_REVENUE: {
        "label": "Minimum Annual Revenue",
        "category": "business",
        "param_schema": {"min_revenue": "number"},
    },
    RuleType.ALLOWED_BUSINESS_TYPES: {
        "label": "Allowed Business Types",
        "category": "business",
        "param_schema": {"types": "array[string]"},
    },
    RuleType.MIN_EMPLOYEE_COUNT: {
        "label": "Minimum Employee Count",
        "category": "business",
        "param_schema": {"min_count": "integer"},
    },
    RuleType.MAX_EMPLOYEE_COUNT: {
        "label": "Maximum Employee Count",
        "category": "business",
        "param_schema": {"max_count": "integer"},
    },
    RuleType.MIN_OWNERSHIP_PCT: {
        "label": "Minimum Guarantor Ownership %",
        "category": "business",
        "param_schema": {"min_pct": "number"},
    },
    RuleType.NAICS_CODE_ALLOWLIST: {
        "label": "NAICS Code Allowlist",
        "category": "business",
        "param_schema": {"codes": "array[string]"},
    },
    RuleType.ALLOWED_EQUIPMENT_TYPES: {
        "label": "Allowed Equipment Types",
        "category": "equipment",
        "param_schema": {"types": "array[string]"},
    },
    RuleType.MAX_EQUIPMENT_AGE_YRS: {
        "label": "Maximum Equipment Age (years)",
        "category": "equipment",
        "param_schema": {"max_age_yrs": "number"},
    },
    RuleType.MIN_LOAN_AMOUNT: {
        "label": "Minimum Loan Amount",
        "category": "equipment",
        "param_schema": {"min_amount": "number"},
    },
    RuleType.MAX_LOAN_AMOUNT: {
        "label": "Maximum Loan Amount",
        "category": "equipment",
        "param_schema": {"max_amount": "number"},
    },
    RuleType.MAX_TERM_MONTHS: {
        "label": "Maximum Term (months)",
        "category": "equipment",
        "param_schema": {"max_months": "integer"},
    },
    RuleType.MIN_DOWN_PAYMENT_PCT: {
        "label": "Minimum Down Payment %",
        "category": "equipment",
        "param_schema": {"min_pct": "number"},
    },
    RuleType.ALLOWED_EQUIPMENT_CONDITIONS: {
        "label": "Allowed Equipment Conditions",
        "category": "equipment",
        "param_schema": {"conditions": "array[string]"},
    },
    RuleType.ALLOWED_STATES: {
        "label": "Allowed States",
        "category": "geographic",
        "param_schema": {"states": "array[string]"},
    },
    RuleType.EXCLUDED_STATES: {
        "label": "Excluded States",
        "category": "geographic",
        "param_schema": {"states": "array[string]"},
    },
    RuleType.MIN_CREDIT_SCORE_BY_STATE: {
        "label": "Min Credit Score by State",
        "category": "geographic",
        "param_schema": {"state_minimums": "object{state: score}"},
    },
    RuleType.MAX_LOAN_AMOUNT_BY_STATE: {
        "label": "Max Loan Amount by State",
        "category": "geographic",
        "param_schema": {"state_maximums": "object{state: amount}"},
    },
    RuleType.MIN_YEARS_IN_BUSINESS_BY_STATE: {
        "label": "Min Years in Business by State",
        "category": "geographic",
        "param_schema": {"state_minimums": "object{state: years}"},
    },
    RuleType.ALLOWED_STATES_FOR_EQUIPMENT: {
        "label": "Allowed States for Equipment Operation",
        "category": "geographic",
        "param_schema": {"states": "array[string]"},
    },
}


@dataclass
class EvalContext:
    """All application data available to every rule evaluator."""
    # Personal guarantors — list of dicts with credit_score, ownership_pct
    guarantors: list[dict[str, Any]] = field(default_factory=list)
    # Business info
    business_name: str = ""
    business_type: str = ""
    state: str = ""
    years_in_biz: float = 0.0
    annual_revenue: float | None = None
    employee_count: int | None = None
    naics_code: str | None = None
    # Business credit
    fico_sbss: int | None = None
    experian_intelliscore: int | None = None
    duns_paydex: int | None = None
    bankruptcies: int = 0
    liens: int = 0
    judgments: int = 0
    # Loan request
    requested_amount: float = 0.0
    requested_term_mo: int = 0
    equipment_type: str = ""
    equipment_age_yrs: float | None = None
    equipment_condition: str | None = None
    state_of_operation: str | None = None
    down_payment_pct: float | None = None


@dataclass
class EvalResult:
    passed: bool
    reason: str
    actual_value: str | None = None
    skipped: bool = False


class BaseRuleEvaluator(abc.ABC):
    rule_type: RuleType

    @abc.abstractmethod
    def evaluate(self, ctx: EvalContext, parameters: dict[str, Any]) -> EvalResult:
        """Evaluate the rule against the application context."""
        ...

    def skip(self, reason: str) -> EvalResult:
        return EvalResult(passed=True, reason=reason, skipped=True)
