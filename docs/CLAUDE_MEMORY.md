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

**Step 2: Build the calculation engine (pure functions + unit tests)**

Architecture is fully defined in `docs/finance/FINANCE_MVP_ARCHITECTURE.md` Section 8.

Priority order:
1. Implement the 11-step calculation sequence for all 4 business model types (SaaS, marketplace, service, product)
2. Implement edge case guards (division by zero, negative customers, missing config)
3. Implement derived summary metrics (runway, break-even, LTV, CAC, LTV:CAC)
4. Write unit tests for every formula — must pass before any API or UI work begins

Key files to create:
- `src/engine/calculate.ts` (or equivalent) — pure calculation function
- `src/engine/calculate.test.ts` — unit tests
- `src/engine/types.ts` — input/output type definitions matching Section 6 data entities

**Step 3 (after calculation engine):** Build the validation rule engine (Section 9 rules)
**Step 4 (after validation engine):** Build the REST API layer (Section 7)
**Step 5 (after API):** Integrate Claude API for AI narrative (Section 9.3)
**Step 6 (after API):** Build frontend input flow (Steps 1–3)
**Step 7 (after input flow):** Build forecast output screen (Step 4)
**Step 8 (after output screen):** Build validation + export screen (Step 5)
