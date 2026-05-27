# Loan Underwriting & Lender Matching System — Architecture & Design Plan

> **Project:** Kaaj — Equipment Finance Underwriting Platform  
> **Status:** Design Phase  
> **Stack:** FastAPI · PostgreSQL · Hatchet · React + Vite · Claude AI  

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack & Rationale](#2-tech-stack--rationale)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Data Models (Full Schema)](#4-data-models-full-schema)
5. [Extensible Policy Rule Engine](#5-extensible-policy-rule-engine)
6. [Hatchet Workflow Design](#6-hatchet-workflow-design)
7. [Fit Score Algorithm](#7-fit-score-algorithm)
8. [API Specification](#8-api-specification)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Adding a New Lender — Workflow](#10-adding-a-new-lender--workflow)
11. [PDF Ingestion Pipeline](#11-pdf-ingestion-pipeline)
12. [Docker Compose Environment](#12-docker-compose-environment)
13. [Implementation Phases](#13-implementation-phases)

---

## 1. System Overview

A multi-lender underwriting engine that evaluates equipment finance loan applications against each lender's credit policies in parallel, ranks eligible lenders by fit score, and explains every decision at the individual criteria level.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                       │
│                                                                        │
│  /applications/new  →  Multi-step loan application form               │
│  /applications      →  Application list with status badges            │
│  /applications/:id  →  Detail view + trigger underwriting             │
│  /applications/:id/results  →  Ranked lender matches + criteria view  │
│  /lenders           →  Policy manager (view / edit / add / PDF)       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  REST API  (JSON over HTTP)
┌───────────────────────────────▼──────────────────────────────────────┐
│                         BACKEND (FastAPI)                             │
│                                                                        │
│   /api/v1/applications   ──►  CRUD for loan applications              │
│   /api/v1/lenders        ──►  Lender + program + rule management      │
│   /api/v1/underwriting   ──►  Trigger run / poll status               │
│   /api/v1/results        ──►  Match results + criteria breakdown       │
│   /api/v1/reference      ──►  Enums: rule types, industries, equip    │
│                                                                        │
│              ┌─────────────────────────────────┐                      │
│              │       HATCHET WORKFLOW ENGINE    │                      │
│              │  validate → derive → [parallel  │                      │
│              │  lender evals] → aggregate →     │                      │
│              │  persist                         │                      │
│              └──────────────┬──────────────────┘                      │
│                             │                                          │
│              ┌──────────────▼──────────────────┐                      │
│              │        MATCHING ENGINE           │                      │
│              │  RuleEvaluatorRegistry           │                      │
│              │  ├── CreditRuleEvaluators        │                      │
│              │  ├── BusinessRuleEvaluators      │                      │
│              │  ├── EquipmentRuleEvaluators     │                      │
│              │  └── GeographicRuleEvaluators    │                      │
│              │  FitScorer (0–100)               │                      │
│              └──────────────────────────────────┘                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  SQLAlchemy async ORM
┌───────────────────────────────▼──────────────────────────────────────┐
│                       PostgreSQL 15                                    │
│                                                                        │
│  applications   lenders   lender_programs   policy_rules              │
│  underwriting_runs   lender_match_results   criteria_check_results    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack & Rationale

| Layer | Technology | Why |
|---|---|---|
| **Backend API** | FastAPI (Python 3.11+) | Async-native, auto OpenAPI docs, natural fit with Hatchet's async Python SDK |
| **ORM** | SQLAlchemy 2.0 (async) | Full async support, JSONB for flexible rule params, mature ecosystem |
| **Migrations** | Alembic | Auto-generates from SQLAlchemy models, reversible |
| **Database** | PostgreSQL 15 | JSONB columns for rule parameters, ACID guarantees for financial data |
| **Workflow Engine** | Hatchet (Python SDK, Lite self-hosted) | DAG-native parallelism, durable retries, built-in dashboard, MIT licensed |
| **PDF Parsing** | pdfplumber + Claude API | Reliable text extraction + LLM-powered structured policy extraction |
| **Frontend** | React 18 + Vite + TypeScript | Fast SPA, familiar ecosystem, excellent DX |
| **UI Components** | Tailwind CSS + shadcn/ui | Accessible, composable, consistent design system |
| **HTTP Client** | TanStack Query (React Query) | Caching, background refetch, optimistic updates for polling |
| **Dev Environment** | Docker Compose | Single `docker compose up` for all services |

---

## 3. Project Directory Structure

```
d:\Testing\Kaaj\
│
├── docker-compose.yml                # Full dev environment (postgres + hatchet + backend + frontend)
├── .env.example                      # All required environment variables documented
├── .env                              # Local overrides (gitignored)
├── README.md
├── ARCHITECTURE.md                   # This file
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   │
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 001_initial_schema.py
│   │       └── 002_seed_lenders.py
│   │
│   ├── seed_data/
│   │   └── lenders.json              # Structured lender policies from PDFs
│   │
│   └── app/
│       ├── main.py                   # FastAPI app factory, lifespan, CORS
│       │
│       ├── core/
│       │   ├── config.py             # Pydantic Settings (reads .env)
│       │   └── database.py           # Async SQLAlchemy engine + session factory
│       │
│       ├── models/                   # SQLAlchemy ORM table definitions
│       │   ├── __init__.py
│       │   ├── application.py        # Business, PersonalGuarantor, BusinessCredit, LoanRequest, Application
│       │   ├── lender.py             # Lender, LenderProgram, PolicyRule
│       │   └── result.py             # UnderwritingRun, LenderMatchResult, CriteriaCheckResult
│       │
│       ├── schemas/                  # Pydantic request/response shapes
│       │   ├── __init__.py
│       │   ├── application.py
│       │   ├── lender.py
│       │   └── result.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── router.py         # Mounts all sub-routers
│       │       ├── applications.py
│       │       ├── lenders.py
│       │       ├── underwriting.py
│       │       └── reference.py
│       │
│       ├── engine/                   # Core underwriting logic (no Hatchet dependency)
│       │   ├── __init__.py
│       │   ├── context.py            # ApplicationContext dataclass (normalised view of application)
│       │   ├── rules/
│       │   │   ├── __init__.py
│       │   │   ├── base.py           # BaseRuleEvaluator ABC + RuleResult dataclass
│       │   │   ├── registry.py       # RuleEvaluatorRegistry (auto-discovery)
│       │   │   ├── credit.py         # FICO, PayNet, bankruptcy, judgments, tax liens
│       │   │   ├── business.py       # TIB, revenue, business type
│       │   │   ├── equipment.py      # Equipment age, type, condition
│       │   │   └── geographic.py     # State allow/deny, industry allow/deny
│       │   ├── evaluator.py          # LenderEvaluator — runs all rules for one lender
│       │   └── scorer.py             # FitScorer — computes 0-100 score from rule results
│       │
│       ├── workflows/
│       │   ├── __init__.py
│       │   ├── underwriting.py       # Hatchet DAG workflow definition
│       │   └── worker.py             # Hatchet worker entrypoint (run separately)
│       │
│       └── services/
│           ├── __init__.py
│           └── pdf_parser.py         # PDF text extraction + Claude API structured extraction
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    │
    └── src/
        ├── main.tsx
        ├── App.tsx                   # Router setup (React Router v6)
        │
        ├── lib/
        │   ├── api.ts                # Axios instance + base URL config
        │   ├── queryClient.ts        # TanStack Query client
        │   └── utils.ts              # cn(), formatCurrency(), etc.
        │
        ├── types/
        │   └── index.ts              # TypeScript interfaces matching backend schemas
        │
        ├── hooks/
        │   ├── useApplications.ts
        │   ├── useLenders.ts
        │   └── useUnderwriting.ts    # Trigger + poll for completion
        │
        ├── components/
        │   ├── ui/                   # shadcn/ui base components
        │   ├── layout/
        │   │   ├── Sidebar.tsx
        │   │   └── TopBar.tsx
        │   ├── forms/
        │   │   ├── ApplicationForm/
        │   │   │   ├── index.tsx     # Multi-step form shell
        │   │   │   ├── Step1Business.tsx
        │   │   │   ├── Step2Guarantor.tsx
        │   │   │   ├── Step3BusinessCredit.tsx
        │   │   │   ├── Step4LoanRequest.tsx
        │   │   │   └── Step5Review.tsx
        │   │   └── RuleEditor/
        │   │       ├── index.tsx     # Rule type dropdown + dynamic param inputs
        │   │       └── paramForms/   # One component per rule type's params
        │   ├── results/
        │   │   ├── MatchResultsView.tsx   # Eligible/ineligible columns
        │   │   ├── LenderMatchCard.tsx    # Score badge + program name
        │   │   └── CriteriaBreakdown.tsx  # Per-rule pass/fail with values
        │   └── lender-policy/
        │       ├── LenderCard.tsx
        │       ├── ProgramList.tsx
        │       ├── RulesTable.tsx
        │       └── PdfUploadModal.tsx
        │
        └── pages/
            ├── Dashboard.tsx
            ├── ApplicationList.tsx
            ├── ApplicationNew.tsx
            ├── ApplicationDetail.tsx
            ├── ApplicationResults.tsx
            └── LenderManager.tsx
```

---

## 4. Data Models (Full Schema)

### 4.1 Application Side

```sql
-- Business / Borrower
CREATE TABLE businesses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name   TEXT NOT NULL,
    ein             TEXT,                          -- Tax ID (XX-XXXXXXX)
    state           CHAR(2) NOT NULL,              -- e.g. "CA"
    city            TEXT,
    naics_code      TEXT,                          -- 6-digit NAICS
    industry_desc   TEXT,
    business_type   TEXT NOT NULL,                 -- LLC | S-Corp | C-Corp | Sole-Prop | Partnership
    founding_date   DATE,
    years_in_biz    NUMERIC(5,2),                  -- derived: can be entered directly or from founding_date
    annual_revenue  NUMERIC(15,2),
    monthly_revenue NUMERIC(15,2),
    employee_count  INTEGER,
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- Personal Guarantor
CREATE TABLE personal_guarantors (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name              TEXT NOT NULL,
    last_name               TEXT NOT NULL,
    ssn_last4               CHAR(4),
    fico_score              SMALLINT NOT NULL,     -- 300–850
    has_bankruptcy          BOOLEAN DEFAULT FALSE,
    bankruptcy_discharge_dt DATE,                  -- NULL if no bankruptcy
    bankruptcy_chapter      SMALLINT,              -- 7 or 13
    has_judgments           BOOLEAN DEFAULT FALSE,
    has_tax_liens           BOOLEAN DEFAULT FALSE,
    ownership_pct           NUMERIC(5,2),          -- 0.00–100.00
    created_at              TIMESTAMPTZ DEFAULT now()
);

-- Business Credit Profile
CREATE TABLE business_credits (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paynet_score          SMALLINT,                -- 500–800, NULL if no history
    duns_paydex           SMALLINT,                -- 0–100
    experian_intelliscore SMALLINT,                -- 0–100
    trade_line_count      SMALLINT DEFAULT 0,
    derogatory_count      SMALLINT DEFAULT 0,
    highest_delq_days     SMALLINT DEFAULT 0,      -- worst delinquency in days
    created_at            TIMESTAMPTZ DEFAULT now()
);

-- Loan Request
CREATE TABLE loan_requests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_amount    NUMERIC(15,2) NOT NULL,
    requested_term_mo   SMALLINT NOT NULL,          -- months
    purpose             TEXT,                       -- purchase | refinance | sale-leaseback
    equipment_type      TEXT NOT NULL,              -- truck | trailer | construction | medical | etc.
    equipment_year      SMALLINT,
    equipment_make      TEXT,
    equipment_model     TEXT,
    equipment_condition TEXT DEFAULT 'used',        -- new | used | refurbished
    equipment_value     NUMERIC(15,2),              -- appraised / purchase price
    equipment_age       SMALLINT,                   -- DERIVED: current_year - equipment_year
    created_at          TIMESTAMPTZ DEFAULT now()
);

-- Application (joins all the above)
CREATE TABLE applications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status              TEXT DEFAULT 'draft',       -- draft | submitted | under_review | completed | withdrawn
    business_id         UUID REFERENCES businesses(id),
    guarantor_id        UUID REFERENCES personal_guarantors(id),
    business_credit_id  UUID REFERENCES business_credits(id),
    loan_request_id     UUID REFERENCES loan_requests(id),
    submitted_at        TIMESTAMPTZ,
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
```

### 4.2 Lender Policy Side

```sql
-- Lender
CREATE TABLE lenders (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    slug          TEXT UNIQUE NOT NULL,             -- url-safe identifier
    contact_email TEXT,
    website       TEXT,
    is_active     BOOLEAN DEFAULT TRUE,
    notes         TEXT,
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- Lender Program / Tier
-- A lender may have multiple programs (e.g. "Prime A", "Standard B", "Startup C")
-- An application matches the highest-priority eligible program for that lender
CREATE TABLE lender_programs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lender_id   UUID NOT NULL REFERENCES lenders(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,                      -- e.g. "Tier A — Prime"
    description TEXT,
    priority    SMALLINT DEFAULT 100,               -- lower = tried first
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Policy Rule
-- Each rule belongs to a program. A failed HARD rule = lender ineligible.
-- Soft rules reduce the fit score but don't block eligibility.
CREATE TABLE policy_rules (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id       UUID NOT NULL REFERENCES lender_programs(id) ON DELETE CASCADE,
    rule_type        TEXT NOT NULL,                 -- enum: see Section 5
    parameters       JSONB NOT NULL DEFAULT '{}',  -- rule-specific config
    is_hard_req      BOOLEAN DEFAULT TRUE,          -- hard = blocks eligibility
    weight           NUMERIC(4,3) DEFAULT 1.0,      -- contribution to fit score (0.0–1.0)
    display_label    TEXT,                          -- human readable: "Minimum FICO Score"
    failure_msg_tmpl TEXT,                          -- "Required >= {min}, got {actual}"
    sort_order       SMALLINT DEFAULT 100,
    created_at       TIMESTAMPTZ DEFAULT now()
);
```

### 4.3 Results Side

```sql
-- One run per underwriting trigger
CREATE TABLE underwriting_runs (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id        UUID NOT NULL REFERENCES applications(id),
    hatchet_workflow_id   TEXT,                     -- Hatchet's external run ID
    status                TEXT DEFAULT 'pending',   -- pending | running | completed | failed
    error_message         TEXT,
    started_at            TIMESTAMPTZ,
    completed_at          TIMESTAMPTZ,
    created_at            TIMESTAMPTZ DEFAULT now()
);

-- One row per lender per run
CREATE TABLE lender_match_results (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID NOT NULL REFERENCES underwriting_runs(id) ON DELETE CASCADE,
    lender_id       UUID NOT NULL REFERENCES lenders(id),
    program_id      UUID REFERENCES lender_programs(id),  -- NULL if ineligible
    is_eligible     BOOLEAN NOT NULL,
    fit_score       NUMERIC(5,2),                  -- 0.00–100.00
    rank            SMALLINT,                      -- 1 = best match
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- One row per policy rule per lender match
CREATE TABLE criteria_check_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_result_id     UUID NOT NULL REFERENCES lender_match_results(id) ON DELETE CASCADE,
    rule_id             UUID NOT NULL REFERENCES policy_rules(id),
    passed              BOOLEAN NOT NULL,
    actual_value        TEXT,                      -- what the application had
    required_value      TEXT,                      -- what the rule required
    display_message     TEXT,                      -- human-readable explanation
    score_contribution  NUMERIC(5,2) DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT now()
);
```

---

## 5. Extensible Policy Rule Engine

### 5.1 Rule Type Enum & JSONB Parameter Contracts

Each `rule_type` string maps to a Python evaluator class and has a defined JSONB parameter schema:

```python
class RuleType(str, Enum):
    # ── Credit ──────────────────────────────────────────────────
    FICO_MIN             = "fico_min"       # {"min": 650}
    FICO_MAX             = "fico_max"       # {"max": 800}
    PAYNET_MIN           = "paynet_min"     # {"min": 650}
    PAYNET_REQUIRED      = "paynet_req"     # {}  ← must have any PayNet score
    NO_BANKRUPTCY        = "no_bankruptcy"  # {"discharge_years": 3}  ← 0 = never allowed
    NO_JUDGMENTS         = "no_judgments"   # {}
    NO_TAX_LIENS         = "no_tax_liens"   # {}
    MAX_DEROGATORY       = "max_derogatory" # {"count": 2}

    # ── Business ────────────────────────────────────────────────
    TIB_MIN              = "tib_min"        # {"months": 24}
    REVENUE_MIN          = "revenue_min"    # {"annual_amount": 150000}
    BUSINESS_TYPE_ALLOW  = "biz_type_allow" # {"types": ["LLC", "S-Corp"]}
    BUSINESS_TYPE_DENY   = "biz_type_deny"  # {"types": ["Sole-Prop"]}

    # ── Loan ────────────────────────────────────────────────────
    LOAN_AMOUNT_MIN      = "loan_min"       # {"amount": 10000}
    LOAN_AMOUNT_MAX      = "loan_max"       # {"amount": 500000}
    LOAN_TERM_MAX        = "term_max"       # {"months": 84}

    # ── Equipment ───────────────────────────────────────────────
    EQUIP_AGE_MAX        = "equip_age_max"  # {"years": 10}
    EQUIP_TYPE_ALLOW     = "equip_allow"    # {"types": ["truck", "trailer"]}
    EQUIP_TYPE_DENY      = "equip_deny"     # {"types": ["aircraft", "watercraft"]}
    EQUIP_COND_ALLOW     = "equip_cond"     # {"conditions": ["new", "used"]}
    EQUIP_VALUE_MIN      = "equip_val_min"  # {"amount": 5000}

    # ── Geographic ──────────────────────────────────────────────
    STATE_ALLOW          = "state_allow"    # {"states": ["CA","TX","NY",...]}
    STATE_DENY           = "state_deny"     # {"states": ["ND","SD"]}

    # ── Industry ────────────────────────────────────────────────
    INDUSTRY_ALLOW       = "industry_allow" # {"naics_prefixes": ["48","49"]}
    INDUSTRY_DENY        = "industry_deny"  # {"naics_prefixes": ["72","71","92"]}
```

### 5.2 Evaluator Class Pattern

```python
# engine/rules/base.py
@dataclass
class RuleResult:
    passed: bool
    actual_value: str          # e.g. "680"
    required_value: str        # e.g. ">= 650"
    score_contribution: float  # 0.0 if failed, rule.weight if passed
    display_message: str | None  # only set on failure

class BaseRuleEvaluator(ABC):
    rule_type: ClassVar[RuleType]   # set on each subclass

    @abstractmethod
    def evaluate(self, rule: PolicyRule, ctx: ApplicationContext) -> RuleResult:
        ...
```

```python
# engine/rules/credit.py  (example)
class FicoMinEvaluator(BaseRuleEvaluator):
    rule_type = RuleType.FICO_MIN

    def evaluate(self, rule, ctx):
        min_fico = rule.parameters["min"]
        actual   = ctx.guarantor.fico_score
        passed   = actual >= min_fico
        return RuleResult(
            passed=passed,
            actual_value=str(actual),
            required_value=f">= {min_fico}",
            score_contribution=rule.weight if passed else 0.0,
            display_message=None if passed else
                f"Minimum FICO required is {min_fico}, application has {actual}",
        )
```

### 5.3 Registry — Auto-Discovery

```python
# engine/rules/registry.py
class RuleEvaluatorRegistry:
    _evaluators: dict[RuleType, BaseRuleEvaluator] = {}

    @classmethod
    def register(cls, evaluator_cls):
        cls._evaluators[evaluator_cls.rule_type] = evaluator_cls()
        return evaluator_cls

    @classmethod
    def get(cls, rule_type: RuleType) -> BaseRuleEvaluator:
        if rule_type not in cls._evaluators:
            raise ValueError(f"No evaluator registered for rule type: {rule_type}")
        return cls._evaluators[rule_type]
```

Evaluators self-register with `@RuleEvaluatorRegistry.register` decorator.

### 5.4 How to Add a New Rule Type (3 steps)

```
Step 1 — Add to enum (engine/rules/base.py):
    NEW_RULE = "new_rule"   # {"param": value}

Step 2 — Create evaluator class (in appropriate rules/*.py file):
    @RuleEvaluatorRegistry.register
    class NewRuleEvaluator(BaseRuleEvaluator):
        rule_type = RuleType.NEW_RULE
        def evaluate(self, rule, ctx): ...

Step 3 — Done. No other changes needed.
    The API /reference/rule-types endpoint auto-exposes it.
    The frontend RuleEditor auto-renders a param form for it.
```

---

## 6. Hatchet Workflow Design

### 6.1 DAG Diagram

```
UnderwritingWorkflow
│
├─ [Step 1] validate_application
│   ├── Check all required fields are present
│   ├── Validate value ranges (FICO 300-850, amounts > 0, etc.)
│   ├── retries=2, execution_timeout=30s
│   └── Raises NonRetryableException on validation failure → surfaces clear error
│
├─ [Step 2] derive_features          (parents: validate)
│   ├── Compute equipment_age = CURRENT_YEAR - equipment_year
│   ├── Compute years_in_business from founding_date if not directly supplied
│   ├── Normalize NAICS to 2-digit prefix for industry matching
│   ├── Flag: bankruptcy_within_3_years, recent_derogatory
│   └── Returns enriched ApplicationContext
│
├─ [Step 3] fetch_lender_policies    (parents: derive_features)
│   ├── Load all active lenders → programs → rules from DB
│   ├── retries=3 (DB read, must succeed)
│   └── Returns: List[LenderEvalInput]
│
├─ [Step 4] evaluate_lenders         (parents: fetch_lender_policies)
│   ├── Spawns one child workflow per lender IN PARALLEL using aio_run_many()
│   │
│   └── [Child] EvaluateLenderWorkflow(lender_id, app_context)
│       ├── For each program (sorted by priority ASC):
│       │   ├── Run all HARD rules → first failure = program ineligible
│       │   ├── If all hard rules pass → run soft rules → accumulate score
│       │   └── Track CriteriaCheckResult per rule
│       ├── Best program = highest-scoring eligible program
│       ├── retries=3, backoff_factor=2.0, backoff_max_seconds=30s
│       └── Returns: LenderEvalOutput
│
├─ [Step 5] aggregate_results        (parents: evaluate_lenders)
│   ├── Collect all child outputs
│   ├── Sort eligible lenders by fit_score DESC → assign rank
│   └── Build final UnderwritingResult payload
│
└─ [Step 6] persist_results          (parents: aggregate_results)
    ├── Write UnderwritingRun (status=completed)
    ├── Write LenderMatchResult per lender
    ├── Write CriteriaCheckResult per rule per lender
    └── retries=5 (DB write is critical, must not lose results)

On-Failure Task (runs if any step above fails):
    └── Mark UnderwritingRun status=failed, store error_message
```

### 6.2 Key Hatchet Features Used

| Feature | Where Used |
|---|---|
| **DAG with `parents=`** | Steps 1–6 chain as a directed acyclic graph |
| **`aio_run_many()`** | Fan-out: all lenders evaluated in true parallel |
| **`retries=N`** | Every step has retries; DB writes have highest (5) |
| **`backoff_factor=2.0`** | Lender eval retries use exponential backoff |
| **`NonRetryableException`** | Validation failures don't retry (wrong input, not transient) |
| **`@workflow.on_failure_task()`** | Guarantees run is marked failed even if all steps crash |
| **`execution_timeout`** | Each step has a timeout to prevent hangs |
| **`ctx.retry_count`** | Logged for observability |

---

## 7. Fit Score Algorithm (0–100)

```
For each lender, for each program (ordered by priority):

  Phase 1 — Hard Gate
  ─────────────────────
  For each rule where is_hard_req = TRUE:
    result = evaluator.evaluate(rule, app_context)
    if NOT result.passed:
      → program is INELIGIBLE
      → record failure reason
      → move to next program

  Phase 2 — Soft Scoring (only if all hard rules passed)
  ──────────────────────────────────────────────────────
  total_weight   = sum(rule.weight for all active rules)
  passed_weight  = sum(rule.weight for passed rules)
  base_score     = (passed_weight / total_weight) * 85   # cap base at 85

  Phase 3 — Bonus Points (up to +15)
  ──────────────────────────────────
  +5  if FICO >= program's "excellent" threshold  (e.g. >= 720)
  +5  if PayNet score >= 700
  +3  if years_in_business >= 5
  +2  if no derogatory marks at all

  Final Score = min(100, base_score + bonuses)

  Lender's score = score of its best-matching (highest-scoring) eligible program

Ranking:
  All eligible lenders sorted by fit_score DESC → rank 1, 2, 3...
  Ineligible lenders listed after, sorted by "near miss" score
  (how many hard rules they failed and by how much)
```

---

## 8. API Specification

### 8.1 Applications

```
POST   /api/v1/applications
       Body: CreateApplicationRequest (nested: business, guarantor, business_credit, loan_request)
       Returns: ApplicationResponse (with generated ID)

GET    /api/v1/applications?page=1&size=20&status=submitted
       Returns: PaginatedResponse[ApplicationSummary]

GET    /api/v1/applications/{id}
       Returns: ApplicationDetailResponse (full nested, latest run summary)

PATCH  /api/v1/applications/{id}
       Body: UpdateApplicationRequest (partial)
       Returns: ApplicationDetailResponse

DELETE /api/v1/applications/{id}
       Returns: 204 No Content
```

### 8.2 Underwriting

```
POST   /api/v1/applications/{id}/underwrite
       Triggers Hatchet workflow, creates UnderwritingRun record
       Returns: { run_id, status: "pending", hatchet_workflow_id }

GET    /api/v1/applications/{id}/runs
       Returns: List[UnderwritingRunSummary]

GET    /api/v1/underwriting-runs/{run_id}
       Returns: UnderwritingRunDetail { status, completed_at, match_results[] }
       (Frontend polls this every 2s until status = completed | failed)
```

### 8.3 Lenders

```
GET    /api/v1/lenders
       Returns: List[LenderSummary] (with program count, active status)

POST   /api/v1/lenders
       Body: CreateLenderRequest
       Returns: LenderDetailResponse

GET    /api/v1/lenders/{id}
       Returns: LenderDetailResponse (with programs and rules nested)

PATCH  /api/v1/lenders/{id}
       Body: UpdateLenderRequest
       Returns: LenderDetailResponse

DELETE /api/v1/lenders/{id}
       Returns: 204 No Content

POST   /api/v1/lenders/{id}/programs
       Body: CreateProgramRequest
       Returns: ProgramResponse

PATCH  /api/v1/lenders/{id}/programs/{pid}
       Returns: ProgramResponse

DELETE /api/v1/lenders/{id}/programs/{pid}
       Returns: 204 No Content

POST   /api/v1/programs/{pid}/rules
       Body: CreateRuleRequest { rule_type, parameters, is_hard_req, weight, display_label }
       Returns: PolicyRuleResponse

PATCH  /api/v1/programs/{pid}/rules/{rid}
       Body: UpdateRuleRequest (partial)
       Returns: PolicyRuleResponse

DELETE /api/v1/programs/{pid}/rules/{rid}
       Returns: 204 No Content
```

### 8.4 PDF Ingestion

```
POST   /api/v1/lenders/import-pdf
       Body: multipart/form-data { file: PDF }
       → Extracts text with pdfplumber
       → Sends to Claude API with extraction prompt
       Returns: ParsedLenderPreview { lender_name, programs[], rules[] }
       (Admin reviews this before committing)

POST   /api/v1/lenders/import-pdf/confirm
       Body: ParsedLenderPreview (edited by admin if needed)
       → Creates Lender + Programs + Rules in DB
       Returns: LenderDetailResponse
```

### 8.5 Reference Data

```
GET    /api/v1/reference/rule-types
       Returns: List[{ type, label, param_schema }]
       (Drives the frontend rule editor dropdown + dynamic forms)

GET    /api/v1/reference/equipment-types
       Returns: List[str]

GET    /api/v1/reference/states
       Returns: List[{ code, name }]

GET    /api/v1/reference/naics-codes?q=truck
       Returns: List[{ code, description }]
```

---

## 9. Frontend Architecture

### 9.1 Pages

| Route | Component | Description |
|---|---|---|
| `/` | `Dashboard` | Stats: active lenders, pending apps, recent runs |
| `/applications` | `ApplicationList` | Paginated table with status filter + "New Application" button |
| `/applications/new` | `ApplicationNew` | 5-step form with progress indicator |
| `/applications/:id` | `ApplicationDetail` | All application fields + run history + "Run Underwriting" button |
| `/applications/:id/results` | `ApplicationResults` | Match results + criteria breakdown |
| `/lenders` | `LenderManager` | Grid of lender cards + "Add Lender" / "Import PDF" |
| `/lenders/:id` | `LenderDetail` | Programs accordion + rules table with inline edit |

### 9.2 Multi-Step Application Form

```
Step 1 — Business Information
  ├── Business Name *
  ├── EIN (Tax ID)
  ├── State *          (dropdown: all US states)
  ├── City
  ├── Industry         (NAICS code search)
  ├── Business Type *  (LLC / S-Corp / C-Corp / Sole Prop / Partnership)
  ├── Years in Business OR Founding Date *
  ├── Annual Revenue *
  └── Employee Count

Step 2 — Personal Guarantor
  ├── First Name *, Last Name *
  ├── FICO Score *     (300–850 numeric input)
  ├── Has Bankruptcy?  (toggle)
  │   └── [if yes] Discharge Date, Chapter (7 or 13)
  ├── Has Judgments?   (toggle)
  └── Has Tax Liens?   (toggle)

Step 3 — Business Credit
  ├── PayNet MasterScore  (500–800, or "No Score")
  ├── D&B Paydex          (0–100)
  ├── Experian Intelliscore (0–100)
  ├── Number of Trade Lines
  ├── Derogatory Marks Count
  └── Worst Delinquency (days)

Step 4 — Loan Request
  ├── Requested Amount *    ($)
  ├── Requested Term *      (months dropdown: 12/24/36/48/60/72/84)
  ├── Purpose               (Purchase / Refinance / Sale-Leaseback)
  ├── Equipment Type *      (dropdown from /reference/equipment-types)
  ├── Equipment Year *
  ├── Make & Model
  ├── Condition *           (New / Used / Refurbished)
  └── Equipment Value / Purchase Price

Step 5 — Review & Submit
  └── Read-only summary of all fields, confirm + submit
```

### 9.3 Match Results View

```
┌─────────────────────────────────────────────────────────────────┐
│  Underwriting Results for: Acme Trucking — $85,000 truck loan   │
│  Run completed: May 27 2026 at 14:32                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ✅ ELIGIBLE LENDERS (3)                                          │
│  ────────────────────────────────────────────────────────────── │
│  #1  First Western Equipment Finance         Score: 91/100      │
│      Program: Tier A — Prime                                     │
│      [View Criteria ▼]                                           │
│        ✅ FICO Score        Required ≥ 650    Actual: 720   +8pts│
│        ✅ Time in Business  Required ≥ 24mo   Actual: 36mo  +6pts│
│        ✅ Loan Amount       $10K–$500K        Actual: $85K  +5pts│
│        ✅ Equipment Age     Required ≤ 10yr   Actual: 3yr   +5pts│
│        ✅ State Eligible    All states        CA ✓         +3pts │
│        ⚠️  PayNet Score     Preferred ≥ 650   No score    -2pts  │
│                                                                   │
│  #2  Amur Equipment Finance                  Score: 78/100      │
│      Program: Standard — B Tier                                   │
│      [View Criteria ▼]                                           │
│        ...                                                        │
│                                                                   │
│  ❌ INELIGIBLE LENDERS (2)                                        │
│  ────────────────────────────────────────────────────────────── │
│  ✗   Stearns Bank Equipment Finance                              │
│      [View Criteria ▼]                                           │
│        ❌ Time in Business  Required ≥ 24mo   Actual: 36mo  ✓   │
│        ❌ FICO Score        Required ≥ 700    Actual: 720   ✓   │
│        ❌ Loan Amount Min   Required ≥ $100K  Actual: $85K  ✗ ← FAIL │
│           "Minimum loan amount is $100,000; application requests $85,000" │
└─────────────────────────────────────────────────────────────────┘
```

### 9.4 Lender Policy Manager

```
┌─────────────────────────────────────────────────────────────────┐
│  Lender Policies                         [+ Add Lender] [📄 PDF]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────┐                         │
│  │ First Western Equipment Finance     │                         │
│  │ 3 programs  |  Active  [Edit] [Del] │                         │
│  │                                     │                         │
│  │ ▼ Tier A — Prime (Priority 1)       │                         │
│  │   Rule                Type    Hard  Weight  Actions           │
│  │   Min FICO 650        fico_min  ✓   1.0    [Edit][Del]       │
│  │   Min TIB 24mo        tib_min   ✓   1.0    [Edit][Del]       │
│  │   Loan $10K–$500K     loan_min  ✓   1.0    [Edit][Del]       │
│  │   PayNet Preferred    paynet_min ✗  0.5    [Edit][Del]       │
│  │   [+ Add Rule]                                                │
│  │                                     │                         │
│  │ ▶ Standard B Tier (Priority 2)      │                         │
│  │ ▶ Startup Program (Priority 3)      │                         │
│  │ [+ Add Program]                     │                         │
│  └─────────────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Adding a New Lender — Workflow

### Option A: PDF Upload (Recommended)
```
1. Admin clicks "Import PDF" on /lenders page
2. Uploads PDF file
3. Backend: pdfplumber extracts raw text
4. Backend: Claude API call with structured extraction prompt:
   "Extract all credit policy criteria from this lender guideline document
    and return as JSON with programs, FICO thresholds, TIB requirements,
    loan amounts, equipment restrictions, geographic limits, etc."
5. Returns ParsedLenderPreview for admin to review in UI
6. Admin can edit any extracted values before confirming
7. Confirm → backend creates Lender + Programs + Rules in DB
8. New lender is immediately available for future underwriting runs
```

### Option B: Manual Entry (UI)
```
1. Click "+ Add Lender" → fill name, contact info
2. Click "+ Add Program" → fill program name, priority
3. Click "+ Add Rule" → dropdown shows all RuleType options
4. Each rule type dynamically shows the right input fields:
   - fico_min   → "Minimum FICO Score" (number input, 300–850)
   - tib_min    → "Months in Business" (number input)
   - state_deny → "Excluded States" (multi-select US states)
   - etc.
5. Toggle "Hard Requirement" + set Weight
6. Save — active immediately
```

### Option C: API (for automated ingestion)
```
POST /api/v1/lenders with full nested JSON payload
```

---

## 11. PDF Ingestion Pipeline

```python
# services/pdf_parser.py

class LenderPdfParser:
    def __init__(self, anthropic_client):
        self.client = anthropic_client

    async def parse(self, pdf_bytes: bytes) -> ParsedLenderPreview:
        # Step 1: Extract text
        text = self._extract_text(pdf_bytes)   # pdfplumber

        # Step 2: Send to Claude for structured extraction
        response = await self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=EXTRACTION_SYSTEM_PROMPT,   # see below
            messages=[{
                "role": "user",
                "content": f"Extract credit policy criteria from this document:\n\n{text}"
            }]
        )

        # Step 3: Parse JSON response → ParsedLenderPreview
        return self._parse_response(response.content[0].text)

EXTRACTION_SYSTEM_PROMPT = """
You are a financial document parser. Extract lender credit policy criteria and return
valid JSON matching this schema:
{
  "lender_name": "string",
  "programs": [{
    "name": "string",
    "priority": 1,
    "rules": [{
      "rule_type": "fico_min|tib_min|loan_min|...",  // from the RuleType enum
      "parameters": {},
      "is_hard_req": true,
      "weight": 1.0,
      "display_label": "string"
    }]
  }]
}
Extract: FICO minimums, time-in-business requirements, loan amount ranges,
equipment age limits, equipment type restrictions, state restrictions,
industry exclusions, PayNet/business credit requirements, bankruptcy policies.
"""
```

---

## 12. Docker Compose Environment

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kaaj
      POSTGRES_USER: kaaj
      POSTGRES_PASSWORD: kaaj_dev
    ports: ["5432:5432"]

  hatchet-lite:
    image: ghcr.io/hatchet-dev/hatchet/hatchet-lite:latest
    environment:
      DATABASE_URL: postgresql://kaaj:kaaj_dev@postgres:5432/hatchet
      SERVER_URL: http://localhost:8888
      SERVER_GRPC_BROADCAST_ADDRESS: localhost:7077
      SERVER_AUTH_COOKIE_INSECURE: "t"
      SERVER_GRPC_INSECURE: "t"
    ports:
      - "8888:8888"   # Hatchet dashboard
      - "7077:7077"   # gRPC for SDK
    depends_on: [postgres]

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://kaaj:kaaj_dev@postgres:5432/kaaj
      HATCHET_CLIENT_TOKEN: ${HATCHET_CLIENT_TOKEN}  # generated after first run
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports: ["8000:8000"]
    depends_on: [postgres, hatchet-lite]

  worker:
    build: ./backend
    command: python -m app.workflows.worker
    environment:
      DATABASE_URL: postgresql+asyncpg://kaaj:kaaj_dev@postgres:5432/kaaj
      HATCHET_CLIENT_TOKEN: ${HATCHET_CLIENT_TOKEN}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on: [postgres, hatchet-lite]

  frontend:
    build: ./frontend
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports: ["5173:5173"]
    depends_on: [backend]
```

> **First-run note:** After starting, visit `http://localhost:8888`, log in with `admin@example.com / Admin123!!`, create a tenant, generate an API token, and add it to `.env` as `HATCHET_CLIENT_TOKEN=...`.

---

## 13. Implementation Phases

### Phase 1 — Foundation
- [ ] Docker Compose + environment setup
- [ ] Backend: FastAPI app, config, database connection
- [ ] SQLAlchemy models + Alembic initial migration
- [ ] Seed data: 5 lenders from PDF documents

### Phase 2 — Core Engine
- [ ] Rule type enum + BaseRuleEvaluator + Registry
- [ ] All rule evaluator classes (credit, business, equipment, geographic)
- [ ] FitScorer algorithm
- [ ] LenderEvaluator orchestrator (runs all programs for one lender)
- [ ] ApplicationContext builder (from Application ORM → context dataclass)

### Phase 3 — Hatchet Workflow
- [ ] Hatchet workflow DAG definition
- [ ] Child workflow for lender evaluation (fan-out)
- [ ] On-failure task
- [ ] Worker entrypoint

### Phase 4 — API Layer
- [ ] Applications CRUD
- [ ] Lender + Program + Rule CRUD
- [ ] Underwriting trigger + status endpoints
- [ ] Results retrieval
- [ ] Reference data endpoints
- [ ] PDF import endpoints

### Phase 5 — Frontend
- [ ] Vite + React + TypeScript + Tailwind setup
- [ ] API client + TanStack Query hooks
- [ ] Multi-step application form
- [ ] Application list + detail pages
- [ ] Match results view with criteria breakdown
- [ ] Lender policy manager with inline rule editor
- [ ] PDF upload modal

### Phase 6 — Polish
- [ ] Error states + loading skeletons
- [ ] Form validation (Zod)
- [ ] Pagination
- [ ] Toast notifications
- [ ] README with setup instructions

---

## Key Design Principles

1. **Extensibility first** — Adding a rule type requires touching only 2 files (enum + evaluator). Adding a lender requires no code changes.
2. **Transparency** — Every eligibility decision is explained at rule level with actual vs. required values.
3. **Durability** — Hatchet persists every workflow step. If the worker crashes mid-run, it resumes from the last completed step.
4. **Parallelism** — All lenders are evaluated simultaneously using Hatchet's `aio_run_many()` fan-out, not sequentially.
5. **Separation of concerns** — The matching engine (`engine/`) has zero Hatchet dependency and can be unit-tested in isolation.

---

*Document generated: May 2026 | Ready to implement — waiting for lender PDFs to seed policies*
