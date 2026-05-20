def validate_research(context: dict) -> dict:
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []
    citations = context.get("citations") or []
    bp_text = context.get("business_plan_text") or ""
    strong_claims = ["必然", "一定", "垄断", "颠覆", "迅速占领", "guaranteed", "dominant"]

    if len(citations) < 2:
        warnings.append("研究引用数量偏少，证据支撑较弱。")
        suggestions.append("补充政府、机构或行业报告来源。")
    if any(claim in bp_text for claim in strong_claims) and len(citations) < 4:
        critical.append("弱证据支撑了过强结论")
        suggestions.append("将强结论改为可验证假设，并增加引用依据。")

    score = 100 - len(warnings) * 12 - len(critical) * 25
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
