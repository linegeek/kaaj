# Architectural Decisions — Kaaj

This document records the key architectural choices made during the design and implementation of the Kaaj equipment finance loan underwriting and lender matching platform, along with the rationale and trade-offs for each.

---

## 1. Hatchet for Async Workflow Orchestration

**Decision:** Use [Hatchet](https://hatchet.run) as the DAG-based workflow engine for the underwriting pipeline rather than Celery, ARQ, or raw asyncio tasks.

**Rationale:**
- Hatchet provides first-class DAG support with named steps, retries, and observability out of the box.
- Each underwriting run step (validate → derive → fetch → evaluate → aggregate → persist) is independently retryable, which matters when external calls (e.g., the Claude API for policy parsing) fail transiently.
- The Hatchet UI gives operators real-time visibility into which step of an underwriting run is in progress or failed — critical for debugging production issues.

**Trade-off:** Hatchet adds operational complexity (RabbitMQ + Hatchet engine + Hatchet API services). To mitigate this for local development, every workflow includes a `_run_sync_fallback()` path that executes all steps in-process without Hatchet, triggered when Hatchet is unreachable.

---

## 2. Decorator-Based Rule Evaluator Registry

**Decision:** Use a class decorator (`@RuleEvaluatorRegistry.register`) to register rule evaluators rather than a configuration file, a database-driven strategy table, or explicit factory methods.

**Rationale:**
- Adding a new rule type requires touching exactly two files: the new evaluator module and `registry.py`'s `ensure_loaded()` import list. No changes to the evaluation engine, the API, or the database schema.
- Evaluators are self-describing — each class declares its own `rule_type`, `label`, and `param_schema` as class attributes, making the registry the single source of truth for rule metadata.
- Type safety: `RuleEvaluatorRegistry.get(rule_type)` raises `ValueError` for unknown types at call time, not silently at evaluation time.

**Trade-off:** The `ensure_loaded()` import list in `registry.py` must be updated when new evaluator modules are added. This is a minor maintenance cost accepted in exchange for explicit control over which modules are loaded.

---

## 3. UUID Primary Keys Everywhere

**Decision:** All primary keys use `UUID` (stored as `uuid` in PostgreSQL) rather than auto-incrementing integers.

**Rationale:**
- UUIDs are safe to generate client-side, which simplifies optimistic UI patterns (e.g., the frontend can assign an ID before the server confirms creation).
- UUIDs do not leak record counts or creation order to the client, which matters for lender data that competitors could enumerate.
- Consistent ID type across all models eliminates a class of bugs where `int` IDs are accidentally mixed with `str`/`UUID` IDs in foreign key joins.

**Trade-off:** UUID indexes are larger and slightly slower than integer indexes. For a platform of this scale this is negligible.

---

## 4. Step-by-Step Application Creation (Sub-Endpoints)

**Decision:** Application creation is split into four sequential endpoint calls (`POST /applications`, `POST /{id}/guarantors`, `PUT /{id}/business-credit`, `PUT /{id}/loan-request`) rather than a single large `POST /applications` with the full payload.

**Rationale:**
- Mirrors the 5-step frontend wizard — each wizard step can save progress independently, so a page reload or network drop doesn't lose the user's input.
- Enables partial application submission: a broker can save a client's business info and return later to complete the loan request details.
- Each sub-resource endpoint validates only the fields relevant to that step, producing targeted validation errors.

**Trade-off:** More round trips from the frontend. Accepted because the wizard UX already assumes sequential progression and each step is user-gated.

---

## 5. `state_of_operation` Separate from `Business.state`

**Decision:** `LoanRequest` has its own `state_of_operation` field rather than relying on `Business.state` for geographic eligibility rules.

**Rationale:**
- A business incorporated in Delaware may operate equipment in Texas. Geographic lending restrictions apply to where the equipment will be operated, not where the business is registered.
- Keeping the fields separate makes the intent explicit and prevents the geographic evaluator from silently using the wrong state.

**Trade-off:** The frontend must expose a separate "state of operation" field in the loan request step, and the underwriting derive step must fall back to `Business.state` when `state_of_operation` is not provided.

---

## 6. Fit Score Formula: 85 Base + 15 Bonus

**Decision:** Fit score = `(passed_weight / total_weight) * 85` + up to 15 bonus points, capped at 100.

**Rationale:**
- A pure pass-rate score (0–100 = % of weighted rules passed) would allow a lender with zero hard rules to score 100% on an application that barely qualifies. The 85-point ceiling for baseline rule compliance reserves headroom for bonus signals (strong credit, long operating history, established relationship).
- Bonus points are additive on top of baseline, rewarding applicants who exceed minimums — not just meet them.
- The cap at 100 prevents bonus stacking from distorting the ranking.

**Trade-off:** The 85/15 split is a product decision, not a mathematically derived one. Adjusting the split changes the relative weight of "meets minimums" vs. "exceeds minimums" across all programs and lenders simultaneously. This should be revisited as real underwriting data accumulates.

---

## 7. `CriteriaCheckResult.rule_id` Nullable (SET NULL on Delete)

**Decision:** `CriteriaCheckResult.rule_id` is a nullable foreign key with `ON DELETE SET NULL` rather than `ON DELETE CASCADE` or a non-nullable key.

**Rationale:**
- Underwriting run results are an audit trail. Deleting a rule (e.g., because a lender retired a program) should not delete historical check results that show why an application was approved or declined.
- `SET NULL` preserves the result row with `rule_id = NULL`, allowing historical queries to see that a check was performed even after the rule no longer exists.

**Trade-off:** Queries that join `CriteriaCheckResult` to `EligibilityRule` must handle nullable `rule_id`. The API response includes denormalized `rule_type`, `rule_name`, and `weight` on each result to make the result self-describing even when `rule_id` is null.

---

## 8. PDF Policy Parsing via Claude API

**Decision:** Use `pdfplumber` to extract text from lender policy PDFs, then send the text to Claude (`claude-opus-4-7`) with a structured prompt to produce a JSON representation of lender programs and eligibility rules.

**Rationale:**
- Lender policy documents are unstructured prose: tables, bullet lists, footnotes. Rule-based parsers require per-document templates and break when formatting changes. An LLM handles format variation gracefully.
- Claude's structured output mode (JSON schema enforcement) eliminates post-processing parsing failures.
- The extracted JSON is presented as a preview for human review before being committed to the database, so LLM hallucinations are caught before they affect underwriting.

**Trade-off:** Parsing costs money (Claude API tokens) and is non-deterministic. The human review step (preview → confirm) is the safeguard. Future improvement: cache parsed results by PDF hash to avoid re-parsing unchanged documents.

---

## 9. Sync Fallback for Local Development

**Decision:** Every Hatchet workflow step has a corresponding `_run_sync_fallback()` function that runs all steps sequentially in-process.

**Rationale:**
- Running the full Hatchet stack (RabbitMQ + engine + API) for every `make dev` session adds startup time and resource overhead.
- The fallback path allows frontend and API development without Hatchet running, using the same business logic as the real workflow.

**Trade-off:** Two code paths for the same logic means divergence is possible. Mitigated by: (a) the fallback calls the same step functions as the Hatchet workflow, and (b) the integration test suite runs against the real Hatchet path.

---

## 10. Async SQLAlchemy 2.0 with asyncpg

**Decision:** Use SQLAlchemy 2.0 async ORM with the `asyncpg` driver rather than synchronous SQLAlchemy or a lighter ORM (Tortoise, SQLModel).

**Rationale:**
- FastAPI is async-native; a synchronous ORM would require `run_in_executor` wrappers on every database call, adding complexity and reducing throughput.
- SQLAlchemy 2.0's explicit `async with AsyncSession` context manager makes transaction boundaries clear and testable.
- `asyncpg` is the fastest PostgreSQL driver for asyncio workloads by benchmark.

**Trade-off:** SQLAlchemy 2.0 async has a steeper learning curve than synchronous SQLAlchemy. Alembic migrations must use `create_async_engine` with `run_sync` wrappers, which is non-obvious but well-documented.
