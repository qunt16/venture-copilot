def build_financial_narrative(forecast) -> dict:
    data = forecast.summary or {}
    forecast_data = data if "monthly_rows" in data else {"summary": data, "monthly_rows": forecast.monthly_rows or []}
    summary = forecast_data.get("summary") or {}
    rows = forecast_data.get("monthly_rows") or forecast.monthly_rows or []
    income = forecast_data.get("income_statement") or []
    cash_flow = forecast_data.get("cash_flow_statement") or []
    balance = forecast_data.get("balance_sheet") or []
    financing = forecast_data.get("financing_needs") or {}
    break_even = forecast_data.get("break_even") or {}
    valuation = forecast_data.get("valuation") or {}
    sensitivity = forecast_data.get("sensitivity_analysis") or []
    inputs = forecast.inputs or {}

    if not rows:
        return {
            "content": "缺少财务预测明细，无法生成财务分析。请先生成 Finance Pro 财务预测。",
            "tables": {},
            "warnings": ["finance_missing"],
        }

    first_revenue = rows[0].get("revenue", 0)
    last_revenue = rows[-1].get("revenue", 0)
    total_revenue = summary.get("total_revenue", 0)
    total_net_profit = summary.get("total_net_profit", 0)
    ending_cash = summary.get("ending_cash", 0)
    lowest_cash = financing.get("lowest_cash_balance")
    breakeven_month = break_even.get("breakeven_month") or summary.get("breakeven_month")
    breakeven_revenue = break_even.get("breakeven_revenue")
    funding_needed = financing.get("funding_needed", summary.get("funding_needed", 0))
    suggested_financing = financing.get("suggested_financing_amount", funding_needed)
    buffer = financing.get("recommended_buffer", 0)

    content = "\n\n".join(
        [
            "8.1 收入预测\n"
            f"本项目以月度收入 {money(first_revenue)} 为起点，按照月增长率 {percent(inputs.get('monthly_growth_rate', 0))} 进行 36 个月测算。"
            f"三年累计收入预计为 {money(total_revenue)}，第 36 个月收入预计达到 {money(last_revenue)}。收入增长假设来自现有 Finance Pro 输入，未额外虚构市场数据。",
            "8.2 成本结构\n"
            f"成本由固定成本和变动成本构成。固定月成本为 {money(inputs.get('fixed_monthly_costs', 0))}，变动成本率为 {percent(inputs.get('variable_cost_rate', 0))}。"
            "随着业务规模扩大，变动成本随收入同步变化，固定成本保持稳定。",
            "8.3 利润表\n"
            f"利润表显示三年累计净利润约为 {money(total_net_profit)}。重点关注收入、毛利润、营业利润和净利润之间的变化关系，详见导出文件中的利润表。",
            "8.4 现金流量表\n"
            f"现金流量表显示期末现金余额约为 {money(ending_cash)}，最低现金余额为 {money(lowest_cash)}。若最低现金余额为负，说明项目需要外部资金覆盖阶段性现金缺口。",
            "8.5 资产负债表\n"
            "资产负债表采用简化口径，重点展示现金、资产、负债和所有者权益，用于判断项目在预测周期内的资金安全边界。",
            "8.6 盈亏平衡分析\n"
            + (
                f"项目预计在第 {breakeven_month} 个月达到盈亏平衡，对应收入约为 {money(breakeven_revenue)}。"
                if breakeven_month
                else "在当前预测周期内尚未达到盈亏平衡，需要进一步优化收入增长或成本结构。"
            ),
            "8.7 融资需求\n"
            f"测算资金缺口为 {money(funding_needed)}，建议融资金额为 {money(suggested_financing)}，其中包含建议安全垫 {money(buffer)}。资金用途应优先覆盖产品研发、校园试点、市场推广和运营周转。",
            "8.8 估值分析\n"
            f"按现有折现率测算，NPV 为 {money(valuation.get('npv'))}，IRR 为 {percent(valuation.get('irr')) if valuation.get('irr') is not None else '暂无有效结果'}，"
            f"DCF 价值为 {money(valuation.get('dcf_value'))}，ROI 为 {percent(valuation.get('roi'))}。这些指标用于辅助判断项目投入产出质量，不应替代真实融资定价。",
            "8.9 敏感性分析\n"
            "敏感性分析围绕月增长率下调 20%、基准情景和上调 20% 三种情况，比较总收入、期末现金和资金需求变化。若下行情景资金缺口明显扩大，应提前设置融资缓冲和成本控制方案。",
        ]
    )
    return {
        "content": content,
        "tables": {
            "income_statement": income,
            "cash_flow_statement": cash_flow,
            "balance_sheet": balance,
            "sensitivity_analysis": sensitivity,
        },
        "summary": summary,
        "valuation": valuation,
        "warnings": [],
    }


def money(value) -> str:
    if value is None:
        return "暂无数据"
    try:
        return f"{float(value):,.2f} 元"
    except (TypeError, ValueError):
        return str(value)


def percent(value) -> str:
    if value is None:
        return "暂无数据"
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(value)
