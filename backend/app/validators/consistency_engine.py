def score_project(context: dict) -> dict:
    deductions = _deductions(context)
    dimensions = _dimensions(context, deductions)
    warnings = [item["reason"] for item in deductions if item["points"] <= -8]
    critical = [item["reason"] for item in deductions if item["points"] <= -15]
    suggestions = _suggestions(deductions)
    overall = max(0, min(100, 100 + sum(item["points"] for item in deductions)))
    return {
        "overall_score": overall,
        "dimensions": dimensions,
        "deductions": deductions,
        "warnings": warnings,
        "critical_conflicts": critical,
        "suggestions": suggestions,
    }


def _deductions(context: dict) -> list[dict]:
    sections = context.get("business_plan_sections") or []
    section_by_key = {section.get("key"): section for section in sections}
    citations = context.get("citations") or []
    frameworks = context.get("frameworks") or {}
    forecast_summary = context.get("forecast_summary") or {}
    financing = context.get("financing_needs") or {}
    assumptions = context.get("financial_assumptions") or {}
    deductions: list[dict] = []

    if not sections:
        deductions.append(_d("Business plan missing", -20, "completeness"))
    required = [
        ("project_overview", "Missing project overview", -8),
        ("market_analysis", "Missing market analysis", -10),
        ("tam_sam_som", "Missing TAM/SAM/SOM", -10),
        ("competitor_analysis", "Missing competitor analysis", -8),
        ("financial_forecast", "Missing financial analysis", -15),
        ("funding_plan", "Missing funding plan", -8),
        ("risk_analysis", "Missing risk analysis", -8),
        ("references", "Missing references", -8),
    ]
    for key, reason, points in required:
        if key not in section_by_key:
            deductions.append(_d(reason, points, "completeness"))
    for section in sections:
        if not str(section.get("content") or "").strip():
            deductions.append(_d(f"Empty chapter: {section.get('heading') or section.get('key')}", -8, "completeness"))
    if not assumptions:
        deductions.append(_d("Finance assumptions missing", -20, "finance"))
    elif not context.get("financial_assumptions_confirmed"):
        deductions.append(_d("AI-generated or unconfirmed assumptions", -20, "finance"))
    if context.get("financial_assumption_warnings"):
        deductions.append(_d("Finance assumptions contain warnings", -6, "finance"))
    if not forecast_summary:
        deductions.append(_d("Finance forecast missing", -15, "finance"))
    if financing.get("funding_needed", 0) > 0 and "资金" not in str(section_by_key.get("funding_plan", {}).get("content", "")):
        deductions.append(_d("Negative cash or funding pressure lacks explanation", -10, "finance"))
    if not citations:
        deductions.append(_d("No citations", -15, "evidence"))
    if "competitor_matrix" not in frameworks and "business_model_canvas" not in frameworks:
        deductions.append(_d("Missing competitor matrix", -8, "market"))
    if context.get("language") == "zh-CN" and _has_raw_english(context.get("combined_text") or ""):
        deductions.append(_d("Language mixing or raw Exa snippet detected", -12, "language"))
    if not context.get("exports"):
        deductions.append(_d("No export generated", -5, "export"))
    return deductions


def _dimensions(context: dict, deductions: list[dict]) -> dict:
    weights = {
        "completeness": 100,
        "data_quality": 100,
        "finance": 100,
        "market": 100,
        "evidence": 100,
        "language": 100,
        "logic": 100,
        "export": 100,
    }
    for item in deductions:
        category = item.get("category", "logic")
        if category in weights:
            weights[category] = max(0, weights[category] + item["points"])
    return weights


def _suggestions(deductions: list[dict]) -> list[str]:
    mapping = {
        "Finance assumptions missing": "先填写并确认财务假设，再生成预测。",
        "No citations": "运行 Exa 研究并把引用写入参考资料。",
        "Missing TAM/SAM/SOM": "补充 TAM/SAM/SOM 市场容量测算。",
        "Missing competitor matrix": "运行框架分析并补充竞品矩阵。",
        "No export generated": "完成最终确认后导出 DOCX/PDF。",
    }
    return [mapping.get(item["reason"], f"修复：{item['reason']}") for item in deductions[:8]]


def _d(reason: str, points: int, category: str) -> dict:
    return {"reason": reason, "points": points, "category": category}


def _has_raw_english(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in ["summary:", "this page markets", "key features:"])
