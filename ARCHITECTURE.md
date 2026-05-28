# Kaaj — Equipment Finance Underwriting Platform: Architecture

> **Status:** Implemented  
> **Stack:** FastAPI · PostgreSQL · Hatchet (optional) · React + Vite · Claude AI

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack & Rationale](#2-tech-stack--rationale)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Data Models](#4-data-models)
5. [Rule Engine](#5-rule-engine)
6. [Fit Score Algorithm](#6-fit-score-algorithm)
7. [Underwriting Workflow](#7-underwriting-workflow)
8. [API Reference](#8-api-reference)
9. [Frontend Architecture](#9-frontend-architecture)
10. [PDF Ingestion Pipeline](#10-pdf-ingestion-pipeline)
11. [Docker Compose Environment](#11-docker-compose-environment)

---

## 1. System Overview

A multi-lender underwriting engine that evaluates equipment finance loan applications against each lender's credit policies, ranks eligible lenders by fit score, and explains every decision at the individual rule level.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React + Vite)                       │
│                                                                        │
│  /                      Dashboard — stats overview                    │
│  /applications          Application list with status badges           │
│  /applications/new      5-step application wizard                     │
│  /applications/:id      Detail view + Run Underwriting button         │
│  /underwriting/:runId   Ranked lender matches + criteria table        │
│  /lenders               Lender list with PDF import                   │
│  /lenders/:id           Programs + rules editor                       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  REST API  /api/v1
┌───────────────────────────────▼──────────────────────────────────────┐
│                         BACKEND (FastAPI)                             │
│                                                                        │
│   /applications    CRUD + list with business summary                  │
│   /lenders         Lender + program + rule management (14 endpoints)  │
│   /underwriting    Trigger run / poll status                          │
│   /reference       Enums: rule types, equipment types, states         │
│   /parse-policy    PDF upload → Claude parse → confirm import         │
│                                                                        │
│              ┌─────────────────────────────────┐                      │
│              │       UNDERWRITING PIPELINE     │                      │
│              │  validate → derive → fetch →    │                      │
│              │  evaluate → persist             │                      │
│              │  (Hatchet DAG or sync fallback) │                      │
│              └──────────────┬──────────────────┘                      │
│                             │                                          │
│              ┌──────────────▼──────────────────┐                      │
│              │        RULE ENGINE              │                      │
│              │  RuleEvaluatorRegistry          │                      │
│              │  ├── 6 Credit evaluators        │                      │
│              │  ├── 7 Business evaluators      │                      │
│              │  ├── 7 Equipment evaluators     │                      │
│              │  └── 6 Geographic evaluators    │                      │
│              │  FitScorer (0–100)              │                      │
│              └──────────────────────────────────┘                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │  SQLAlchemy 2.0 async ORM
┌───────────────────────────────▼──────────────────────────────────────┐
│                       PostgreSQL 15                                    │
│                                                                        │
│  lenders   lender_programs   eligibility_rules                        │
│  applications   businesses   personal_guarantors                      │
│  business_credits   loan_requests                                     │
│  underwriting_runs   criteria_check_results   (11 tables total)       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tech Stack & Rationale

| Layer | Technology | Why |
|---|---|---|
| **Backend API** | FastAPI 0.115 (Python 3.11+) | Async-native, auto OpenAPI docs |
| **ORM** | SQLAlchemy 2.0 (async) | Full async support, JSONB for rule params |
| **Migrations** | Alembic | Auto-generates from models, reversible |
| **Database** | PostgreSQL 15 | JSONB columns, ACID guarantees for financial data |
| **Workflow Engine** | Hatchet SDK (optional) | DAG steps, durable retries; sync fallback runs in-process when unavailable |
| **PDF Parsing** | pdfplumber + Claude API (claude-opus-4-7) | Text extraction + LLM-powered structured extraction |
| **Frontend** | React 18 + Vite + TypeScript | Fast SPA, familiar ecosystem |
| **State / Fetching** | TanStack Query v5 | Caching, polling (2 s interval while underwriting runs) |
| **Routing** | React Router v6 | Declarative nested routes |
| **UI** | Tailwind CSS + custom component classes | Consistent design system |
| **Forms** | React Hook Form | Performant, minimal re-renders |
| **HTTP Client** | Axios | Typed API layer in `lib/api.ts` |
| **Dev Environment** | Docker Compose | Single `docker compose up --build` |

---

## 3. Project Directory Structure

```
Kaaj/
├── docker-compose.yml              # 9 services: postgres, rabbitmq, hatchet (×4), backend, worker, frontend
├── .env.example
├── README.md
├── ARCHITECTURE.md
├── DECISIONS.md                    # 10 architectural decision records
│
├── backend/
│   ├── pyproject.toml              # hatchet-sdk is an optional extra, not required
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py                  # async migrations, WindowsSelectorEventLoopPolicy on Win32
│   │   └── versions/
│   │       └── 0001_initial_schema.py
│   ├── seed_data/
│   │   └── seed.py                 # 5 lenders, programs, and 77 rules
│   └── app/
│       ├── main.py                 # FastAPI factory, CORS, lifespan → ensure_loaded()
│       ├── core/
│       │   ├── config.py           # Pydantic Settings (DATABASE_URL, ANTHROPIC_API_KEY, …)
│       │   └── database.py         # Async engine, AsyncSessionLocal, Base, get_db()
│       ├── models/
│       │   ├── lender.py           # Lender, LenderProgram, EligibilityRule
│       │   ├── application.py      # Application, Business, PersonalGuarantor, BusinessCredit, LoanRequest
│       │   └── underwriting.py     # UnderwritingRun, CriteriaCheckResult (rule_id nullable on SET NULL)
│       ├── schemas/
│       │   ├── application.py      # ApplicationSummary, ApplicationResponse, …
│       │   ├── lender.py
│       │   ├── underwriting.py
│       │   └── policy.py           # ParsedLenderPreview for PDF import
│       ├── api/v1/
│       │   ├── applications.py     # GET /applications, POST, GET /:id, guarantors, credit, loan-request
│       │   ├── lenders.py          # 14 endpoints: lender + program + rule CRUD
│       │   ├── underwriting.py     # POST /run, GET /runs/:id
│       │   ├── reference.py        # /rule-types, /equipment-types, /business-types, /states
│       │   └── parse_policy.py     # POST /upload, POST /import
│       ├── engine/
│       │   ├── rules/
│       │   │   ├── base.py         # RuleType (26 values), RULE_TYPE_META, EvalContext, EvalResult, BaseRuleEvaluator
│       │   │   ├── registry.py     # RuleEvaluatorRegistry with @register decorator
│       │   │   ├── credit.py       # 6 evaluators
│       │   │   ├── business.py     # 7 evaluators
│       │   │   ├── equipment.py    # 7 evaluators
│       │   │   └── geographic.py   # 6 evaluators
│       │   └── scorer.py           # FitScorer — base 85 + up to 15 bonus
│       ├── workflows/
│       │   ├── hatchet_client.py   # Shared Hatchet instance (only imported inside try/except)
│       │   ├── underwriting.py     # 6 step functions + _run_sync_fallback() + register_workflow()
│       │   └── worker.py           # Hatchet worker entrypoint (optional, run separately)
│       └── tests/
│           ├── conftest.py         # make_ctx() helper
│           ├── test_credit_rules.py
│           ├── test_business_rules.py
│           ├── test_equipment_rules.py
│           ├── test_geographic_rules.py
│           └── test_scorer.py
│
└── frontend/
    ├── vite.config.ts              # proxy /api/v1 → http://localhost:8000
    └── src/
        ├── App.tsx                 # Routes: /, /applications, /applications/new, /applications/:id, /underwriting/:runId, /lenders, /lenders/:id
        ├── types/index.ts          # All TypeScript interfaces (IDs are string, not number)
        ├── lib/api.ts              # Axios client + all API functions
        ├── hooks/
        │   ├── useApplications.ts  # useApplicationsList, useApplication, mutations
        │   ├── useLenders.ts
        │   ├── useUnderwriting.ts  # useTriggerUnderwriting, useUnderwritingRun (2 s poll)
        │   ├── usePolicy.ts
        │   └── useReference.ts
        ├── pages/
        │   ├── Dashboard.tsx
        │   ├── ApplicationList.tsx
        │   ├── ApplicationWizard.tsx
        │   ├── ApplicationDetail.tsx
        │   ├── UnderwritingResults.tsx
        │   ├── LenderList.tsx
        │   └── LenderDetail.tsx
        └── components/
            ├── layout/Sidebar.tsx, Layout.tsx
            ├── wizard/Step1Business.tsx … Step5Review.tsx
            └── lender-policy/
                ├── RuleFormModal.tsx   # ParamField renders by param_schema type
                ├── PdfUploadModal.tsx  # upload → preview → confirm import
                ├── ProgramFormModal.tsx
                ├── ProgramList.tsx
                └── RulesTable.tsx
```

---

## 4. Data Models

### 4.1 Lender Side (3 tables)

| Table | Key Columns |
|---|---|
| `lenders` | id (UUID PK), name, contact_email, contact_phone, notes, is_active |
| `lender_programs` | id, lender_id (FK cascade), name, description, min_amount, max_amount, is_active |
| `eligibility_rules` | id, program_id (FK cascade), rule_type (TEXT), label, weight (FLOAT), parameters (JSONB), is_active |

### 4.2 Application Side (5 tables)

| Table | Key Columns |
|---|---|
| `applications` | id, status (draft/submitted/underwriting/approved/declined), created_at, updated_at |
| `businesses` | id, application_id (FK), business_name, dba_name, owner_name, owner_email, state, business_type, years_in_biz, naics_code, annual_revenue, employee_count |
| `personal_guarantors` | id, application_id (FK), full_name, ssn_last4, credit_score, ownership_pct |
| `business_credits` | id, application_id (FK), fico_sbss, experian_intelliscore, duns_paydex, bankruptcies, liens, judgments, years_in_file |
| `loan_requests` | id, application_id (FK), requested_amount, requested_term_mo, equipment_type, equipment_description, equipment_year, equipment_age_yrs, equipment_condition, state_of_operation, down_payment_pct |

> `loan_requests.state_of_operation` is separate from `businesses.state`. Geographic rules use the equipment operation state; the workflow derives it from business state if not supplied.

### 4.3 Underwriting Side (2 tables)

| Table | Key Columns |
|---|---|
| `underwriting_runs` | id, application_id (FK), status (pending/running/completed/failed), started_at, completed_at, error_message, results (JSONB — full scored results snapshot) |
| `criteria_check_results` | id, run_id (FK), rule_id (FK nullable **SET NULL** — preserves audit row when rule deleted), program_id, lender_id, rule_type, rule_name, weight, passed, reason, actual_value |

---

## 5. Rule Engine

### 5.1 The 26 Rule Types

| Category | Rule Types |
|---|---|
| **Credit (6)** | `MIN_CREDIT_SCORE`, `MAX_BANKRUPTCIES`, `MIN_FICO_SBSS`, `MIN_EXPERIAN_INTELLISCORE`, `MIN_DUNS_PAYDEX`, `MAX_DEROGATORY_MARKS` |
| **Business (7)** | `MIN_YEARS_IN_BUSINESS`, `MIN_ANNUAL_REVENUE`, `ALLOWED_BUSINESS_TYPES`, `MIN_EMPLOYEE_COUNT`, `MAX_EMPLOYEE_COUNT`, `MIN_OWNERSHIP_PCT`, `NAICS_CODE_ALLOWLIST` |
| **Equipment (7)** | `ALLOWED_EQUIPMENT_TYPES`, `MAX_EQUIPMENT_AGE_YRS`, `MIN_LOAN_AMOUNT`, `MAX_LOAN_AMOUNT`, `MAX_TERM_MONTHS`, `MIN_DOWN_PAYMENT_PCT`, `ALLOWED_EQUIPMENT_CONDITIONS` |
| **Geographic (6)** | `ALLOWED_STATES`, `EXCLUDED_STATES`, `MIN_CREDIT_SCORE_BY_STATE`, `MAX_LOAN_AMOUNT_BY_STATE`, `MIN_YEARS_IN_BUSINESS_BY_STATE`, `ALLOWED_STATES_FOR_EQUIPMENT` |

`NAICS_CODE_ALLOWLIST` supports prefix matching — code `"23"` matches any application NAICS starting with `"23"`.

`ALLOWED_STATES_FOR_EQUIPMENT` uses only `state_of_operation` and skips (not fails) when it is None. Other geographic rules fall back to `business.state`.

### 5.2 Evaluator Pattern

```python
# base.py
@dataclass
class EvalContext:
    guarantors: list[dict]        # [{credit_score, ownership_pct, full_name}]
    business_type: str
    state: str                    # business registration state
    years_in_biz: float
    annual_revenue: float | None
    # ... 15 more fields

@dataclass
class EvalResult:
    passed: bool
    skipped: bool = False         # True when required data is absent
    reason: str | None = None
    actual_value: str | None = None

class BaseRuleEvaluator(ABC):
    @abstractmethod
    def evaluate(self, ctx: EvalContext, parameters: dict) -> EvalResult: ...

    def skip(self, reason: str) -> EvalResult:
        return EvalResult(passed=True, skipped=True, reason=reason)
```

### 5.3 Registry

```python
class RuleEvaluatorRegistry:
    _evaluators: dict[RuleType, BaseRuleEvaluator] = {}

    @classmethod
    def register(cls, rule_type: RuleType):
        def decorator(evaluator_cls):
            cls._evaluators[rule_type] = evaluator_cls()
            return evaluator_cls
        return decorator

    @classmethod
    def ensure_loaded(cls):
        import app.engine.rules.credit
        import app.engine.rules.business
        import app.engine.rules.equipment
        import app.engine.rules.geographic
```

### 5.4 Adding a New Rule Type (2 files)

```
1. backend/app/engine/rules/base.py
   - Add value to RuleType enum
   - Add entry to RULE_TYPE_META (label, category, param_schema)

2. backend/app/engine/rules/<category>.py
   - Add evaluator class decorated with @RuleEvaluatorRegistry.register(RuleType.NEW_RULE)

Done. The API /reference/rule-types, the frontend rule editor dropdown,
and the PDF parser prompt all pick it up automatically.
```

---

## 6. Fit Score Algorithm

```
base_score = (sum of passed rule weights / sum of non-skipped rule weights) × 85

Special cases:
  • No active rules → base_score = 85 (full base, no data to penalize)
  • All rules skipped → base_score = 85
  • Unknown rule types are silently skipped (not failed)

Bonus points (each +5, maximum +15 total):
  +5  if best guarantor credit score ≥ 750
  +5  if years_in_biz ≥ 10
  +5  if annual_revenue ≥ $1,000,000

fit_score = min(100, base_score + bonuses)
```

Skipped rules are excluded from the total weight denominator so missing data does not penalize the applicant.

---

## 7. Underwriting Workflow

### 7.1 Pipeline Steps

```
validate    — check application has business + loan_request
derive      — compute equipment_age_yrs from year; fall back state_of_operation to business.state
fetch       — load all active lenders → programs → rules from DB
evaluate    — score each program with FitScorer; sort by fit_score DESC
persist     — write UnderwritingRun(status=completed) + CriteriaCheckResult rows
```

### 7.2 Hatchet vs Sync Fallback

The workflow supports two execution paths:

| Path | When | How |
|---|---|---|
| **Hatchet DAG** | `HATCHET_CLIENT_TOKEN` is set and worker is running | `register_workflow()` in `workflows/underwriting.py`; POST /run pushes event to Hatchet |
| **Sync fallback** | Hatchet unavailable (import fails or connection error) | `asyncio.create_task(_run_sync_fallback())` runs all steps in-process; no separate worker needed |

The API endpoint tries Hatchet first inside a `try/except`. For local dev without Docker, the sync fallback runs automatically with zero configuration.

`hatchet-sdk` is an optional dependency (`pip install -e ".[hatchet]"`). The main install does not require it.

---

## 8. API Reference

All endpoints are at `/api/v1`.

### Applications

| Method | Path | Description |
|---|---|---|
| GET | `/applications` | List all applications (summary: business name, status, amount, equipment type) |
| POST | `/applications` | Step 1 — create application + business |
| GET | `/applications/{id}` | Full application detail |
| POST | `/applications/{id}/guarantors` | Step 2 — add guarantor |
| PUT | `/applications/{id}/business-credit` | Step 3 — upsert credit profile |
| PUT | `/applications/{id}/loan-request` | Step 4 — upsert loan + equipment details |

### Underwriting

| Method | Path | Description |
|---|---|---|
| POST | `/underwriting/run` | Trigger underwriting for an application |
| GET | `/underwriting/runs/{id}` | Poll status and results |

Poll until `status` is `completed` or `failed`. Frontend polls every 2 seconds.

### Lenders (14 endpoints)

| Method | Path |
|---|---|
| GET / POST | `/lenders` |
| GET / PUT / DELETE | `/lenders/{id}` |
| GET / POST | `/lenders/{id}/programs` |
| GET / PUT / DELETE | `/programs/{id}` |
| GET / POST | `/programs/{id}/rules` |
| PUT / DELETE | `/rules/{id}` |

### Reference

| Method | Path | Returns |
|---|---|---|
| GET | `/reference/rule-types` | 26 rule types with label, category, param_schema |
| GET | `/reference/equipment-types` | string list |
| GET | `/reference/business-types` | string list |
| GET | `/reference/states` | `[{code, name}]` |

### PDF Policy Import

| Method | Path | Description |
|---|---|---|
| POST | `/parse-policy/upload` | Upload PDF → Claude parses → returns `ParsedLenderPreview` |
| POST | `/parse-policy/import` | Commit a reviewed preview as lender + programs + rules |

Two-step flow: preview lets the user review and correct Claude's extraction before committing to the database.

---

## 9. Frontend Architecture

### Routes

| Route | Page | Description |
|---|---|---|
| `/` | `Dashboard` | Active lenders, recent runs, quick stats |
| `/applications` | `ApplicationList` | Table of all applications with status badges |
| `/applications/new` | `ApplicationWizard` | 5-step form with per-step API saves |
| `/applications/:id` | `ApplicationDetail` | Full detail + Run Underwriting button |
| `/underwriting/:runId` | `UnderwritingResults` | Scored program list + expandable criteria table |
| `/lenders` | `LenderList` | Grid with PDF import |
| `/lenders/:id` | `LenderDetail` | Programs accordion + rule editor |

### Data Fetching

- All server state via **TanStack Query v5**
- Underwriting run polling: `refetchInterval` returns `2000` while status is `pending` or `running`, `false` otherwise
- Mutations invalidate relevant query keys on success

### Key Component Details

**`ApplicationWizard`** — `useState` for `step` (1–5) and `applicationId`. Step 1 creates the application and captures the ID; subsequent steps PATCH sub-resources using the same ID.

**`RuleFormModal`** — `ParamField` component switches on `param_schema` string: `"integer"/"number"` → number input, `"array[string]"` → comma-separated text, other → JSON textarea. Rule type dropdown is grouped by category.

**`PdfUploadModal`** — Three-phase UI: upload → preview (editable) → confirm import.

**`UnderwritingResults`** — `ScoreBadge` colored green (≥75) / amber (≥50) / red (<50). Criteria table is collapsible per program.

---

## 10. PDF Ingestion Pipeline

```
1. User uploads PDF on /lenders page
2. pdfplumber extracts raw text (page by page)
3. Text truncated to 12,000 chars if needed
4. Claude API call (claude-opus-4-7, max_tokens=8192):
   - Extraction prompt includes all 26 rule types with param schemas
   - Returns JSON: {lender_name, notes, contact_email, contact_phone, programs[{name, rules[]}]}
5. Response stripped of markdown fences, parsed as ParsedLenderPreview
6. Frontend shows preview — user can review before import
7. POST /parse-policy/import creates: LenderProgram rows + EligibilityRule rows
   under an existing Lender (user selects which lender)
```

Human review is mandatory before import — the preview step is not skippable.

---

## 11. Docker Compose Environment

9 services in total:

```
postgres          — PostgreSQL 15
rabbitmq          — Message broker for Hatchet
hatchet-migration — One-shot: runs Hatchet DB migrations
hatchet-api       — Hatchet API server
hatchet-engine    — Hatchet workflow engine
hatchet-setup-config — One-shot: bootstraps tenant + API token
backend           — FastAPI: alembic upgrade head + seed + uvicorn
worker            — Hatchet worker: python -m app.workflows.worker
frontend          — Vite dev server
```

Startup order enforced via `depends_on` + healthchecks:
- `rabbitmq` must be healthy before `hatchet-engine` / `hatchet-api`
- `hatchet-migration` must complete before `hatchet-api`
- Backend waits for postgres

**Running without Docker** (local dev):
1. Start postgres only: `docker compose up postgres -d`
2. Set `HATCHET_CLIENT_TOKEN=` (empty) in `backend/.env`
3. `alembic upgrade head && python -m seed_data.seed`
4. `uvicorn app.main:app --reload` — underwriting runs in sync fallback mode

---

## Key Design Decisions

See [DECISIONS.md](DECISIONS.md) for full rationale. Summary:

| Decision | Choice | Alternative Considered |
|---|---|---|
| Workflow engine | Hatchet with sync fallback | Celery (less visible), no fallback |
| Rule registration | `@register` decorator, zero-config discovery | Class scan / config file |
| Primary keys | UUID everywhere | Auto-increment int |
| Application creation | 5 separate API calls (one per step) | Single nested POST |
| State separation | `state_of_operation` ≠ `business.state` | Single state field |
| Fit score base | 85 pts (room for 15 bonus) | 100 pts base, deduct |
| Rule audit trail | `rule_id` nullable with SET NULL | Hard FK (blocks rule deletion) |
| PDF parsing | Claude API + human review | Template parsing, no review |
| Async driver | asyncpg for app, sync alembic env | Single driver for both |
