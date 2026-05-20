# CLAUDE MEMORY — AI Finance Copilot Project

**Project:** AI Finance Copilot for University Startup Competitions  
**Last updated:** May 2026

---

## What Has Been Done

### Research Task (Completed)
Researched publicly available information on the following financial forecasting tools:
- LivePlan, Sturppy, Runway (runway.com), Baremetrics, Finmark, Causal, Fathom

Full research document saved at:
`docs/research/financial_forecasting_tools_research.md`

### Architecture Task (Completed)
Defined the full product architecture for the Finance MVP.

Document saved at:
`docs/finance/FINANCE_MVP_ARCHITECTURE.md`

Branch: `finance-copilot`
Commit: `docs: define finance MVP architecture`

Architecture covers:
- Product positioning and differentiators vs. LivePlan, Sturppy, etc.
- Target user definition (university competition students, pre-revenue)
- 5-step core workflow (Setup → Revenue → Costs → Output → Validate/Export)
- Full MVP scope (in-scope and explicitly out-of-scope features)
- All 8 data entities with complete field definitions
- Full REST API plan (7 endpoint groups, 20+ endpoints)
- Calculation engine plan: full formula sequence for all 4 business model types
- Validation engine plan: 20 named rules across 5 categories + AI narrative layer
- 5-phase iteration plan (MVP → Scenarios → Collaboration → Benchmarks → Pitch Deck)
- Smart defaults table and business model type definitions

---

## Key Findings

### Market Gap
None of the researched tools target university startup competition students who:
- Have zero historical data or live business data
- Have no finance or accounting background
- Need competition-ready output (not investor due diligence-level accuracy)
- Need educational scaffolding while building their model

### Common Workflow (All Tools)
Business model setup → Revenue inputs → Cost inputs → Cashflow setup → Output review and iteration

### Most Critical Financial Modules for Our MVP
1. Revenue forecast (price × customers × growth rate)
2. Payroll / headcount plan (roles, salaries, start dates)
3. Fixed + variable cost model
4. Cashflow statement (monthly, auto-generated)
5. Runway calculation (cash ÷ net burn)
6. P&L summary (annual, auto-generated)
7. Break-even analysis
8. Scenario analysis (base / optimistic / pessimistic)
9. Shareable/exportable output

### Best Design Principles Observed
- Guided question-based input (not a blank spreadsheet)
- Inline terminology explanations (non-negotiable for non-finance users)
- Business model templates to avoid blank-form paralysis
- Real-time visual feedback (changes flow through immediately)
- Validation alerts that warn but don't block
- AI suggestions for missing categories or unrealistic assumptions

### Key Validation Checks Needed
- Unrealistic growth rate (>30% monthly is aggressive; flag it)
- Runway < 6 months (danger signal; flag with remediation)
- LTV < CAC (unsustainable unit economics)
- LTV:CAC < 3:1 (below SaaS health threshold)
- Missing cost categories (no server/API cost for tech product, etc.)
- Negative cashflow with no mitigation plan

### What to Exclude from MVP
- Live accounting integrations (no historical data)
- Cap table / equity modeling
- Balance sheet generation
- Multi-currency
- HRIS / payroll integrations
- Actuals tracking

### What to Add Unique to Competition Context
- "What judges look for" contextual guidance
- Assumption documentation prompts (judges probe assumptions)
- Plain-language narrative auto-generation
- Competition-ready one-page financial summary export
- Benchmark ranges per business type and metric
- "Fix it" suggestions when validation issues detected

---

## Recommended MVP Direction

### Product Concept
A guided, AI-powered financial model builder for university startup competitions. Input 10–15 key numbers, get a competition-ready 3-year financial model in under 20 minutes, with AI validation and a pitch-ready export.

### MVP User Flow (5 Steps)
1. Business Setup (name, type, competition context)
2. Revenue Model (pricing, customers, growth, churn)
3. Costs (team, fixed, variable, starting cash)
4. Forecast Output (cashflow chart, runway, P&L, break-even, LTV:CAC)
5. Validation + Export (AI feedback, narrative, shareable summary)

### Business Model Types for Phase 1
SaaS / Subscription, Marketplace, Service / Consulting, Physical Product

### Core Tech Requirements
- AI layer: Claude API for validation, suggestion, and narrative generation
- Financial calculation engine: pure logic (no external data needed)
- Output: shareable link + PDF summary

---

## Next Implementation Step

### Round 1 — Finance MVP Data Foundation (Completed)

Completed on 2026-05-20 on branch `finance-copilot`.

Implemented only the requested data foundation:
- Extended `Project` with nullable finance setup fields: `industry`, `competition_type`, `business_model`, `planning_horizon`.
- Added SQLAlchemy models:
  - `RevenueConfig`
  - `CostConfig`
  - `ForecastOutput`
  - `ValidationReport`
- Added relationships:
  - Project has one `RevenueConfig`
  - Project has one `CostConfig`
  - Project has many `ForecastOutput`
  - Project has many `ValidationReport`
- Added Pydantic schemas:
  - `RevenueConfigCreate`
  - `RevenueConfigRead`
  - `CostConfigCreate`
  - `CostConfigRead`
  - `ForecastOutputRead`
  - `ValidationReportRead`
- Added minimal CRUD/service functions for revenue config, cost config, forecast outputs, and validation reports.
- Added API endpoints:
  - `PUT /projects/{project_id}/finance/revenue`
  - `GET /projects/{project_id}/finance/revenue`
  - `PUT /projects/{project_id}/finance/costs`
  - `GET /projects/{project_id}/finance/costs`
  - `GET /projects/{project_id}/finance/forecasts`
  - `GET /projects/{project_id}/finance/validations`
- Added Alembic migration `0006_finance_mvp_foundation`.

Validation:
- Confirmed current Git branch: `finance-copilot`.
- `docker compose up -d --build` could not run because root `.env` is missing in this workspace.
- Existing Docker containers were running:
  - `venture-copilot-backend`
  - `venture-copilot-postgres`
  - `venture-copilot-redis`
- `docker exec venture-copilot-backend python -m compileall app` passed.
- `docker exec venture-copilot-backend alembic -c alembic.ini upgrade head` passed.
- `GET /health` returned 200.
- Smoke-tested project creation with new finance setup fields.
- Smoke-tested revenue and cost config PUT/GET endpoints.
- Smoke-tested forecast output and validation report list endpoints; both returned empty arrays as expected because Round 1 does not implement calculation or validation generation.

Important note:
- Requested document path `docs/finance/FINANCE_MVP_ARCHITECTURE.md` was not present in the workspace.
- Existing `docs/FINANCE_MVP_ARCHITECTURE.md` was present but empty and untracked.

### Round 2 — Deterministic Finance Calculation Engine (Completed)

Completed on 2026-05-20 on branch `finance-copilot`.

Implemented pure calculation logic only:
- Added `backend/app/finance/calculation_engine.py`.
- No database dependency.
- No API dependency.
- No AI dependency.
- No frontend/export/chart changes.

Calculation input:
- Project finance setup dictionary.
- `RevenueConfig`-style dictionary.
- `CostConfig`-style dictionary.
- Planning horizon: supports 12, 24, and 36 months.

Supported MVP business models:
- SaaS / subscription.
- Service / consulting.

Calculation coverage:
- SaaS monthly active customers, new customers, churned customers, revenue, MRR, ARR, churn impact.
- Service active clients, new clients, client growth, churn/project completion, revenue.
- Shared fixed costs, variable costs, marketing costs, payroll/headcount costs, one-time costs.
- Total costs, gross profit, net profit/loss, net cashflow, cumulative cash balance.
- Gross burn, net burn, runway months, zero-cash month, break-even month.
- Gross margin %, LTV, CAC, LTV:CAC ratio, ARPU where possible.
- Annual revenue/net profit/gross margin summaries.

Edge cases covered:
- Division by zero returns `None` for undefined ratios.
- Negative customers are clamped to zero.
- Missing optional fields use safe defaults.
- Monetary values are rounded to 2 decimals.
- Customer/client counts are integers.
- Zero revenue / zero cost scenarios do not crash.

Tests added:
- `backend/tests/test_calculation_engine.py`
- SaaS revenue growth.
- Churn behavior.
- Cash balance calculation.
- Runway calculation.
- Break-even calculation.
- Zero revenue / zero cost edge case.
- Division by zero metrics.

Validation:
- `docker exec venture-copilot-backend python -m compileall app` passed.
- `docker exec -w /app venture-copilot-backend python -m pytest tests/test_calculation_engine.py` passed: 7 tests.

Remaining rounds:
- Round 3: validation rules.
- Round 4: API integration and persistence into `ForecastOutput`.
- Round 5: frontend flow.
- Round 6: export and AI narrative polish.

### Round 3 — Deterministic Validation Engine (Completed)

Completed on 2026-05-20 on branch `finance-copilot`.

Implemented rule-based validation only:
- Added `backend/app/finance/validation_engine.py`.
- No AI narrative generation.
- No Claude/OpenAI calls.
- No database changes.
- No API changes.
- No frontend/export/chart changes.

Validation input:
- Calculation engine output.
- Project business model.
- `RevenueConfig`-style dictionary.
- `CostConfig`-style dictionary.

Validation output is `ValidationReport`-compatible:
- `summary_narrative: null`
- `judge_perspective: null`
- `issue_count.errors`
- `issue_count.warnings`
- `issue_count.suggestions`
- `issues[]` with stable `rule_id`, severity, title, description, fix suggestion, affected fields.

Rules implemented from Section 9.2 where supported by Round 1/2 data:
- Cashflow: `CF-001`, `CF-002`, `CF-003`, `CF-004`, `CF-005`
- Revenue: `REV-001`, `REV-002`, `REV-003`, `REV-004`, `REV-005`
- Churn: `CHURN-001`, `CHURN-002`, `CHURN-003`
- Unit economics: `UNIT-001`, `UNIT-002`, `UNIT-003`, `UNIT-004`
- Cost completeness: `COST-001`, `COST-003`, `COST-005`
- Margin: `MARGIN-001`, `MARGIN-003`, `MARGIN-004`

Rules intentionally skipped for now:
- `COST-002` and `MARGIN-002` because physical product models are not part of Round 2 calculation support.
- `COST-004` because Round 1/2 do not yet provide a reliable intended-team-vs-hire-month model.

Tests added:
- `backend/tests/test_validation_engine.py`
- Healthy model has no errors.
- Runway under 6 months triggers `CF-003`.
- Monthly growth over 30% triggers `REV-001`.
- Monthly growth over 50% triggers `REV-002`.
- Churn over 10% triggers `CHURN-001`.
- Zero churn triggers `CHURN-003`.
- LTV < CAC triggers `UNIT-001`.
- LTV:CAC < 3 triggers `UNIT-002`.
- Missing SaaS server/API cost triggers `COST-001`.
- Negative gross margin triggers `MARGIN-003`.
- Break-even not reached triggers `MARGIN-004`.

Validation:
- `docker exec venture-copilot-backend python -m compileall app` passed.
- `docker exec -w /app venture-copilot-backend python -m pytest` passed: 18 tests.

Remaining rounds:
- Round 4: API integration and persistence into `ForecastOutput` / `ValidationReport`.
- Round 5: frontend flow.
- Round 6: export and AI narrative polish.

**Next Step: Round 4 — API integration and persistence**

Architecture is fully defined in `docs/finance/FINANCE_MVP_ARCHITECTURE.md` Section 8.

Priority order:
1. Wire calculation and validation engines into service/API endpoints.
2. Persist calculation output into `ForecastOutput`.
3. Persist validation report into `ValidationReport`.
4. Preserve existing endpoints and response envelope.
