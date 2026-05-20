def validate_logic(context: dict) -> dict:
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []
    idea = context.get("idea_summary") or ""
    team_size = int(context.get("team_size") or 0)
    ambitious_terms = ["foundation model", "基础大模型", "通用大模型", "AGI"]

    if team_size <= 2 and any(term in idea for term in ambitious_terms):
        critical.append("团队执行能力与项目技术难度不匹配")
        suggestions.append("收窄技术范围，优先验证可交付 MVP。")
    if not context.get("frameworks"):
        warnings.append("缺少战略框架分析，逻辑支撑不完整。")
        suggestions.append("先运行 SWOT、PEST、波特五力和商业模式画布。")

    score = 100 - len(warnings) * 10 - len(critical) * 25
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
