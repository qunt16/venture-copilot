# Venture Copilot — Product Specification

## Product Name
**Venture Copilot**

## Tagline
Finance-first AI business planning platform for university startup teams.

---

## Problem

University startup teams waste weeks building business plans manually:
- Inconsistent financial models built in Excel with no validation
- Research sections with no citations or sourcing
- Generic business plans that don't reflect real market data
- No structured workflow from idea → investor-ready document

---

## Solution

A backend API platform that takes a startup idea and generates:
1. A **36-month financial forecast** with deterministic modelling
2. A **research report** with market data and citations
3. A **structured business plan** using AI generation
4. A **markdown export** ready for polishing or further processing

---

## Target Users

- University entrepreneurship teams
- Student startup founders
- Incubator programme participants
- Early-stage pre-seed teams

---

## Core Features (P0)

| Feature                  | Description                                                       |
|--------------------------|-------------------------------------------------------------------|
| Project management       | Create and manage startup project records                         |
| Finance Engine           | 36-month deterministic forecast with break-even and runway        |
| Research report          | Market size, competitors, risks, opportunities — all cited        |
| Business plan generation | 10-section AI-generated plan tied to project + finance + research |
| Markdown export          | Full project export as a single structured `.md` file             |
| AI provider abstraction  | Swap between Mock / Claude / OpenAI via env var                   |
| Multi-tenant design      | Project-level isolation; role-based team membership               |

---

## P1 Features (Iteration 4)

| Feature              | Description                               |
|----------------------|-------------------------------------------|
| PDF export           | Render markdown to PDF                    |
| Basic permissions    | Enforce owner / editor / viewer roles     |
| Structured logging   | structlog JSON logs per request           |
| Error handling       | Consistent error envelope across API      |
| Deployment docs      | Docker production deployment guide        |

---

## Out of Scope (MVP)

- Frontend / UI / Next.js
- Real-time collaboration
- Payment processing
- Mobile app
- Mentor / coaching system
- PowerPoint generation
- Complex web scraping

---

## Business Plan Sections (AI-generated)

1. Executive Summary
2. Problem Statement
3. Solution
4. Target Market
5. Business Model
6. Competitive Analysis
7. Financial Forecast (sourced from Finance Engine)
8. Risks & Mitigations
9. Funding Need & Use of Funds
10. Implementation Plan (12-month roadmap)

---

## Finance Engine Inputs

| Field                  | Type    | Description                        |
|------------------------|---------|------------------------------------|
| industry               | string  | e.g. "EdTech", "FinTech"          |
| business_model         | string  | e.g. "SaaS", "Marketplace"        |
| initial_users          | int     | Users at month 1                   |
| monthly_growth_rate    | float   | e.g. 0.10 = 10% MoM growth        |
| conversion_rate        | float   | Free → paid conversion             |
| arpu                   | float   | Average revenue per paying user/mo |
| fixed_costs            | float   | Monthly fixed overhead             |
| variable_cost_per_user | float   | Cost per active user per month     |
| marketing_cost         | float   | Monthly marketing spend            |
| starting_cash          | float   | Initial cash balance               |

---

## Finance Engine Outputs (per month × 36)

| Field            | Description                          |
|------------------|--------------------------------------|
| month            | Month number (1–36)                  |
| monthly_users    | Total active users                   |
| paying_users     | Converted paying users               |
| monthly_revenue  | ARPU × paying_users                  |
| fixed_costs      | Fixed overhead                       |
| variable_costs   | variable_cost_per_user × users       |
| marketing_costs  | Marketing spend                      |
| gross_profit     | Revenue − variable costs             |
| net_profit       | Revenue − all costs                  |
| cash_balance     | Cumulative cash                      |

### Summary Metrics

- `total_revenue` — sum of all monthly revenue
- `total_net_profit` — sum of all monthly net profit
- `break_even_month` — first month net_profit > 0
- `funding_need` — lowest cash_balance (negative = funding gap)
- `runway_months` — months until cash = 0

---

## Research Report Structure

```json
{
  "market_size": "Global EdTech market valued at $X billion (2024)",
  "competitors": [
    { "name": "Competitor A", "description": "...", "weakness": "..." }
  ],
  "risks": ["Regulatory risk", "Competition risk"],
  "opportunities": ["Post-COVID digital adoption", "University partnerships"],
  "citations": [
    {
      "title": "Global EdTech Market Report 2024",
      "source": "Statista",
      "url": "https://statista.com/...",
      "date": "2024-01"
    }
  ]
}
```
