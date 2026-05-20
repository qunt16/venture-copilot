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
    enriched = add_deterministic_insights(
        deepcopy(report),
        project=project,
        forecast_summary=forecast_summary,
        business_model=business_model,
    )
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


def add_deterministic_insights(
    report: dict[str, Any],
    *,
    project: dict[str, Any],
    forecast_summary: dict[str, Any],
    business_model: str | None,
) -> dict[str, Any]:
    issue_count = report.get("issue_count") or {"errors": 0, "warnings": 0, "suggestions": 0}
    score = calculate_overall_score(issue_count)
    risk_level = classify_risk_level(score, issue_count)
    issues = report.get("issues") or []
    top_risks = [
        issue.get("title") or issue.get("description")
        for issue in issues[:3]
        if issue.get("title") or issue.get("description")
    ]
    next_actions = [
        issue.get("fix_suggestion")
        for issue in issues[:3]
        if issue.get("fix_suggestion")
    ]
    focus = competition_focus(project.get("competition_type"))
    runway = forecast_summary.get("runway_months")
    break_even = forecast_summary.get("break_even_month")
    why = build_why_this_matters(
        risk_level=risk_level,
        focus=focus,
        issue_count=issue_count,
        runway=runway,
        break_even=break_even,
    )
    judge = build_judge_perspective(focus, business_model)

    report["overall_score"] = score
    report["risk_level"] = risk_level
    report["why_this_matters"] = why
    report["top_risks"] = top_risks
    report["next_actions"] = next_actions
    report["summary_narrative"] = report.get("summary_narrative") or why
    report["judge_perspective"] = report.get("judge_perspective") or judge
    return report


def calculate_overall_score(issue_count: dict[str, Any]) -> int:
    errors = int(issue_count.get("errors") or 0)
    warnings = int(issue_count.get("warnings") or 0)
    suggestions = int(issue_count.get("suggestions") or 0)
    return max(0, min(100, 100 - errors * 25 - warnings * 10 - suggestions * 3))


def classify_risk_level(score: int, issue_count: dict[str, Any]) -> str:
    if int(issue_count.get("errors") or 0) > 0 or score < 60:
        return "高风险"
    if int(issue_count.get("warnings") or 0) > 0 or score < 85:
        return "需关注"
    return "健康"


def competition_focus(competition_type: str | None) -> str:
    focus_map = {
        "challenge_cup": "创新性、社会价值和假设可解释性",
        "internet_plus": "商业化路径、增长证据和落地能力",
        "business_competition": "盈利能力、现金安全和执行能力",
    }
    return focus_map.get(competition_type or "", "商业可行性、财务可信度和执行能力")


def build_why_this_matters(
    *,
    risk_level: str,
    focus: str,
    issue_count: dict[str, Any],
    runway: Any,
    break_even: Any,
) -> str:
    issue_total = sum(int(issue_count.get(key) or 0) for key in ("errors", "warnings", "suggestions"))
    context = f"当前模型风险等级为{risk_level}，需要围绕{focus}进一步解释关键假设。"
    if issue_total == 0:
        return f"{context} 暂未发现明显规则冲突，但仍建议准备好收入增长、成本结构和现金续航的答辩依据。"
    details = []
    if runway is not None:
        details.append(f"现金续航约为{runway}个月")
    if break_even is not None:
        details.append(f"预计第{break_even}个月达到盈亏平衡")
    if details:
        return f"{context} {'，'.join(details)}，这些指标会直接影响评委对项目抗风险能力的判断。"
    return f"{context} 已发现{issue_total}个需要处理的问题，建议先修正高风险项，再完善支撑材料。"


def build_judge_perspective(focus: str, business_model: str | None) -> str:
    model_label = "SaaS/订阅模式" if business_model == "saas" else "服务/咨询模式" if business_model == "service" else "当前商业模式"
    return f"从评委视角看，{model_label}需要证明{focus}，并能清楚说明每个关键财务假设的来源。"


def build_ai_payload(
    *,
    report: dict[str, Any],
    project: dict[str, Any],
    forecast_summary: dict[str, Any],
    business_model: str | None,
) -> dict[str, Any]:
    issues = report.get("issues") or []
    return {
        "task": "Rewrite deterministic validation output into clearer Chinese language for a university startup competition team.",
        "strict_rules": [
            "Do not add new rule IDs.",
            "Do not add new issues.",
            "Do not remove existing issues.",
            "Do not provide legal or financial advice.",
            "Do not claim real market viability.",
            "Do not invent missing numbers.",
            "Do not change overall_score or risk_level.",
            "Improve fix_suggestion only for the provided issues.",
            "Write narrative fields in natural Chinese.",
        ],
        "business_model": business_model,
        "competition_focus": competition_focus(project.get("competition_type")),
        "project": {
            "title": project.get("title"),
            "idea_summary": project.get("idea_summary"),
            "industry": project.get("industry"),
            "competition_type": project.get("competition_type"),
        },
        "forecast_summary": forecast_summary,
        "overall_score": report.get("overall_score"),
        "risk_level": report.get("risk_level"),
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
            "summary_narrative": "3-5 Chinese sentences based only on supplied numbers and issues",
            "why_this_matters": "2-4 Chinese sentences explaining why the current issues matter in competition judging",
            "top_risks": ["Chinese risk sentence copied or summarized from existing issues only"],
            "judge_perspective": "1-2 Chinese sentences adapted to competition_type",
            "next_actions": ["Chinese action sentence based only on existing fix_suggestion values"],
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
    if isinstance(result.get("why_this_matters"), str):
        report["why_this_matters"] = result["why_this_matters"]
    if isinstance(result.get("top_risks"), list):
        report["top_risks"] = [str(item) for item in result["top_risks"][:5] if item]
    if isinstance(result.get("judge_perspective"), str):
        report["judge_perspective"] = result["judge_perspective"]
    if isinstance(result.get("next_actions"), list):
        report["next_actions"] = [str(item) for item in result["next_actions"][:5] if item]
    return report


def _system_prompt() -> str:
    return (
        "You are a Chinese finance writing assistant for university startup competitions. "
        "You only rewrite the provided deterministic validation report. "
        "Return strict JSON only. Never invent new rules, new issues, new facts, or missing numbers."
    )
