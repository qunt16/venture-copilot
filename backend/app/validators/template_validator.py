from app.templates.business_plan_templates import TEMPLATE_PRESETS


def validate_template(context: dict) -> dict:
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []
    template_type = context.get("template_type") or "generic_startup"
    selected = context.get("selected_sections") or []

    if not selected:
        critical.append("业务计划缺少章节结构")
        suggestions.append("重新生成业务计划并选择必要章节。")
    if template_type in TEMPLATE_PRESETS and selected:
        preset = TEMPLATE_PRESETS[template_type]
        expected = [key for key in preset if key in selected]
        if selected[: len(expected)] != expected:
            warnings.append("业务计划章节顺序与模板预设不完全一致。")
            suggestions.append("按赛事模板顺序重新生成业务计划。")
        missing = [key for key in preset[:5] if key not in selected]
        if missing:
            warnings.append("业务计划缺少部分核心模板章节。")

    score = 100 - len(warnings) * 10 - len(critical) * 25
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
