import json
from copy import deepcopy
from typing import Any

from app.ai.base import AIConfig, AIProviderError
from app.ai.provider_factory import get_provider


def add_ai_narrative(
    report: dict[str, Any],
    *,
    project: dict[str, Any],
    forecast_summary: dict[str, Any],
    business_model: str | None,
) -> dict[str, Any]:
    enriched = deepcopy(report)
    try:
        provider = get_provider(AIConfig(provider="openrouter", fallback_to_mock=False))
        payload = build_ai_payload(
            report=enriched,
            project=project,
            forecast_summary=forecast_summary,
            business_model=business_model,
        )
        result = provider.chat_json(
            _system_prompt(),
            json.dumps(payload, ensure_ascii=False),
            "summary_narrative",
        )
    except (AIProviderError, AttributeError, TypeError, ValueError):
        return enriched

    return apply_ai_result(enriched, result)


def build_ai_payload(
    *,
    report: dict[str, Any],
    project: dict[str, Any],
    forecast_summary: dict[str, Any],
    business_model: str | None,
) -> dict[str, Any]:
    issues = report.get("issues") or []
    return {
        "task": "Rewrite deterministic validation output into clearer language for a university startup competition team.",
        "strict_rules": [
            "Do not add new rule IDs.",
            "Do not add new issues.",
            "Do not remove existing issues.",
            "Do not provide legal or financial advice.",
            "Do not claim real market viability.",
            "Do not invent missing numbers.",
            "Improve fix_suggestion only for the provided issues.",
        ],
        "business_model": business_model,
        "project": {
            "title": project.get("title"),
            "idea_summary": project.get("idea_summary"),
            "industry": project.get("industry"),
            "competition_type": project.get("competition_type"),
        },
        "forecast_summary": forecast_summary,
        "issue_count": report.get("issue_count") or {"errors": 0, "warnings": 0, "suggestions": 0},
        "issues": [
            {
                "rule_id": issue.get("rule_id"),
                "severity": issue.get("severity"),
                "title": issue.get("title"),
                "description": issue.get("description"),
                "fix_suggestion": issue.get("fix_suggestion"),
                "affected_fields": issue.get("affected_fields") or [],
            }
            for issue in issues
        ],
        "output_schema": {
            "summary_narrative": "3-5 sentences",
            "judge_perspective": "1-2 sentences",
            "issues": [{"rule_id": "existing rule_id only", "fix_suggestion": "rewritten suggestion"}],
        },
    }


def apply_ai_result(report: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    allowed_rule_ids = {issue.get("rule_id") for issue in report.get("issues", [])}
    rewritten = {
        issue.get("rule_id"): issue.get("fix_suggestion")
        for issue in result.get("issues", [])
        if issue.get("rule_id") in allowed_rule_ids and issue.get("fix_suggestion")
    }
    for issue in report.get("issues", []):
        rule_id = issue.get("rule_id")
        if rule_id in rewritten:
            issue["fix_suggestion"] = rewritten[rule_id]
    if isinstance(result.get("summary_narrative"), str):
        report["summary_narrative"] = result["summary_narrative"]
    if isinstance(result.get("judge_perspective"), str):
        report["judge_perspective"] = result["judge_perspective"]
    return report


def _system_prompt() -> str:
    return (
        "You are a finance writing assistant for university startup competitions. "
        "You only rewrite the provided deterministic validation report. "
        "Return strict JSON only. Never invent new rules, new issues, new facts, or missing numbers."
    )
