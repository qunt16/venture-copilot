# Venture Copilot — Data Security Policy

## Design Principle

Venture Copilot is designed for future multi-tenant SaaS operation.
Every architectural decision in the MVP must be compatible with production-grade security.

---

## Data Isolation

### Project-Level Isolation
- Every data record (forecasts, reports, plans) is scoped to a `project_id`
- Every project is owned by an `owner_id`
- No cross-project data leakage is permitted at the query layer
- All service methods accept and enforce `project_id` as a required parameter

### Team-Level Access Control
- `TeamMember` table defines roles: `owner | editor | viewer`
- Role checks must be enforced in the service layer before any data mutation
- In MVP: roles stored in DB but not yet middleware-enforced (Iteration 4)

---

## Authentication & Authorisation

### MVP State
- `user_id = "demo_user"` placeholder for all requests
- No JWT validation in MVP
- Roles stored in DB, enforcement added in Iteration 4

### Production Target
- JWT tokens (python-jose) with short expiry
- OAuth2 compatible (university SSO)
- Row-level security in PostgreSQL as a second layer
- All endpoints require authenticated identity

---

## Secrets Management

| Secret              | MVP                   | Production                       |
|---------------------|-----------------------|----------------------------------|
| Database password   | `.env` file           | AWS Secrets Manager / Vault      |
| AI provider API key | `.env` file           | Injected via CI/CD secret        |
| App secret key      | `.env` file           | Rotated, externally managed      |

**Rules:**
- `.env` is **never committed to version control** (gitignored)
- `.env.example` is committed with placeholder values only
- No secrets hardcoded in source code

---

## Data at Rest

### MVP
- PostgreSQL data stored in Docker volume (`postgres_data`)
- No encryption at rest in MVP

### Production Target
- Encrypt sensitive columns (business plans, financial data) with AES-256
- Use PostgreSQL transparent data encryption or column-level encryption
- Encryption key stored in KMS, never in application code

---

## Data in Transit

- All production traffic behind HTTPS / TLS termination (load balancer or nginx)
- Internal Docker network traffic not encrypted (acceptable within single-host)
- External AI provider calls over HTTPS only (enforced by httpx defaults)

---

## GDPR Compliance Path

| Requirement              | MVP State              | Production Target                          |
|--------------------------|------------------------|--------------------------------------------|
| Right to erasure         | Not implemented        | Soft-delete + scheduled hard delete        |
| Data portability         | Markdown export        | JSON export of all project data            |
| Data minimisation        | Collect only what's needed | Audit quarterly                       |
| Consent                  | Not applicable (no UI) | Consent management on signup               |
| Data processing agreement | N/A (no users yet)   | DPA with AI provider (Anthropic / OpenAI)  |

---

## AI Provider Data Rules

- **No user data used for model training**
- Anthropic API: ensure "zero data retention" option is enabled in production
- OpenAI API: opt out of data training via API (default for API customers)
- Never log raw prompts containing user business plan content to external services
- All AI prompts treated as sensitive data

---

## Audit Trail

- All `create`, `update`, `delete` operations logged with `user_id`, `project_id`, timestamp
- `created_at` / `updated_at` on every model
- Future: dedicated audit log table with immutable append-only writes

---

## Cross-Tenant Contamination Prevention

- AI prompts must **never** include data from another team's project
- Each generation call sources data exclusively from its own `project_id`
- Integration tests must assert no data leaks between projects
- Future: prompt injection sanitisation before sending to AI providers

---

## Incident Response

- Any suspected data breach: immediately rotate all secrets, revoke tokens
- PostgreSQL: restore from last known clean backup
- Notify affected users within 72 hours (GDPR Article 33)
