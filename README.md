# venture-copilot

> Finance-first AI business planning platform for university startup teams.

---

## What is this?

A backend API that takes a startup idea and generates:
1. **36-month financial forecast** — deterministic projections across revenue, costs, profit, runway
2. **Research report with citations** — market size, competitors, risks, opportunities
3. **Business plan** — 10-section structured document via AI provider abstraction
4. **Markdown export** — portable output for presentations, docs, pitch decks

---

## Quick start

> ⚠️ **All commands must be run via Docker. No pip, no python, no local environments.**

### 1. Clone and configure

```bash
git clone <repo>
cd venture-copilot
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD, SECRET_KEY, and AI keys
```

### 2. Build containers

```bash
docker compose build
```

### 3. Start services

```bash
docker compose up
```

### 4. Verify health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "service": "venture-copilot-backend", "version": "0.1.0"}
```

### 5. View API docs

Open: http://localhost:8000/docs

---

## Docker commands reference

| Action | Command |
|---|---|
| Build images | `docker compose build` |
| Start all services | `docker compose up` |
| Start detached | `docker compose up -d` |
| Stop all | `docker compose down` |
| Stop + remove volumes | `docker compose down -v` |
| View logs | `docker compose logs -f` |
| Backend logs only | `docker compose logs -f backend` |
| Open backend shell | `docker compose exec backend bash` |
| Run migrations | `docker compose exec backend alembic upgrade head` |
| Check DB | `docker compose exec postgres psql -U vc_user -d venture_copilot` |

---

## Services

| Service | Port | Description |
|---|---|---|
| backend | 8000 | FastAPI application |
| postgres | 5432 | PostgreSQL 15 database |
| redis | 6379 | Redis 7 cache / queue |

---

## API overview

```
GET  /health                                  Health check
POST /projects                                Create project
GET  /projects                                List projects
GET  /projects/{id}                           Get project
POST /projects/{id}/finance                   Generate financial forecast
POST /projects/{id}/research                  Generate research report
POST /projects/{id}/business-plan            Generate business plan
GET  /projects/{id}/export/markdown          Export as Markdown
```

Full interactive docs: http://localhost:8000/docs

---

## Project structure

```
venture-copilot/
├── docs/                   Architecture, specs, memory
├── backend/
│   ├── app/
│   │   ├── api/            Route handlers
│   │   ├── core/           Config, DB, Redis
│   │   ├── models/         SQLAlchemy ORM models
│   │   ├── schemas/        Pydantic schemas
│   │   ├── services/       Business logic
│   │   ├── finance/        Finance engine
│   │   ├── research/       Research service
│   │   ├── ai/             AI provider abstraction
│   │   ├── security/       Auth, permissions
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Forbidden

The following are **never** used in this project:

- `pip install` (on host)
- `python` (on host)
- `uvicorn` (on host)
- `venv` / `.venv` / `conda`
- Any frontend framework

Everything runs in Docker.

---

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Product Spec](docs/PRODUCT_SPEC.md)
- [Data Security](docs/DATA_SECURITY.md)
- [Copyright Policy](docs/COPYRIGHT_POLICY.md)
