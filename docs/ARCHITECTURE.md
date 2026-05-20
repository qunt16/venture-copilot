# Venture Copilot — Architecture

## Overview

Venture Copilot is a **backend-only**, finance-first AI business planning platform for university startup teams. It is designed as a future multi-tenant SaaS, built with project-level data isolation from day one.

---

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐  ┌─────────────┐  │
│  │   FastAPI    │   │  PostgreSQL  │  │    Redis    │  │
│  │  (Backend)   │──▶│     :5432    │  │    :6379    │  │
│  │   :8000      │   └──────────────┘  └─────────────┘  │
│  └──────┬───────┘                                       │
│         │                                               │
└─────────┼───────────────────────────────────────────────┘
          │
    External Clients
    (REST API calls)
```

---

## Service Breakdown

| Service   | Image              | Role                                      |
|-----------|--------------------|-------------------------------------------|
| backend   | python:3.11-slim   | FastAPI app, all business logic           |
| postgres  | postgres:15-alpine | Primary data store                        |
| redis     | redis:7-alpine     | Caching, task queuing (future Celery)     |

---

## Module Structure

```
backend/app/
├── api/          # Route handlers (thin layer — validation + delegation only)
├── core/         # Config, DB session, settings, startup hooks
├── models/       # SQLAlchemy ORM models (DB schema)
├── schemas/      # Pydantic schemas (request/response contracts)
├── services/     # Business logic (projects, business plan assembly)
├── finance/      # Finance engine (36-month deterministic forecasting)
├── research/     # Research service (citation-based market research)
├── ai/           # AI provider abstraction (Mock, Claude, OpenAI)
└── security/     # Auth, permissions, RBAC (placeholder → real in future)
```

---

## Data Flow — Business Plan Generation

```
POST /projects/{id}/finance   →  FinanceEngine.run()  →  FinanceForecast stored
POST /projects/{id}/research  →  ResearchService.run() →  ResearchReport stored
POST /projects/{id}/business-plan  →  AIProvider.generate()  →  BusinessPlan stored
GET  /projects/{id}/export/markdown  →  ExportService.render()  →  .md file
```

---

## AI Provider Abstraction

```python
class AIProvider(ABC):
    async def generate_business_plan(self, context: PlanContext) -> BusinessPlanContent: ...

class MockProvider(AIProvider): ...      # deterministic, used in dev/test
class ClaudeProvider(AIProvider): ...   # Anthropic API
class OpenAIProvider(AIProvider): ...   # OpenAI API
```

Provider is selected via `AI_PROVIDER` environment variable. No provider is hardcoded.

---

## Database Design Principles

- Every resource is scoped to a `project_id`
- Every project has an `owner_id` (future: real user UUID)
- `TeamMember` table enforces `owner | editor | viewer` roles
- `created_at` / `updated_at` on all tables for audit trail
- Soft-delete pattern planned for GDPR compliance

---

## Security Posture (MVP → Production Path)

| Concern            | MVP State              | Production Target              |
|--------------------|------------------------|--------------------------------|
| Authentication     | `demo_user` placeholder | JWT + OAuth2                  |
| Authorization      | Role enum in DB        | Middleware enforcement         |
| Secrets            | `.env` file            | Vault / AWS Secrets Manager   |
| Data isolation     | `owner_id` on all rows | Row-level security in Postgres |
| Encryption at rest | Not implemented        | AES-256 for sensitive docs     |

---

## Iteration Plan

| # | Scope                                                     | Status      |
|---|-----------------------------------------------------------|-------------|
| 0 | Infrastructure, Docker, docs, memory system               | ✅ Complete |
| 1 | FastAPI + DB models + Project CRUD                        | ⏳ Next     |
| 2 | Finance Engine + finance endpoint + storage               | 🔲 Pending  |
| 3 | Research service + AI adapter + business plan generation  | 🔲 Pending  |
| 4 | Export + permissions + logging + error handling + deploy  | 🔲 Pending  |
