# CLAUDE_MEMORY.md — venture-copilot

> **IMPORTANT**: Read this file at the start of every task before writing any code.  
> Update this file at the end of every task before stopping.

---

## 1. Product definition

**venture-copilot** is a finance-first AI business planning backend for university startup teams.

Core workflow:
```
startup idea → 36-month financial forecast → research report (cited) → business plan → export
```

It is a backend-only product. No frontend. No UI.

---

## 2. Architecture decisions

| Decision | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Async, typed, OpenAPI auto-docs |
| ORM | SQLAlchemy 2.0 | Async, mature |
| Migrations | Alembic | Standard SQLAlchemy companion |
| Validation | Pydantic v2 | FastAPI native |
| Database | PostgreSQL 15 | ACID, JSONB columns |
| Cache | Redis 7 | Fast, future task queue |
| Containers | Docker + Compose | Reproducible, clean host |
| AI layer | Custom ABC | Provider-agnostic, env-switched |
| Auth (MVP) | demo_user placeholder | Real JWT drop-in in Iteration 4 |

---

## 3. Environment rules (NON-NEGOTIABLE)

- **Never** create venv / .venv / conda / poetry local env
- **Never** run pip install on host
- **Never** run python or uvicorn on host
- **Everything** runs inside Docker containers
- **Dependencies** install only through Dockerfile
- **PostgreSQL** runs only in Docker
- **Redis** runs only in Docker
- **README** contains Docker-only commands

---

## 4. Completed modules

### Iteration 0 ✅

| File | Status |
|---|---|
| `docker-compose.yml` | ✅ Created |
| `backend/Dockerfile` | ✅ Created |
| `backend/.dockerignore` | ✅ Created |
| `backend/requirements.txt` | ✅ Created |
| `.env.example` | ✅ Created |
| `README.md` | ✅ Created |
| `backend/app/main.py` | ✅ Created (skeleton) |
| `backend/app/__init__.py` | ✅ Created |
| `backend/app/api/__init__.py` | ✅ Created |
| `backend/app/core/__init__.py` | ✅ Created |
| `backend/app/models/__init__.py` | ✅ Created |
| `backend/app/schemas/__init__.py` | ✅ Created |
| `backend/app/services/__init__.py` | ✅ Created |
| `backend/app/finance/__init__.py` | ✅ Created |
| `backend/app/research/__init__.py` | ✅ Created |
| `backend/app/ai/__init__.py` | ✅ Created |
| `backend/app/security/__init__.py` | ✅ Created |
| `docs/ARCHITECTURE.md` | ✅ Created |
| `docs/PRODUCT_SPEC.md` | ✅ Created |
| `docs/DATA_SECURITY.md` | ✅ Created |
| `docs/COPYRIGHT_POLICY.md` | ✅ Created |
| `docs/CLAUDE_MEMORY.md` | ✅ Created |

---

## 5. Modified files log

| Iteration | File | Change |
|---|---|---|
| 0 | All above | Initial creation |

---

## 6. Current limitations

- No database models — schema is documented only
- No API routes beyond `/health`
- No business logic (finance, research, AI)
- No authentication — demo_user placeholder not yet wired
- No migrations — Alembic not initialised
- MockProvider not implemented

---

## 7. Next task: Iteration 1

**Goal**: FastAPI + DB + models + project CRUD

**Tasks**:
1. Add `app/core/config.py` — pydantic-settings for env vars
2. Add `app/core/database.py` — SQLAlchemy async engine + session
3. Add `app/core/redis.py` — Redis client
4. Add `app/models/` — User, Project, TeamMember, FinanceForecast, ResearchReport, BusinessPlan
5. Add `app/schemas/project.py` — Pydantic request/response schemas
6. Add `app/api/projects.py` — CRUD route handlers
7. Register router in `main.py`
8. Initialise Alembic + create first migration
9. Update this file

**Do not implement**:
- Finance engine (Iteration 2)
- Research service (Iteration 3)
- AI provider (Iteration 3)
- Export (Iteration 4)

---

## 8. Do-not-change rules

- Never touch `docker-compose.yml` services structure without noting here
- Never rename database tables once created (breaks migrations)
- Never add a frontend
- Never add dependencies to requirements.txt without a clear reason
- Always preserve `owner_id` on all models (required for future auth)
- Always include `created_at` / `updated_at` on all models
- Always filter queries by `project_id` to preserve tenant isolation
- Citation objects must always include: title, source, url, date
