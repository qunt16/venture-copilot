import re


def validate_market(context: dict) -> dict:
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []
    summary = context.get("forecast_summary") or {}
    total_revenue = float(summary.get("total_revenue") or 0)
    market_size_text = context.get("market_size") or ""
    tiny_market = any(term in market_size_text for term in ["小众", "有限", "试点", "tiny", "small"])
    numbers = [float(item) for item in re.findall(r"\d+(?:\.\d+)?", market_size_text)]
    explicit_market = max(numbers) if numbers else None

    if tiny_market and total_revenue > 1_000_000:
        critical.append("预测收入超过可触达市场规模")
        suggestions.append("降低增长率假设，或补充更清晰的可触达市场测算。")
    elif explicit_market and explicit_market < 100 and total_revenue > 1_000_000:
        warnings.append("市场规模描述偏小，但收入预测较高。")

    score = 100 - len(warnings) * 12 - len(critical) * 25
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
