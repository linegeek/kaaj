# Kaaj - Equipment Finance Underwriting Platform

Kaaj is a full-stack platform for equipment finance lenders to manage lending programs, define eligibility rules, and run automated underwriting against borrower applications. It matches applicants to lender programs using a weighted scoring engine and generates fit scores with per-rule explanations.

## Architecture Overview

```
frontend/          React 18 + Vite + TanStack Query
backend/           FastAPI + async SQLAlchemy 2.0
  app/
    api/v1/        REST endpoints (lenders, applications, underwriting, reference, parse-policy)
    engine/
      rules/       26 rule evaluators across 4 categories
      scorer.py    Weighted fit scoring (base 85 + bonus up to 15, capped at 100)
    workflows/     Hatchet DAG steps with in-process sync fallback
    models/        SQLAlchemy ORM (11 tables)
    schemas/       Pydantic request/response models
  tests/           pytest unit tests for all evaluators and scorer
  seed_data/       5 seed lenders with programs and rules
docker-compose.yml 9 services: postgres, rabbitmq, hatchet (4), backend, worker, frontend
```

Key architectural decisions are documented in [DECISIONS.md](DECISIONS.md).

## Rule Categories

| Category | Count | Examples |
|----------|-------|---------|
| Credit | 6 | MIN_CREDIT_SCORE, MAX_BANKRUPTCIES, MAX_DEROGATORY_MARKS |
| Business | 7 | MIN_YEARS_IN_BUSINESS, ALLOWED_BUSINESS_TYPES, NAICS_CODE_ALLOWLIST |
| Equipment | 7 | MAX_EQUIPMENT_AGE_YRS, ALLOWED_EQUIPMENT_TYPES, MIN_DOWN_PAYMENT_PCT |
| Geographic | 6 | ALLOWED_STATES, EXCLUDED_STATES, MIN_CREDIT_SCORE_BY_STATE |

## Fit Score Formula

```
base_score = (sum of passed rule weights / sum of all non-skipped rule weights) * 85

bonuses (each +5, max +15 total):
  credit score >= 750
  years in business >= 10
  annual revenue >= $1,000,000

fit_score = min(base_score + bonuses, 100)
```

Skipped rules (missing data) are excluded from the weight denominator so they do not penalize applicants. An empty rule set returns 85.

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop

### Option A - Docker Compose (full stack)

```bash
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY for PDF import, HATCHET_CLIENT_TOKEN if using Hatchet

docker compose up --build
```

Services start on:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Hatchet dashboard: http://localhost:8080

Database migrations and seed data run automatically on backend startup.

### Option B - Local dev (faster iteration)

**Backend:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

pip install -e ".[dev]"

# Start postgres (or point DATABASE_URL at an existing instance)
docker compose up postgres -d

# Copy and edit env
cp ../.env.example .env

# Run migrations and seed
alembic upgrade head
python -m seed_data.seed

# Start API server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev          # starts on http://localhost:5173
```

**Worker (optional - needed for Hatchet-backed underwriting):**

```bash
cd backend
python -m app.workflows.worker
```

Without the worker running, underwriting falls back to an in-process async execution path automatically.

### Running Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=term-missing
```

Tests cover all 26 rule evaluators and the FitScorer. They use an in-memory `EvalContext` and require no database connection.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async DSN (`postgresql+asyncpg://...`) |
| `ANTHROPIC_API_KEY` | For PDF import | Claude API key used to parse lender PDF guidelines |
| `HATCHET_CLIENT_TOKEN` | For Hatchet | Token from Hatchet dashboard; omit to use sync fallback |
| `SECRET_KEY` | Yes | App secret key (change in production) |
| `DEBUG` | No | Set `true` to enable SQLAlchemy query logging |

## API Reference

All endpoints are prefixed with `/api/v1`.

### Lenders

| Method | Path | Description |
|--------|------|-------------|
| GET | `/lenders` | List all lenders |
| POST | `/lenders` | Create a lender |
| GET | `/lenders/{id}` | Get lender with programs |
| PUT | `/lenders/{id}` | Update lender |
| DELETE | `/lenders/{id}` | Delete lender |
| GET | `/lenders/{id}/programs` | List programs for a lender |
| POST | `/lenders/{id}/programs` | Create a program |
| GET | `/programs/{id}` | Get program with rules |
| PUT | `/programs/{id}` | Update program |
| DELETE | `/programs/{id}` | Delete program |
| GET | `/programs/{id}/rules` | List rules for a program |
| POST | `/programs/{id}/rules` | Add a rule |
| PUT | `/rules/{id}` | Update a rule |
| DELETE | `/rules/{id}` | Delete a rule |

### Applications (5-step wizard)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/applications` | Step 1 - Create application + business |
| POST | `/applications/{id}/guarantors` | Step 2 - Add a personal guarantor |
| PUT | `/applications/{id}/business-credit` | Step 3 - Business credit profile |
| PUT | `/applications/{id}/loan-request` | Step 4 - Loan and equipment details |
| GET | `/applications/{id}` | Step 5 / full application view |

### Underwriting

| Method | Path | Description |
|--------|------|-------------|
| POST | `/underwriting/run` | Start an underwriting run for an application |
| GET | `/underwriting/runs/{id}` | Poll run status and results |

Poll `GET /underwriting/runs/{id}` until `status` is `completed` or `failed`. The frontend polls every 2 seconds automatically.

### Reference Data

| Method | Path | Description |
|--------|------|-------------|
| GET | `/reference/rule-types` | All 26 rule types with labels, categories, param schemas |
| GET | `/reference/equipment-types` | Allowed equipment type values |
| GET | `/reference/business-types` | Allowed business entity type values |
| GET | `/reference/states` | US state codes |

### PDF Policy Import

| Method | Path | Description |
|--------|------|-------------|
| POST | `/parse-policy/upload` | Upload a PDF, returns parsed lender preview |
| POST | `/parse-policy/import` | Import a confirmed preview as lender + programs + rules |

The upload step uses Claude to extract structured lending criteria from the PDF. The import step creates the database records. This two-step flow gives users a chance to review and correct Claude's interpretation before committing it.

## Adding a New Rule Type

1. Add the enum value to `RuleType` in [backend/app/engine/rules/base.py](backend/app/engine/rules/base.py)
2. Add its metadata entry to `RULE_TYPE_META` in the same file
3. Add an evaluator class decorated with `@RuleEvaluatorRegistry.register(RuleType.YOUR_NEW_RULE)` in the appropriate category file (`credit.py`, `business.py`, `equipment.py`, or `geographic.py`)

That's it. The registry, API, frontend dropdown, and PDF parser all pick it up automatically.

## Project Structure

```
backend/
  app/
    api/v1/
      lenders.py          CRUD for lenders, programs, rules
      applications.py     5-step application creation
      underwriting.py     Run creation and result polling
      reference.py        Static lookup data
      parse_policy.py     PDF upload and import
    core/
      config.py           Pydantic settings
      database.py         Async SQLAlchemy engine and session
    engine/
      rules/
        base.py           RuleType enum, EvalContext, EvalResult, BaseRuleEvaluator
        registry.py       RuleEvaluatorRegistry with @register decorator
        credit.py         6 credit evaluators
        business.py       7 business evaluators
        equipment.py      7 equipment evaluators
        geographic.py     6 geographic evaluators
      scorer.py           FitScorer
    models/
      lender.py           Lender, LenderProgram, EligibilityRule
      application.py      Application, Business, PersonalGuarantor, BusinessCredit, LoanRequest
      underwriting.py     UnderwritingRun, CriteriaCheckResult
    schemas/              Pydantic request/response models
    workflows/
      underwriting.py     Hatchet DAG + sync fallback
      worker.py           Worker entrypoint
    main.py               FastAPI app factory
  alembic/
    versions/0001_initial_schema.py
  seed_data/seed.py       5 seed lenders
  tests/
    conftest.py           make_ctx() helper
    test_credit_rules.py
    test_business_rules.py
    test_equipment_rules.py
    test_geographic_rules.py
    test_scorer.py

frontend/
  src/
    types/index.ts        TypeScript interfaces
    lib/api.ts            Axios client
    hooks/                TanStack Query hooks
    pages/
      Dashboard.tsx
      ApplicationWizard.tsx
      UnderwritingResults.tsx
      LenderList.tsx
      LenderDetail.tsx
    components/
      lender-policy/      RuleFormModal, PdfUploadModal
```
