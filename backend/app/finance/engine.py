from app.schemas.finance import FinanceForecastCreate


def run_forecast(data: FinanceForecastCreate) -> dict:
    monthly_rows: list[dict] = []
    income_statement: list[dict] = []
    cash_flow_statement: list[dict] = []
    balance_sheet: list[dict] = []

    cash = data.starting_cash + data.financing_amount
    revenue = data.starting_revenue
    breakeven_month = None
    breakeven_revenue = None
    min_cash = cash
    net_cash_flows = [-data.initial_investment]

    for m in range(1, data.months + 1):
        if m > 1:
            revenue = revenue * (1 + data.monthly_growth_rate)

        opening_cash = cash
        variable_costs = round(revenue * data.variable_cost_rate, 2)
        gross_profit = round(revenue * data.gross_margin, 2)
        fixed_costs = round(data.fixed_monthly_costs, 2)
        total_costs = round(variable_costs + fixed_costs, 2)
        operating_profit = round(revenue - total_costs, 2)
        tax = round(max(operating_profit, 0) * data.tax_rate, 2)
        net_profit = round(operating_profit - tax, 2)
        financing_cash_flow = data.financing_amount if m == 1 else 0.0
        operating_cash_flow = net_profit
        cash = round(opening_cash + operating_cash_flow + financing_cash_flow, 2)
        assets = cash
        liabilities = max(0.0, round(abs(cash) if cash < 0 else 0.0, 2))
        equity = round(assets - liabilities, 2)
        net_cash_flows.append(operating_cash_flow)

        if breakeven_month is None and net_profit >= 0:
            breakeven_month = m
            breakeven_revenue = round(revenue, 2)

        if cash < min_cash:
            min_cash = cash

        row = {
            "month": m,
            "revenue": round(revenue, 2),
            "variable_costs": variable_costs,
            "fixed_costs": fixed_costs,
            "total_costs": total_costs,
            "gross_profit": gross_profit,
            "operating_profit": operating_profit,
            "net_profit": net_profit,
            "cash_balance": cash,
        }
        monthly_rows.append(row)
        income_statement.append({
            "month": m,
            "revenue": row["revenue"],
            "variable_costs": variable_costs,
            "fixed_costs": fixed_costs,
            "gross_profit": gross_profit,
            "operating_profit": operating_profit,
            "net_profit": net_profit,
        })
        cash_flow_statement.append({
            "month": m,
            "opening_cash": round(opening_cash, 2),
            "operating_cash_flow": operating_cash_flow,
            "financing_cash_flow": financing_cash_flow,
            "ending_cash": cash,
        })
        balance_sheet.append({
            "month": m,
            "cash": cash,
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
        })

    total_revenue = round(sum(r["revenue"] for r in monthly_rows), 2)
    total_net_profit = round(sum(r["net_profit"] for r in monthly_rows), 2)
    ending_cash = monthly_rows[-1]["cash_balance"]
    funding_needed = round(abs(min_cash) if min_cash < 0 else 0.0, 2)
    recommended_buffer = round(max(data.fixed_monthly_costs * 3, total_revenue / max(data.months, 1) * 0.2), 2)
    suggested_financing_amount = round(funding_needed + recommended_buffer, 2)
    npv = round(_npv(data.discount_rate, net_cash_flows), 2)
    irr = _irr(net_cash_flows)
    dcf_value = round(sum(cf / ((1 + data.discount_rate) ** i) for i, cf in enumerate(net_cash_flows[1:], start=1)), 2)
    roi = round((total_net_profit - data.initial_investment) / data.initial_investment, 4) if data.initial_investment else 0.0

    summary = {
        "total_revenue": total_revenue,
        "total_net_profit": total_net_profit,
        "ending_cash": ending_cash,
        "breakeven_month": breakeven_month,
        "funding_needed": funding_needed,
    }
    forecast_data = {
        "summary": summary,
        "monthly_rows": monthly_rows,
        "income_statement": income_statement,
        "cash_flow_statement": cash_flow_statement,
        "balance_sheet": balance_sheet,
        "financing_needs": {
            "funding_needed": funding_needed,
            "lowest_cash_balance": round(min_cash, 2),
            "recommended_buffer": recommended_buffer,
            "suggested_financing_amount": suggested_financing_amount,
        },
        "break_even": {
            "breakeven_month": breakeven_month,
            "breakeven_revenue": breakeven_revenue,
        },
        "valuation": {
            "npv": npv,
            "irr": irr,
            "roi": roi,
            "dcf_value": dcf_value,
        },
        "sensitivity_analysis": _sensitivity(data),
    }
    forecast_data["markdown_tables"] = {
        "income_statement": _markdown_table(income_statement),
        "cash_flow_statement": _markdown_table(cash_flow_statement),
        "balance_sheet": _markdown_table(balance_sheet),
        "sensitivity_analysis": _markdown_table(forecast_data["sensitivity_analysis"]),
    }
    forecast_data["csv_exports"] = {
        "income_statement_csv": _csv(income_statement),
        "cash_flow_csv": _csv(cash_flow_statement),
        "balance_sheet_csv": _csv(balance_sheet),
    }
    forecast_data["charts"] = {
        "revenue_trend": [{"month": r["month"], "revenue": r["revenue"]} for r in monthly_rows],
        "profit_trend": [{"month": r["month"], "net_profit": r["net_profit"]} for r in monthly_rows],
        "cash_trend": [{"month": r["month"], "cash_balance": r["cash_balance"]} for r in monthly_rows],
        "cost_structure": [
            {"month": r["month"], "fixed_costs": r["fixed_costs"], "variable_costs": r["variable_costs"]}
            for r in monthly_rows
        ],
    }
    return forecast_data


def _npv(discount_rate: float, cash_flows: list[float]) -> float:
    return sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))


def _irr(cash_flows: list[float]) -> float | None:
    low, high = -0.95, 1.0
    for _ in range(80):
        mid = (low + high) / 2
        value = _npv(mid, cash_flows)
        if abs(value) < 0.01:
            return round(mid, 4)
        if value > 0:
            low = mid
        else:
            high = mid
    result = (low + high) / 2
    return round(result, 4) if -0.95 < result < 1.0 else None


def _sensitivity(data: FinanceForecastCreate) -> list[dict]:
    scenarios = [
        ("monthly_growth_rate -20%", data.monthly_growth_rate * 0.8),
        ("base", data.monthly_growth_rate),
        ("monthly_growth_rate +20%", data.monthly_growth_rate * 1.2),
    ]
    rows = []
    for label, growth in scenarios:
        revenue = data.starting_revenue
        cash = data.starting_cash + data.financing_amount
        min_cash = cash
        total_revenue = 0.0
        for m in range(1, data.months + 1):
            if m > 1:
                revenue *= 1 + growth
            variable_costs = revenue * data.variable_cost_rate
            operating_profit = revenue - variable_costs - data.fixed_monthly_costs
            tax = max(operating_profit, 0) * data.tax_rate
            cash += operating_profit - tax
            min_cash = min(min_cash, cash)
            total_revenue += revenue
        rows.append({
            "scenario": label,
            "monthly_growth_rate": round(growth, 4),
            "total_revenue": round(total_revenue, 2),
            "ending_cash": round(cash, 2),
            "funding_needed": round(abs(min_cash) if min_cash < 0 else 0.0, 2),
        })
    return rows


def _markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |" for row in rows)
    return "\n".join(lines)


def _csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    lines = [",".join(headers)]
    lines.extend(",".join(str(row.get(h, "")) for h in headers) for row in rows)
    return "\n".join(lines)
