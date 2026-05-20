# Venture Copilot — Copyright & Data Policy

## Purpose

This document defines the rules governing how Venture Copilot collects, processes,
and presents third-party data in research reports and AI-generated content.

---

## Core Principle

Venture Copilot does **not** scrape, reproduce, or redistribute copyrighted content.
All research outputs are:
- Citation-based summaries (not full-text reproductions)
- Sourced from public APIs and open datasets
- Attributed with full citation metadata

---

## Permitted Data Sources

| Source Type                  | Permitted | Notes                                      |
|------------------------------|-----------|--------------------------------------------|
| Public government datasets   | ✅ Yes    | ONS, FRED, World Bank, etc.               |
| Open APIs (no login required)| ✅ Yes    | Must respect rate limits and ToS           |
| User-provided sources        | ✅ Yes    | User takes responsibility for their input  |
| Academic papers (abstracts)  | ✅ Yes    | Abstract only, not full paper text         |
| News articles (summary only) | ✅ Yes    | Headline + paraphrase, not full text       |
| Wikipedia / Wikidata         | ✅ Yes    | CC-BY-SA compatible                        |

---

## Prohibited Data Collection

| Source Type                      | Prohibited | Reason                               |
|----------------------------------|------------|--------------------------------------|
| Paid research databases          | ❌ Never   | Copyright and ToS violation          |
| Sites disallowing bots (robots.txt) | ❌ Never | ToS violation                       |
| Full-text news articles          | ❌ Never   | Copyright violation                  |
| Copyrighted reports (e.g. McKinsey) | ❌ Never | Copyright violation                 |
| Paywalled academic papers        | ❌ Never   | Copyright violation                  |
| Personal data without consent    | ❌ Never   | GDPR violation                       |

---

## Citation Requirements

Every factual claim in a research report **must** be linked to a citation object:

```json
{
  "title": "Name of the source document",
  "source": "Organisation or publication name",
  "url": "https://direct-url-to-source.com",
  "date": "YYYY-MM"
}
```

**Rules:**
- `url` must point to the original source, not a search engine result
- `date` should reflect publication or last-updated date
- Citations must be verifiable by the end user
- Do not fabricate citations — MockProvider uses clearly labelled placeholder citations

---

## AI-Generated Content Policy

- Business plans are AI-generated based on user inputs only
- AI must not reproduce copyrighted text verbatim in outputs
- AI prompts must not include instructions to reproduce third-party copyrighted material
- AI outputs are the intellectual property of the project owner (user)
- Venture Copilot claims no rights over user-generated business plan content

---

## Mock Research Data

The MVP `MockProvider` and `MockResearchService` use:
- Clearly labelled placeholder data (e.g., `"source": "MockData"`)
- Non-realistic example figures that cannot be mistaken for real market data
- No real company names used in fabricated competitive analysis

---

## Future Research API Integration

When integrating real research APIs, the following must be verified before use:
1. Review API Terms of Service — confirm commercial use is permitted
2. Confirm data can be stored (some APIs prohibit caching)
3. Attribute correctly per API provider's attribution requirements
4. Implement rate limiting to stay within API usage limits
5. Never store raw API responses if the ToS prohibits it — store summaries only

---

## Responsibility

- Venture Copilot is a tool — not a publisher
- Users are responsible for verifying research data before using in real business plans
- Venture Copilot provides citations so users can verify sources independently
- Venture Copilot does not warrant the accuracy of AI-generated content
