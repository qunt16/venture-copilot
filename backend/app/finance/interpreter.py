def interpret_forecast(forecast_data: dict, assumptions: dict | None = None) -> dict:
    assumptions = assumptions or {}
    summary = forecast_data.get("summary") or {}
    financing = forecast_data.get("financing_needs") or {}
    break_even = forecast_data.get("break_even") or {}
    valuation = forecast_data.get("valuation") or {}
    sensitivity = forecast_data.get("sensitivity_analysis") or []
    rows = forecast_data.get("monthly_rows") or []

    strengths: list[str] = []
    weaknesses: list[str] = []
    risks: list[str] = []
    recommendations: list[str] = []

    breakeven_month = break_even.get("breakeven_month") or summary.get("breakeven_month")
    npv = valuation.get("npv")
    irr = valuation.get("irr")
    dcf = valuation.get("dcf_value")
    roi = valuation.get("roi")
    ending_cash = summary.get("ending_cash")
    funding_needed = financing.get("funding_needed", summary.get("funding_needed", 0))
    lowest_cash = financing.get("lowest_cash_balance")

    if breakeven_month:
        text = f"项目预计第 {breakeven_month} 个月达到盈亏平衡。"
        if breakeven_month <= 12:
            strengths.append(text + "回本周期较短，有利于竞赛答辩中的可行性表达。")
        elif breakeven_month <= 24:
            weaknesses.append(text + "回本周期偏长，需要说明市场启动期和获客节奏。")
        else:
            risks.append(text + "回本周期较长，现金流压力需要重点解释。")
    else:
        risks.append("当前预测周期内未达到盈亏平衡，商业模式和成本结构需要重新校验。")

    if npv is not None:
        if npv < 0:
            risks.append(f"当前假设下 NPV 为 {money(npv)}，说明折现后项目价值为负，长期盈利确定性不足。")
            recommendations.append("建议降低固定成本、提高毛利率或重新校准增长率假设。")
        else:
            strengths.append(f"当前假设下 NPV 为 {money(npv)}，折现后仍保持正向价值。")
    if irr is not None:
        if irr < 0.08:
            weaknesses.append(f"IRR 为 {percent(irr)}，投资回报吸引力偏弱。")
        else:
            strengths.append(f"IRR 为 {percent(irr)}，在当前假设下具备一定投资回报潜力。")
    if dcf is not None:
        strengths.append(f"DCF 估算值为 {money(dcf)}，可作为项目估值讨论的保守参考。")
    if roi is not None:
        if roi < 0:
            risks.append(f"ROI 为 {percent(roi)}，投入产出为负。")
        else:
            strengths.append(f"ROI 为 {percent(roi)}，显示累计净利润相对初始投入具备回收能力。")

    if funding_needed and funding_needed > 0:
        risks.append(f"最低现金余额为 {money(lowest_cash)}，测算资金缺口为 {money(funding_needed)}，若不融资可能中断运营。")
        recommendations.append(f"建议至少准备 {money(financing.get('suggested_financing_amount', funding_needed))} 的融资或备用资金。")
    else:
        strengths.append(f"预测期末现金为 {money(ending_cash)}，当前假设下未出现显著资金缺口。")

    downside = next((row for row in sensitivity if "20%" in str(row.get("scenario")) and "-" in str(row.get("scenario"))), None)
    if downside and downside.get("funding_needed", 0) > funding_needed:
        risks.append("敏感性分析显示增长率下行情景会放大资金需求，项目对增长假设较敏感。")

    if assumptions.get("ai_suggested"):
        risks.append("当前财务假设包含 AI 建议且未作为用户确认输入，不能直接作为最终预测依据。")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "funding_pressure": "；".join(item for item in risks if "资金" in item or "现金" in item) or "当前未发现显著资金压力。",
        "risks": risks,
        "recommendations": recommendations,
        "key_metrics": {
            "breakeven_month": breakeven_month,
            "npv": npv,
            "irr": irr,
            "dcf": dcf,
            "roi": roi,
            "ending_cash": ending_cash,
            "funding_needed": funding_needed,
        },
        "summary": _summary(strengths, weaknesses, risks),
    }


def money(value) -> str:
    if value is None:
        return "暂无数据"
    return f"{float(value):,.2f} 元"


def percent(value) -> str:
    if value is None:
        return "暂无数据"
    return f"{float(value) * 100:.2f}%"


def _summary(strengths: list[str], weaknesses: list[str], risks: list[str]) -> str:
    if risks:
        return risks[0]
    if weaknesses:
        return weaknesses[0]
    if strengths:
        return strengths[0]
    return "财务解释需要先完成预测。"
