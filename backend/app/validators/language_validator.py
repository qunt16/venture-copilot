from app.services.language_service import detect_language_mixing


def validate_language(context: dict) -> dict:
    warnings: list[str] = []
    suggestions: list[str] = []
    language = context.get("language") or "zh-CN"
    text = context.get("combined_text") or ""
    mixing = detect_language_mixing(text, language)
    if mixing:
        warnings.extend(mixing)
        suggestions.append("重新生成或清洗中文正文，仅保留 URL、公司名、引用标题和公式缩写。")
    score = 100 - len(mixing) * 20
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": [], "suggestions": suggestions}
