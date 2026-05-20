# Venture Copilot — Claude Memory File

> **INSTRUCTION FOR CLAUDE**: Read this file at the START of every task.
> Update this file at the END of every task.
> This is the single source of truth for project state.

---

## 1. Product Definition

**Product:** Venture Copilot
**Type:** Backend-only, finance-first AI business planning platform
**Users:** Chinese university entrepreneurship competition teams
**Primary scenario:** 挑战杯 / 互联网+ style Chinese business plans
**Core flow:** Startup idea → 36-month financial forecast → business plan → research report → PDF/DOCX export

---

## 2. Architecture Decisions (Locked)

- **FastAPI** + **SQLAlchemy (async)** + **PostgreSQL** + **Redis** — all in Docker
- **No frontend** — pure REST API backend
- **MockProvider only for Iteration 3** — no Claude/OpenAI integration yet
- **MockResearchProvider only for Iteration 4** — no web search, scraping, RAG, or external APIs yet
- **Business plan templates** — `generic_startup`, `challenge_cup`, `internet_plus`, `custom`
- **Language modes** — `zh-CN` default, `en-US` supported
- **Project-level data isolation** — every route scopes by `project_id` + hardcoded `user_id`
- **Deterministic finance engine** — no ML, pure arithmetic in `finance/engine.py`
- **Placeholder auth** — `user_id = "demo_user"` hardcoded in routes
- **Standard response envelope** — `{"success": bool, "data": any, "message": str|null}` on all endpoints
- **Service layer pattern** — routes are thin; DB + business logic lives in `services/`

---

## 3. Environment Rules (NON-NEGOTIABLE)

❌ NEVER create: `.venv`, `venv`, `conda env`, `poetry local env`
❌ NEVER run: `pip install`, `python -m venv`, `uvicorn` on host
✅ ALWAYS: run everything inside Docker containers
✅ ALWAYS: install dependencies via Dockerfile only
✅ ALWAYS: use `docker compose` commands only

---

## 4. Completed Modules

### Iteration 0 ✅ Infrastructure

### Iteration 1 ✅ FastAPI + DB + Project CRUD

Validated on 2026-05-19.

### Iteration 2 ✅ Finance Engine

Validated on 2026-05-19.

### Iteration 3 ✅ Business Plan Generator

Completed and validated on 2026-05-19.

### Iteration 4 ✅ Research Report + Citations

Completed and validated on 2026-05-19.

| File | Status |
|---|---|
| `backend/app/schemas/research.py` | ✅ ResearchReportRead + Citation schema |
| `backend/app/services/research_service.py` | ✅ Generate/store/get latest research report |
| `backend/app/research/mock_research_provider.py` | ✅ Static credible-style citation provider |
| `backend/app/api/routes/research.py` | ✅ POST + GET /projects/{id}/research |
| `backend/app/main.py` | ✅ Research router registered |
| `backend/alembic/versions/0002_research_report_fields.py` | ✅ Adds provider_used, summary, industry_trends |

### Iteration 5 ✅ Export + MVP Finalization

Completed and validated on 2026-05-19. MVP is complete.

| File | Status |
|---|---|
| `backend/app/schemas/export.py` | ✅ ExportResult + ExportFile schemas |
| `backend/app/services/export_service.py` | ✅ Combine project, forecast, business plan, research into PDF/DOCX |
| `backend/app/api/routes/export.py` | ✅ POST PDF, POST DOCX, GET exports |
| `backend/app/main.py` | ✅ Export router + static `/exports` mount registered |
| `backend/exports/` | ✅ Export storage directory |

### Iteration 6 ✅ Localisation + Configurable Templates

Completed and validated on 2026-05-19.

| File | Status |
|---|---|
| `backend/app/schemas/template.py` | ✅ BusinessPlanTemplateRequest |
| `backend/app/services/template_service.py` | ✅ Resolve templates, section order, Chinese/English content |
| `backend/app/templates/business_plan_templates.py` | ✅ Section headings + presets |
| `backend/app/services/business_plan_service.py` | ✅ Stores language/template/selected sections in existing JSON |
| `backend/app/api/routes/business_plan.py` | ✅ POST body supports language/template/sections |
| `backend/app/services/export_service.py` | ✅ Export respects language and selected section order |

### Iteration 7 ✅ Finance Pro + Framework Engine + Chinese Cleanup

Completed and validated on 2026-05-19.

| File | Status |
|---|---|
| `backend/app/finance/engine.py` | ✅ Finance Pro statements, valuation, sensitivity, markdown/CSV/chart data |
| `backend/app/schemas/finance.py` | ✅ Backward-compatible extended FinanceForecastCreate/Read |
| `backend/app/frameworks/engine.py` | ✅ SWOT, PEST, Porter, BMC, TAM/SAM/SOM, STP, 4P, value chain, risk and competitor matrices |
| `backend/app/models/framework_analysis.py` | ✅ Stores latest framework analysis |
| `backend/app/schemas/framework.py` | ✅ Framework request/read schemas |
| `backend/app/services/framework_service.py` | ✅ Generate/store/get framework analysis |
| `backend/app/api/routes/frameworks.py` | ✅ POST + GET framework endpoints |
| `backend/app/research/mock_research_provider.py` | ✅ zh-CN body text is Chinese |
| `backend/app/services/template_service.py` | ✅ Business plan can include selected framework sections |
| `backend/app/services/export_service.py` | ✅ Export respects selected framework sections and Chinese body text |

### Iteration 8 ✅ AI Provider Layer + Consistency Engine + Project Scoring

Completed and validated on 2026-05-19.

| File | Status |
|---|---|
| `backend/app/ai/base.py` | ✅ Request-scoped AIConfig + provider base |
| `backend/app/ai/provider_factory.py` | ✅ mock/openai/anthropic/deepseek/qwen/moonshot/openai_compatible selection |
| `backend/app/ai/providers/*.py` | ✅ Provider shells with safe mock fallback |
| `backend/app/validators/*.py` | ✅ Finance, market, research, template, language, logic, export validators |
| `backend/app/validators/consistency_engine.py` | ✅ Aggregated project scoring |
| `backend/app/models/project_review.py` | ✅ Stores latest project review score JSON |
| `backend/app/schemas/review.py` | ✅ Review response schema |
| `backend/app/services/review_service.py` | ✅ Reads project package and scores consistency |
| `backend/app/api/routes/review.py` | ✅ POST + GET /projects/{id}/review |
| `backend/app/services/export_service.py` | ✅ Optional include_review export appendix |

### Iteration 9 ✅ External Repo Study + Lightweight Research/Competitor Integration

Completed and validated on 2026-05-19.

Reference repos inspected, but not imported wholesale:

| Repo | Useful Ideas Kept | Ignored |
|---|---|---|
| `liangdabiao/exa-research-mcp-skill` | Research provider boundary, Exa-style search categories, citations, multi-source validation | Claude skill runtime, MCP setup, browser fallback, markdown report files |
| `kk-taro/competitoragent-web` | Competitor matrix fields, market gap, positioning, pricing/strength/weakness structure | Streamlit UI, LangGraph, LangChain, DuckDuckGo scraping, Word export |
| `msitarzewski/agency-agents` | Growth strategy, STP/4P, funding/investor-perspective placeholders | Full prompt library, agent personalities, multi-agent orchestration |

| File | Status |
|---|---|
| `backend/app/research/base.py` | ✅ ResearchConfig + provider base |
| `backend/app/research/provider_factory.py` | ✅ mock/exa/tavily/serpapi research provider selection |
| `backend/app/research/exa_provider.py` | ✅ Exa-ready provider shell, no live search yet |
| `backend/app/research/future_provider.py` | ✅ Future Tavily/SerpApi placeholders |
| `backend/app/competitors/engine.py` | ✅ Lightweight competitor matrix, market gap, positioning |
| `backend/app/frameworks/engine.py` | ✅ competitor_matrix, growth_strategy, funding_suggestion |
| `backend/app/templates/business_plan_templates.py` | ✅ Section headings for new frameworks |
| `backend/app/services/template_service.py` | ✅ New framework sections can be selected into BP/export |

### Iteration 10 ✅ Real Provider Wiring

Completed on 2026-05-19. Code paths are real HTTP integrations; live success validation requires user-supplied API keys or a running local Ollama server.

| File | Status |
|---|---|
| `backend/app/ai/base.py` | ✅ OpenAI-compatible `/chat/completions` HTTP client + JSON parsing |
| `backend/app/ai/provider_factory.py` | ✅ openai/deepseek/qwen/moonshot/openrouter/ollama mappings |
| `backend/app/services/business_plan_service.py` | ✅ Non-mock AI provider generates selected BP section content |
| `backend/app/services/research_service.py` | ✅ Non-mock AI provider can generate research JSON when research provider is mock |
| `backend/app/services/framework_service.py` | ✅ Non-mock AI provider can generate framework JSON |
| `backend/app/research/exa_provider.py` | ✅ Real Exa Search API calls via `https://api.exa.ai/search` |
| `backend/app/competitors/engine.py` | ✅ Competitor output marks whether it is based on latest research competitors |

Validation environment note:
- No provider API keys were present in container env or local `.env`.
- Ollama was not reachable at `http://host.docker.internal:11434`.
- Fake-key calls confirmed real request paths fail safely without leaking secrets.

### Iteration 10.1 ⚠ OpenAI Env-Key Fix Attempt

Attempted on 2026-05-19. Phase 1 stopped before Exa/frontend because OpenAI validation did not pass.

Implemented:
- `OPENAI_API_KEY` and `EXA_API_KEY` added to settings.
- `provider=openai` now uses request `api_key` first, then `OPENAI_API_KEY` from backend environment.
- `openai_compatible` still requires request key/base URL and does not force the OpenAI env key.
- OpenAI-compatible payload reduced to minimal `model` + `messages`.
- Provider errors now expose provider/model/status/body without exposing API keys.
- Safe provider log added for provider/model/status code only.
- Exa provider can read `EXA_API_KEY` from environment and accepts `num_results`.

Validation blocker:
- Root `.env` visible to this run contained Postgres settings but did not contain `OPENAI_API_KEY` or `EXA_API_KEY` entries.
- Backend container confirmed `OPENAI_API_KEY=false` and `EXA_API_KEY=false`.
- Required OpenAI validation returned:

```json
{
  "success": false,
  "data": null,
  "message": "openai provider failed: status=missing_api_key model=gpt-4o-mini body=api_key_required"
}
```

Per Iteration 10.1 rules, Exa validation and frontend work were not started.

### Iteration 10.1 Continuation ⚠ OpenAI Live Key Reached, Quota Blocker

Continued on 2026-05-19 after root `.env` was updated.

Validation:
- Backend container confirmed `OPENAI_API_KEY=true` and `EXA_API_KEY=true`.
- Docker services healthy; backend port remained `18000 -> 8000`.
- Required OpenAI request used no request-body key.
- OpenAI provider made a real request using `.env` key.

Result:

```json
{
  "success": false,
  "data": null,
  "message": "openai provider failed: status=429 model=gpt-4o-mini body={ \"error\": { \"message\": \"You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.\", \"type\": \"insufficient_quota\", \"param\": null, \"code\": \"insufficient_quota\" } }"
}
```

### Iteration 10.2 / 11 ✅ OpenRouter + Exa Live + Minimal Frontend MVP

Completed on 2026-05-19 after `OPENROUTER_API_KEY` and `EXA_API_KEY` were present in root `.env`.

Backend changes:
- Added `OPENROUTER_API_KEY` to settings.
- `provider=openrouter` now uses request `api_key` first, then `OPENROUTER_API_KEY` from backend environment.
- OpenRouter validation succeeded with no request-body key:
  - provider: `openrouter`
  - model: `deepseek/deepseek-chat`
  - `provider_used=openrouter`
  - zh-CN business plan sections returned Chinese content.
- Improved AI JSON parsing to accept strict `{"sections":[...]}` output and section-key JSON such as `{"project_overview":"..."}`.
- Switched Exa research provider from raw HTTP to official `exa_py` SDK.
- Added `exa-py==1.8.9` to backend Docker requirements.
- Added `research_config.type` support for Exa search types such as `auto`.
- Exa validation succeeded with no request-body key:
  - `provider_used=exa`
  - citations contained real URLs from Exa results.

Frontend changes:
- Added minimal `frontend/` Next.js + Tailwind + shadcn-style local UI.
- Frontend runs at `http://localhost:3000`.
- Frontend calls backend only at `http://127.0.0.1:18000`.
- No API keys are included in frontend code.
- Flow: idea → project → finance → Exa research → frameworks → OpenRouter business plan → review → DOCX/PDF export.

Validation:
- `docker compose up -d --build` ✅
- `docker compose exec backend python -m compileall app` ✅
- `docker compose exec backend alembic -c alembic.ini upgrade head` ✅
- Runtime booleans: `OPENROUTER_API_KEY=true`, `EXA_API_KEY=true` ✅
- OpenRouter BP validation ✅
- Exa research validation ✅
- `npm install` in `frontend/` ✅
- `npm run build` in `frontend/` ✅
- `npm run dev` started at `http://localhost:3000` ✅
- Frontend homepage returned HTTP 200 ✅

### Iteration 12 ✅ Business Plan Writing Workstation

Completed on 2026-05-19.

Backend changes:
- Added Final BP assembly behavior through the existing business plan service.
- Final BP reads project, latest Finance Pro forecast, latest Exa research, latest framework analysis, and latest review score.
- Challenge Cup / Internet+ presets now include a complete competition-style chapter order.
- Financial chapter is mandatory when finance exists and is titled `财务分析`.
- Added `backend/app/finance/narrative.py` to transform Finance Pro JSON into readable Chinese BP subsections:
  - 收入预测
  - 成本结构
  - 利润表
  - 现金流量表
  - 资产负债表
  - 盈亏平衡分析
  - 融资需求
  - 估值分析 with NPV / IRR / DCF / ROI
  - 敏感性分析
- Added `backend/app/services/language_service.py` to clean raw Exa prefixes and detect English body contamination.
- Research output is normalized before storage so Exa snippets do not enter BP/export as raw English paragraphs.
- Review language validator now flags raw Exa snippets and English body paragraphs via language service.
- DOCX export now inserts python-docx tables for:
  - 利润表
  - 现金流量表
  - 资产负债表
  - 敏感性分析
- PDF export includes financial summary and basic financial tables.
- Added `POST /projects/{project_id}/sections/polish`.
- Section polish uses OpenRouter from backend `.env`; no request-body API key is required.
- Section polish supports: `polish`, `expand`, `shorten`, `challenge_cup_style`, `internet_plus_style`, `fix_language_mixing`.

Frontend changes:
- Replaced button demo with a document writing workstation at `http://localhost:3000`.
- Layout:
  - left: project input + chapter tree
  - center: editable section textarea + AI suggestion apply/append controls
  - right: generation flow, AI actions, final confirmation checklist, export links, run log
- Frontend calls backend only and contains no provider keys.

Validation:
- `docker compose up -d --build` ✅
- `docker compose exec backend python -m compileall app` ✅
- `docker compose exec backend alembic -c alembic.ini upgrade head` ✅
- OpenRouter final BP generation succeeded with `provider_used=openrouter` ✅
- Exa research succeeded with `provider_used=exa` and real citation URLs ✅
- AI section polish endpoint succeeded ✅
- DOCX/PDF export succeeded ✅
- DOCX text check confirmed: `财务分析`, `收入预测`, `利润表`, `现金流量表`, `资产负债表`, `盈亏平衡分析`, `融资需求`, `NPV`, `IRR`, `DCF`, `敏感性分析` ✅
- Language check confirmed no raw `Summary:`, `This page markets`, or `Key features:` in generated BP/DOCX ✅
- `npm run build` in `frontend/` ✅
- `http://localhost:3000` returned HTTP 200 ✅
- Frontend page contains chapter tree, section editor, AI assistant actions, final confirmation, and export area ✅

### Iteration 14 ✅ Collaborative Planning Workspace + Assumption-Driven Finance

Completed on 2026-05-19.

Backend changes:
- Added `project_financial_assumptions` table and model.
- Added `document_blocks` table and model for editable workspace blocks.
- Added `section_comments` table and model for comment threads and resolve status.
- Added Alembic migration `0005_assumptions_blocks_comments.py`.
- Added financial assumption endpoints:
  - `POST /projects/{project_id}/finance/assumptions`
  - `GET /projects/{project_id}/finance/assumptions`
  - `PATCH /projects/{project_id}/finance/assumptions`
- Finance forecasts now require confirmed user assumptions; direct forecast generation without confirmed assumptions returns 400.
- Negative assumptions are rejected by schema validation.
- Extreme growth rates return warnings instead of silently passing.
- Saving confirmed assumptions immediately recalculates forecast.
- Added `backend/app/finance/interpreter.py` to explain break-even, NPV, IRR, DCF, ROI, funding pressure, risks, strengths, and recommendations from computed numbers only.
- Added `backend/app/finance/charts.py` using matplotlib to generate revenue, cash, cost structure, and sensitivity chart PNGs.
- Added document workspace endpoints:
  - `GET /projects/{project_id}/document/blocks`
  - `PATCH /projects/{project_id}/document/autosave`
- Added comment endpoints:
  - `POST /projects/{project_id}/sections/{section_id}/comment`
  - `GET /projects/{project_id}/sections/{section_id}/comments`
  - `PATCH /projects/{project_id}/comments/{comment_id}/resolve`
- Final BP generation syncs sections into editable document blocks.
- DOCX export now includes financial assumptions, tables, interpretation, citations, and chart images.
- Review scoring changed from average-based scoring to transparent weighted deductions.
- Incomplete project validation now scores low instead of >90.

Frontend changes:
- Reworked `frontend/app/page.tsx` into a collaborative infinite document workspace.
- Added financial assumption panel with required startup inputs.
- Added instant recalculation after assumptions are saved.
- Added editable document blocks for research, market, competitor, SWOT, finance, funding, risk, social value, and appendix.
- Added autosave every 5 seconds.
- Added section comments with resolve flow.
- Added undo, redo, duplicate block, move section, collapse section, search, Cmd+S, and Cmd+K.
- Added final export checklist and low-score export warning.

Validation:
- `docker compose up -d --build` ✅
- `docker compose exec backend python -m compileall app` ✅
- `docker compose exec backend alembic -c alembic.ini upgrade head` ✅
- Missing assumptions blocked forecast with 400 ✅
- Negative assumption rejected with 422 ✅
- Extreme growth rate returned warning ✅
- Assumptions save recalculated forecast and returned interpretation ✅
- Chart files generated: revenue, cash, cost structure, sensitivity ✅
- Incomplete project score: `0` with transparent deductions ✅
- Complete project score: `95` before export, only export deduction remaining ✅
- Document blocks visible and autosave persisted after reload ✅
- Comment created and resolved ✅
- DOCX validation confirmed assumptions, finance tables, interpretation, NPV/IRR/DCF, citations, and 4 embedded chart images ✅
- Frontend build passed ✅
- `http://localhost:3000` shows financial assumption panel, document navigation, comments, and final export checklist ✅

---

## 5. Current API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/projects` | Create project |
| GET | `/projects` | List demo_user's projects |
| GET | `/projects/{project_id}` | Get project (404 if not found) |
| POST | `/projects/{project_id}/finance/forecast` | Generate + store 36-month forecast |
| GET | `/projects/{project_id}/finance/forecast` | Get latest forecast (404 if none) |
| POST | `/projects/{project_id}/business-plan` | Generate + store configurable localized business plan |
| GET | `/projects/{project_id}/business-plan` | Get latest business plan (404 if none) |
| POST | `/projects/{project_id}/research` | Generate + store mock research report with citations |
| GET | `/projects/{project_id}/research` | Get latest research report (404 if none) |
| POST | `/projects/{project_id}/frameworks/analyze` | Generate + store selected strategic framework analysis |
| GET | `/projects/{project_id}/frameworks/analysis` | Get latest framework analysis (404 if none) |
| POST | `/projects/{project_id}/review` | Score project consistency and store review |
| GET | `/projects/{project_id}/review` | Get latest project review (404 if none) |
| POST | `/projects/{project_id}/export/pdf` | Generate downloadable PDF startup package |
| POST | `/projects/{project_id}/export/docx` | Generate downloadable DOCX startup package |
| GET | `/projects/{project_id}/exports` | List available exports for project |
| GET | `/exports/{file_name}` | Download generated export file |

Host access note:
- Backend container serves port 8000 internally.
- Host access is `http://127.0.0.1:18000`.
- Do not change port mapping.

---

## 6. Finance Engine Spec

**Input** (`FinanceForecastCreate`):
- `starting_revenue` float ≥ 0 (default 0)
- `monthly_growth_rate` float 0–1 (default 0.08)
- `gross_margin` float 0–1 (default 0.7)
- `fixed_monthly_costs` float ≥ 0 (default 3000)
- `variable_cost_rate` float 0–1 (default 0.2)
- `starting_cash` float ≥ 0 (default 10000)
- `months` int 1–60 (default 36)
- `discount_rate` float ≥ 0 (default 0.1)
- `tax_rate` float 0–1 (default 0)
- `initial_investment` float ≥ 0 (default 0)
- `financing_amount` float ≥ 0 (default 0)

**Per-month row**: month, revenue, variable_costs, fixed_costs, total_costs, gross_profit, net_profit, cash_balance

**Finance Pro output**:
- `summary`
- `monthly_rows`
- `income_statement`
- `cash_flow_statement`
- `balance_sheet`
- `financing_needs`
- `break_even`
- `valuation` with NPV, IRR, ROI, DCF value
- `sensitivity_analysis`
- `markdown_tables`
- `csv_exports`
- `charts`

**Storage**: `finance_forecasts` table — `inputs` (JSON), `monthly_rows` (JSON list), `summary` (JSON full forecast payload)

---

## 7. Business Plan Spec

**Input**: optional request body. Requires existing project and latest finance forecast.

**Provider**: request-scoped AI provider config. `mock` remains default.

**Request shape**:

```json
{
  "language": "zh-CN",
  "template_type": "internet_plus",
  "sections": ["project_overview", "market_analysis", "business_model"],
  "ai_config": {
    "provider": "mock",
    "api_key": null,
    "model": null,
    "base_url": null,
    "fallback_to_mock": true
  }
}
```

**Language modes**:
- `zh-CN` default
- `en-US`

**Template modes**:
- `generic_startup`
- `challenge_cup`
- `internet_plus`
- `custom`

**Storage**: no migration. Existing `business_plans.sections` JSON stores:
- `language`
- `template_type`
- `selected_sections`
- ordered `sections` list with `key`, `heading`, `content`

**Custom behavior**:
- Uses only user-provided sections.
- Preserves exact user order.
- Does not auto-add missing sections.
- Does not reorder sections.

**Framework section keys supported in business plan/export**:
- `swot_analysis`
- `pest_analysis`
- `porter_five_forces`
- `business_model_canvas`
- `tam_sam_som`
- `risk_matrix`

Requires latest framework analysis for populated framework content.

---

## 8. Research Report Spec

**Input**: optional `ai_config` body. Requires existing project owned by `demo_user`.

**Provider**: research provider layer supports `mock`, `exa`, `tavily`, `serpapi`.

**Request shape**:

```json
{
  "ai_config": {"provider": "mock"},
  "research_config": {
    "provider": "mock",
    "api_key": null,
    "fallback_to_mock": true
  }
}
```

`exa` is a provider shell for gradual replacement of mock research. `tavily` and `serpapi` are reserved future providers. No live external search is performed yet.

**Stored/returned fields**:
- `provider_used = "mock_research"`
- `summary`
- `market_size`
- `industry_trends`
- `competitors`
- `risks`
- `opportunities`
- `citations`

**Citation format**:

```json
{
  "title": "...",
  "source": "...",
  "url": "...",
  "source_type": "government|institution|company|report|news"
}
```

Current citations are stable placeholder sources and do not imply live browsing.

---

## 9. Framework Engine Spec

**Input** (`FrameworkAnalysisRequest`):

```json
{
  "language": "zh-CN",
  "frameworks": ["swot", "pest", "porter_five_forces", "business_model_canvas"],
  "ai_config": {"provider": "mock"}
}
```

**Defaults**: if `frameworks` is omitted, generate `swot`, `pest`, `porter_five_forces`, and `business_model_canvas`.

**Supported frameworks**:
- `swot`
- `pest`
- `porter_five_forces`
- `business_model_canvas`
- `tam_sam_som`
- `stp`
- `marketing_4p`
- `value_chain`
- `risk_matrix`
- `competitor_matrix`
- `growth_strategy`
- `funding_suggestion`

**zh-CN rule**: all framework labels and analysis body text must be Chinese. English is allowed only for framework formulas/abbreviations such as SWOT, PEST, TAM, SAM, SOM.

**Storage**: `framework_analyses` table — `project_id`, `language`, `frameworks` JSON, timestamps.

---

## 10. Research Provider Layer Spec

**Supported research providers**:
- `mock`
- `exa`
- `tavily` future placeholder
- `serpapi` future placeholder

**Default**: `mock`.

**Security rules**:
- API keys are request-scoped only.
- API keys are never stored in DB.
- Provider errors are masked.
- Future providers fall back to mock when `fallback_to_mock=true`.

**Current behavior**:
- `mock`: deterministic static credible-style research.
- `exa`: real Exa Search API integration. Requires request-scoped Exa API key.
- `tavily` / `serpapi`: reserved provider names for future integration.

---

## 11. Lightweight Competitor Engine Spec

**Implemented framework key**: `competitor_matrix`.

**Output shape**:
- `competitor_matrix`: competitor, positioning, pricing, strengths, weaknesses, differentiation
- `market_gap`
- `recommended_positioning`

**Source of competitors**: latest research report competitors list, with deterministic fallback competitors.

**Marketing/Funding placeholders**:
- `marketing_4p`
- `stp`
- `growth_strategy`
- `funding_suggestion`

These remain lightweight structured outputs, not full agent workflows.

---

## 12. AI Provider Layer Spec

**Supported providers**:
- `mock`
- `openai`
- `anthropic`
- `deepseek`
- `qwen`
- `moonshot`
- `openrouter`
- `ollama`
- `openai_compatible`

**Default**: `mock`.

**Security rules**:
- API keys are request-scoped only.
- API keys are never stored in DB.
- API keys are never logged by application code.
- Provider errors return masked messages such as `AI provider unavailable`.
- OpenAI-compatible providers perform real HTTP calls to `/chat/completions`.
- Ollama uses `http://host.docker.internal:11434/v1/chat/completions` and does not require an API key.
- If not configured and `fallback_to_mock=true`, provider selection falls back to mock before generation.

**Default provider mappings**:
- `openai`: `https://api.openai.com/v1`, model `gpt-4o-mini`
- `deepseek`: `https://api.deepseek.com/v1`, model `deepseek-chat`
- `qwen`: `https://dashscope.aliyuncs.com/compatible-mode/v1`, model `qwen-plus`
- `moonshot`: `https://api.moonshot.cn/v1`, model `moonshot-v1-8k`
- `openrouter`: `https://openrouter.ai/api/v1`, model `openai/gpt-4o-mini`
- `ollama`: `http://host.docker.internal:11434/v1`, model `qwen2.5`

---

## 13. Consistency Review Spec

**Endpoint**:
- `POST /projects/{project_id}/review`
- `GET /projects/{project_id}/review`

**Reads**:
- project
- latest finance forecast
- latest research report
- latest framework analysis
- latest business plan
- local export files

**Returns**:

```json
{
  "overall_score": 84,
  "dimensions": {
    "finance": 80,
    "market": 75,
    "logic": 90,
    "evidence": 70,
    "language": 100,
    "template": 100,
    "export": 92
  },
  "warnings": [],
  "critical_conflicts": [],
  "suggestions": []
}
```

**Checks**:
- Market ↔ Finance
- Finance ↔ Funding
- Research ↔ Conclusion
- Team ↔ Execution
- Language consistency
- Template integrity
- Export integrity

**Storage**: `project_reviews` table — `project_id`, `score` JSON, timestamps.

---

## 14. Export Spec

**Input**: optional `{ "include_review": true }`. Requires existing project owned by `demo_user` and latest finance forecast, business plan, and research report.

**Formats**:
- PDF generated with `reportlab`
- DOCX generated with `python-docx`

**Stored under**:
- `backend/exports/`

**Filename format**:
- `{project_id}_{timestamp}.pdf`
- `{project_id}_{timestamp}.docx`

**Sections included**:
- Title page: localized project title, generated date, Venture Copilot
- Only selected business plan sections
- Preserves selected section order
- Uses Chinese headings for `zh-CN`
- If `include_review=true` and a review exists, appends 项目评分 / 风险提示 / 改进建议

---

## 15. Database Schema

| Table | Key Columns |
|---|---|
| `users` | id, email, display_name, timestamps |
| `projects` | id, user_id, title, idea_summary, stage, timestamps |
| `team_members` | id, project_id, user_id, role, timestamps |
| `finance_forecasts` | id, project_id, inputs(JSON), monthly_rows(JSON), summary(JSON), timestamps |
| `business_plans` | id, project_id, provider_used, sections(JSON), timestamps |
| `research_reports` | id, project_id, provider_used, summary, market_size, industry_trends/competitors/risks/opportunities/citations (JSON), timestamps |
| `framework_analyses` | id, project_id, language, frameworks(JSON), timestamps |
| `project_reviews` | id, project_id, score(JSON), timestamps |

Migration 0002 adds Iteration 4 research fields to `research_reports`.
Migration 0003 adds Iteration 7 `framework_analyses`.
Migration 0004 adds Iteration 8 `project_reviews`.

---

## 16. Current Limitations

- `user_id = "demo_user"` hardcoded — no real auth
- Only latest forecast returned — no forecast history endpoint yet
- Only latest business plan returned — no business plan history endpoint yet
- Only latest research report returned — no research history endpoint yet
- Business plan generator is deterministic mock text only
- Research report generator is deterministic mock text only; no live web search
- Exa research provider requires a valid Exa API key for live results
- Tavily and SerpApi are reserved provider names only
- Framework engine is deterministic mock/structured analysis only; no external market intelligence yet
- Competitor engine is lightweight and deterministic; no live competitor discovery yet
- External AI provider classes perform real HTTP calls when a request-scoped key/base URL is provided
- Consistency review is deterministic heuristic scoring, not an expert audit
- Export files are local Docker/workspace files only; no cloud storage
- PDF/DOCX export follows latest generated business plan template and selected section order

---

## 17. Validation Snapshot

Validated on 2026-05-19 using Docker only:

- `docker compose up -d --build` ✅
- `docker compose ps` ✅
- `docker compose exec backend python -m compileall app` ✅
- `docker compose exec backend alembic -c alembic.ini upgrade head` ✅
- `GET /health` ✅
- `POST /projects` ✅
- `GET /projects` ✅
- `POST /projects/{project_id}/finance/forecast` with old body ✅
- `POST /projects/{project_id}/finance/forecast` with Finance Pro body ✅
- `GET /projects/{project_id}/finance/forecast` ✅
- `POST /projects/{project_id}/business-plan` ✅
- `POST /projects/{project_id}/business-plan` with `zh-CN` + `internet_plus` + selected sections ✅
- `POST /projects/{project_id}/business-plan` with `zh-CN` + `custom` + exact selected sections ✅
- `POST /projects/{project_id}/business-plan` with selected framework sections ✅
- `GET /projects/{project_id}/business-plan` ✅
- `POST /projects/{project_id}/research` ✅
- `POST /projects/{project_id}/research` with `research_config.provider=mock` ✅
- `POST /projects/{project_id}/research` with `research_config.provider=exa` ✅ provider shell; no live browsing
- `POST /projects/{project_id}/research` with future `tavily` + fallback ✅
- `GET /projects/{project_id}/research` ✅
- `POST /projects/{project_id}/frameworks/analyze` ✅
- `POST /projects/{project_id}/frameworks/analyze` with `competitor_matrix`, `growth_strategy`, `funding_suggestion`, `marketing_4p`, `stp` ✅
- `GET /projects/{project_id}/frameworks/analysis` ✅
- `POST /projects/{project_id}/business-plan` with `ai_config.provider=mock` ✅
- `POST /projects/{project_id}/business-plan` with `ai_config.provider=openai` + missing key + fallback ✅
- `POST /projects/{project_id}/business-plan` with invalid provider ✅ masked 400; API key not leaked
- `POST /projects/{project_id}/business-plan` with fake OpenAI key + fallback disabled ✅ real HTTP path attempted; masked failure; fake key not leaked
- `POST /projects/{project_id}/business-plan` with provider=openai and no request key ⚠ stopped: backend env missing `OPENAI_API_KEY`
- `POST /projects/{project_id}/business-plan` with provider=openai and env key present ⚠ real OpenAI call reached API but failed with `429 insufficient_quota`
- `POST /projects/{project_id}/research` with fake OpenAI key + fallback disabled ✅ real HTTP path attempted; masked failure; fake key not leaked
- `POST /projects/{project_id}/frameworks/analyze` with fake OpenAI key + fallback disabled ✅ real HTTP path attempted; masked failure; fake key not leaked
- `POST /projects/{project_id}/research` with fake Exa key + fallback disabled ✅ real Exa path attempted; masked failure; fake key not leaked
- Ollama reachability check from container ❌ `host.docker.internal:11434` was not reachable in current environment
- `POST /projects/{project_id}/review` ✅
- `GET /projects/{project_id}/review` ✅
- Finance inconsistency scenario ✅ critical conflict generated
- Language inconsistency scenario ✅ warning generated
- `POST /projects/{project_id}/export/docx` with `include_review=true` ✅
- `POST /projects/{project_id}/export/pdf` ✅
- `POST /projects/{project_id}/export/docx` ✅
- `GET /projects/{project_id}/exports` ✅
- `GET /exports/{file_name}` ✅

Errors fixed during validation:

- Restored empty `backend/alembic.ini` with valid Alembic config.
- Restored migration content into `backend/alembic/versions/0001_initial_schema.py`.
- Removed stray `backend/alembic/scrip` and empty `backend/alembic/ini.py`.
- Removed host port exposure for Postgres/Redis to avoid conflicts with other local containers.
- Mapped backend host port to `18000` because host IPv4 port `8000` was occupied by another local Python service.
- Added model-level `Project.user_id` foreign key and `Project.owner` relationship so SQLAlchemy can configure `User.projects`.
- Added global HTTPException handling so 400/404 responses use the standard `{"success", "data", "message"}` envelope.
- Added 0002 migration because the existing `research_reports` table was incompatible with the required Iteration 4 output shape.
- Added `reportlab` and `python-docx` to Docker requirements for Iteration 5 export generation.
- Registered DOCX MIME type so downloaded Word files are served with the correct content type.
- Added Iteration 6 localization/templates without migration by storing structured metadata in `business_plans.sections`.
- Confirmed custom mode exports only selected Chinese sections in exact user-provided order.
- Added Iteration 7 Finance Pro without finance migration by storing the richer forecast payload in existing JSON fields.
- Added 0003 migration for `framework_analyses` because no existing flexible table was appropriate for persistent framework output.
- Replaced English mock research/body text for zh-CN flow and verified business plan/research/framework/DOCX body text has no English sentence-like paragraphs.
- Added Iteration 8 provider layer with request-scoped AI config and safe mock fallback.
- Added 0004 migration for `project_reviews` because reviews need a persisted latest score.
- Added consistency scoring validators and verified warnings/critical conflicts for language, team execution, export, and finance/funding issues.
- Added optional review appendix in DOCX/PDF export when `include_review=true`.
- Studied Exa Research, CompetitorAgent, and agency-agents reference repos; integrated only lightweight data structures and framework ideas.
- Added Iteration 9 research provider layer with mock/exa/future tavily/future serpapi support.
- Added lightweight competitor engine with competitor matrix, market gap, and recommended positioning.
- Added growth strategy and funding suggestion framework placeholders without new dependencies or migrations.
- Added Iteration 10 real OpenAI-compatible HTTP provider calls for BP/research/framework generation.
- Added real Exa Search API call path for research with citations.
- Added Ollama provider mapping for qwen2.5/deepseek-r1/llama3/mistral-compatible local models via request `model`.
- Added Iteration 10.1 env-key lookup and exact provider error propagation; stopped at OpenAI validation because runtime env did not contain `OPENAI_API_KEY`.

---

## 18. Folder Structure

```
venture-copilot/
├── docs/
│   └── CLAUDE_MEMORY.md
├── frontend/
│   ├── app/
│   ├── components/ui/
│   ├── lib/
│   ├── package.json
│   └── tailwind.config.ts
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 0001_initial_schema.py
│   │       ├── 0002_research_report_fields.py
│   │       ├── 0003_framework_analyses.py
│   │       └── 0004_project_reviews.py
│   ├── app/
│   │   ├── ai/base.py
│   │   ├── ai/provider_factory.py
│   │   ├── ai/providers/
│   │   ├── api/routes/
│   │   │   ├── health.py
│   │   │   ├── projects.py
│   │   │   ├── finance.py
│   │   │   ├── business_plan.py
│   │   │   ├── research.py
│   │   │   └── export.py
│   │   ├── core/
│   │   ├── finance/engine.py
│   │   ├── competitors/engine.py
│   │   ├── frameworks/engine.py
│   │   ├── research/
│   │   ├── templates/business_plan_templates.py
│   │   ├── models/
│   │   ├── schemas/
│   │   │   ├── project.py
│   │   │   ├── finance.py
│   │   │   ├── business_plan.py
│   │   │   ├── template.py
│   │   │   ├── research.py
│   │   │   ├── framework.py
│   │   │   ├── review.py
│   │   │   └── export.py
│   │   ├── services/
│   │   │   ├── project_service.py
│   │   │   ├── finance_service.py
│   │   │   ├── business_plan_service.py
│   │   │   ├── template_service.py
│   │   │   ├── research_service.py
│   │   │   ├── framework_service.py
│   │   │   ├── review_service.py
│   │   │   └── export_service.py
│   │   ├── validators/
│   │   └── main.py
│   ├── exports/
│   ├── Dockerfile, requirements.txt, alembic.ini
└── docker-compose.yml
```

---

## 19. MVP Status

MVP complete.

Verified user flow:

- Create project
- Generate finance forecast
- Generate business plan
- Generate localized challenge_cup / internet_plus / custom business plan
- Generate mock research report with citations
- Generate Finance Pro forecast with financial statements, valuation, sensitivity, markdown/CSV/chart-ready data
- Generate Chinese strategic frameworks and include selected frameworks in business plan/export
- Select request-scoped AI provider config with safe mock fallback
- Select request-scoped research provider config with safe mock/future-provider fallback
- Generate lightweight competitor matrix, market gap, recommended positioning, growth strategy, and funding suggestion
- Generate live OpenRouter business plan content using backend `.env` key
- Generate live Exa research citations using backend `.env` key
- Run deterministic consistency review and project scoring
- Export PDF/DOCX with optional project score appendix
- Export PDF
- Export DOCX
- List and download exports
- Use minimal local frontend at `http://localhost:3000`

---

## 20. Do-Not-Change Rules

🔒 Never change Docker service names: `backend`, `postgres`, `redis`
🔒 Never change Docker network name: `venture-net`
🔒 Never change port mapping: host `18000` → container `8000`
🔒 Never add a frontend Docker service unless explicitly requested
🔒 Never use local Python environment
🔒 Real AI/web providers must remain request-scoped and must never store API keys
🔒 No scraping, RAG, or vector DB unless explicitly requested
🔒 Never store raw AI prompt content in logs
🔒 Never store full-text copyrighted content in DB
🔒 Always use citation schema: `{title, source, url, source_type}`
🔒 Always scope queries to `project_id` + `user_id`
🔒 Always return `{"success", "data", "message"}` envelope
