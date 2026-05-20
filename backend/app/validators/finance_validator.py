def validate_finance(context: dict) -> dict:
    summary = context.get("forecast_summary") or {}
    financing = context.get("financing_needs") or {}
    warnings: list[str] = []
    critical: list[str] = []
    suggestions: list[str] = []

    funding_needed = float(summary.get("funding_needed") or 0)
    lowest_cash = float(financing.get("lowest_cash_balance") or 0)
    requested_financing = float((context.get("forecast_inputs") or {}).get("financing_amount") or 0)

    if funding_needed > 0 and requested_financing <= 0:
        critical.append("融资金额低于最低现金需求")
        suggestions.append("提高初始融资或降低固定成本，避免现金流断裂。")
    if lowest_cash < 0:
        warnings.append("预测期内出现负现金余额。")
    if float(summary.get("breakeven_month") or 0) > 24:
        warnings.append("盈亏平衡时间较晚，需要解释获客和成本控制路径。")

    score = 100 - len(warnings) * 10 - len(critical) * 20
    return {"score": max(score, 0), "warnings": warnings, "critical_conflicts": critical, "suggestions": suggestions}
