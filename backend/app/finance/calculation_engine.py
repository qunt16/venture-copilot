from __future__ import annotations

from typing import Any


VALID_HORIZONS = {12, 24, 36}


def calculate_forecast(
    project_setup: dict[str, Any] | None,
    revenue_config: dict[str, Any] | None,
    cost_config: dict[str, Any] | None,
    planning_horizon: int | None = None,
) -> dict[str, Any]:
    setup = project_setup or {}
    revenue = _unwrap_config(revenue_config)
    costs = _unwrap_config(cost_config)
    months = _planning_horizon(planning_horizon or setup.get("planning_horizon"))
    business_model = _business_model(setup.get("business_model") or revenue.get("business_model"))

    if business_model in {"saas", "subscription"}:
        revenue_rows = _saas_revenue(revenue, months)
    elif business_model in {"service", "consulting"}:
        revenue_rows = _service_revenue(revenue, months)
    else:
        revenue_rows = _saas_revenue(revenue, months)
        business_model = "saas"

    monthly_rows = _apply_costs_and_cashflow(revenue_rows, costs)
    summary = _summary(monthly_rows, business_model, revenue, costs, months)

    return {
        "business_model": business_model,
        "planning_horizon": months,
        "monthly_rows": monthly_rows,
        "summary": summary,
        "metadata": {
            "engine": "deterministic_finance_mvp",
            "supported_models": ["saas", "subscription", "service", "consulting"],
            "incomplete_sections": _incomplete_sections(revenue, costs),
        },
    }


def _saas_revenue(config: dict[str, Any], months: int) -> list[dict[str, Any]]:
    tiers = _pricing_tiers(config)
    growth_rate = _rate(config, "monthly_growth_rate", "growth_rate", default=0.0)
    churn_rate = _rate(config, "monthly_churn_rate", "churn_rate", default=0.0)
    previous_new = sum(tier["initial_customers"] for tier in tiers)
    previous_active = 0
    rows = []

    for month in range(1, months + 1):
        if month == 1:
            new_customers = previous_new
            churned_customers = 0
        else:
            new_customers = _count(previous_new * (1 + growth_rate))
            churned_customers = _count(previous_active * churn_rate)

        active_customers = max(0, _count(previous_active + new_customers - churned_customers))
        revenue = 0.0
        tier_rows = []
        for tier in tiers:
            tier_customers = _count(active_customers * tier["share"])
            tier_revenue = tier_customers * tier["monthly_price"]
            revenue += tier_revenue
            tier_rows.append({
                "name": tier["name"],
                "customers": tier_customers,
                "monthly_price": _money(tier["monthly_price"]),
                "revenue": _money(tier_revenue),
            })

        rows.append({
            "month": month,
            "new_customers": new_customers,
            "churned_customers": churned_customers,
            "active_customers": active_customers,
            "monthly_active_customers": active_customers,
            "monthly_revenue": _money(revenue),
            "mrr": _money(revenue),
            "arr": _money(revenue * 12),
            "churn_impact": {
                "churn_rate": churn_rate,
                "churned_customers": churned_customers,
                "lost_mrr": _money(_average_price(tiers) * churned_customers),
            },
            "arpu": _safe_div(revenue, active_customers),
            "tiers": tier_rows,
        })
        previous_new = new_customers
        previous_active = active_customers

    return rows


def _service_revenue(config: dict[str, Any], months: int) -> list[dict[str, Any]]:
    growth_rate = _rate(config, "monthly_client_growth_rate", "client_growth_rate", "growth_rate", default=0.0)
    churn_rate = _rate(config, "completion_rate", "monthly_churn_rate", "churn_rate", default=0.0)
    revenue_per_client = _number(config, "average_monthly_revenue_per_client", "revenue_per_client", "monthly_revenue_per_client", default=0.0)
    previous_new = _count(_number(config, "initial_clients", "active_clients", "month_1_clients", default=0.0))
    previous_active = 0
    rows = []

    for month in range(1, months + 1):
        if month == 1:
            new_clients = previous_new
            churned_clients = 0
        else:
            new_clients = _count(previous_new * (1 + growth_rate))
            churned_clients = _count(previous_active * churn_rate)
        active_clients = max(0, _count(previous_active + new_clients - churned_clients))
        monthly_revenue = active_clients * revenue_per_client
        rows.append({
            "month": month,
            "new_customers": new_clients,
            "new_clients": new_clients,
            "churned_customers": churned_clients,
            "completed_clients": churned_clients,
            "active_customers": active_clients,
            "active_clients": active_clients,
            "monthly_revenue": _money(monthly_revenue),
            "client_growth_rate": growth_rate,
            "arpu": _safe_div(monthly_revenue, active_clients),
        })
        previous_new = new_clients
        previous_active = active_clients

    return rows


def _apply_costs_and_cashflow(revenue_rows: list[dict[str, Any]], costs: dict[str, Any]) -> list[dict[str, Any]]:
    cash = _number(costs, "starting_cash", "starting_cash_balance", default=0.0)
    funding_events = costs.get("funding_events") or []
    rows = []

    for row in revenue_rows:
        month = row["month"]
        revenue = row["monthly_revenue"]
        active_customers = row.get("active_customers") or row.get("active_clients") or 0
        variable_costs = _variable_costs(costs, revenue, active_customers)
        fixed_costs = _fixed_costs(costs, month)
        marketing_costs = _marketing_costs(costs, revenue)
        payroll_costs = _payroll_costs(costs, month)
        one_time_costs = _one_time_costs(costs, month)
        funding_received = _funding_received(funding_events, month)
        total_costs = _money(variable_costs + fixed_costs + marketing_costs + payroll_costs + one_time_costs)
        gross_profit = _money(revenue - variable_costs)
        net_profit = _money(revenue - total_costs)
        net_cashflow = _money(net_profit + funding_received)
        cash = _money(cash + net_cashflow)
        gross_margin_pct = _safe_div(gross_profit, revenue)
        gross_burn = _money(total_costs)
        net_burn = _money(max(total_costs - revenue, 0.0))

        rows.append({
            **row,
            "revenue": _money(revenue),
            "fixed_costs": _money(fixed_costs),
            "variable_costs": _money(variable_costs),
            "marketing_costs": _money(marketing_costs),
            "payroll_costs": _money(payroll_costs),
            "one_time_costs": _money(one_time_costs),
            "funding_received": _money(funding_received),
            "total_costs": total_costs,
            "gross_profit": gross_profit,
            "gross_margin_pct": gross_margin_pct,
            "net_profit": net_profit,
            "net_cashflow": net_cashflow,
            "cumulative_cash_balance": cash,
            "cash_balance": cash,
            "gross_burn": gross_burn,
            "net_burn": net_burn,
        })

    return rows


def _summary(
    rows: list[dict[str, Any]],
    business_model: str,
    revenue_config: dict[str, Any],
    cost_config: dict[str, Any],
    months: int,
) -> dict[str, Any]:
    total_revenue = _money(sum(row["monthly_revenue"] for row in rows))
    total_costs = _money(sum(row["total_costs"] for row in rows))
    total_net_profit = _money(sum(row["net_profit"] for row in rows))
    zero_cash_month = next((row["month"] for row in rows if row["cumulative_cash_balance"] < 0), None)
    break_even_month = next((row["month"] for row in rows if row["net_profit"] >= 0), None)
    runway_months = zero_cash_month - 1 if zero_cash_month else months
    ending_cash = rows[-1]["cumulative_cash_balance"] if rows else _number(cost_config, "starting_cash", default=0.0)
    average_gross_margin = _safe_div(sum(row["gross_profit"] for row in rows), total_revenue)
    average_arpu = _safe_div(sum(row["monthly_revenue"] for row in rows), sum(row.get("active_customers", 0) for row in rows))
    first_12 = rows[:12]
    average_cac = _average_cac(first_12)
    churn_rate = _rate(revenue_config, "monthly_churn_rate", "churn_rate", default=0.0)
    ltv = _safe_div(average_arpu, churn_rate) if business_model in {"saas", "subscription"} else None
    ltv_cac_ratio = _safe_div(ltv, average_cac) if ltv is not None and average_cac is not None else None

    return {
        "total_revenue": total_revenue,
        "total_costs": total_costs,
        "total_net_profit": total_net_profit,
        "ending_cash": _money(ending_cash),
        "runway_months": runway_months,
        "zero_cash_month": zero_cash_month,
        "break_even_month": break_even_month,
        "gross_margin_pct": average_gross_margin,
        "ltv": _money(ltv) if ltv is not None else None,
        "cac": _money(average_cac) if average_cac is not None else None,
        "ltv_cac_ratio": ltv_cac_ratio,
        "arpu": _money(average_arpu) if average_arpu is not None else None,
        "mrr": _money(rows[-1].get("mrr", rows[-1]["monthly_revenue"])) if rows else 0.0,
        "arr": _money(rows[-1].get("arr", rows[-1]["monthly_revenue"] * 12)) if rows else 0.0,
        "gross_burn_month_1": rows[0]["gross_burn"] if rows else 0.0,
        "net_burn_month_1": rows[0]["net_burn"] if rows else 0.0,
        "annual": _annual_summary(rows),
    }


def _pricing_tiers(config: dict[str, Any]) -> list[dict[str, Any]]:
    raw_tiers = config.get("pricing_tiers") or config.get("tiers")
    if not raw_tiers:
        raw_tiers = [{
            "name": "default",
            "monthly_price": _number(config, "monthly_price", "unit_price", "price", default=0.0),
            "initial_customers": _number(config, "initial_customers", "month_1_customers", "starting_customers", default=0.0),
            "share_of_new_customers": 1.0,
        }]

    tiers = []
    for index, tier in enumerate(raw_tiers[:3]):
        share = _number(tier, "share_of_new_customers", "share", default=1.0 if len(raw_tiers) == 1 else 0.0)
        tiers.append({
            "name": str(tier.get("name") or tier.get("tier_name") or f"tier_{index + 1}"),
            "monthly_price": max(0.0, _number(tier, "monthly_price", "price", "unit_price", default=0.0)),
            "initial_customers": max(0, _count(_number(tier, "initial_customers", "month_1_customers", default=0.0))),
            "share": max(0.0, share),
        })

    total_share = sum(tier["share"] for tier in tiers)
    if total_share <= 0:
        equal_share = 1 / max(len(tiers), 1)
        for tier in tiers:
            tier["share"] = equal_share
    elif total_share != 1:
        for tier in tiers:
            tier["share"] = tier["share"] / total_share
    return tiers


def _variable_costs(costs: dict[str, Any], revenue: float, active_customers: int) -> float:
    total = revenue * _rate(costs, "variable_cost_rate", "variable_cost_pct", default=0.0)
    for item in costs.get("variable_costs") or []:
        basis = item.get("basis", "percent_of_revenue")
        rate = max(0.0, float(item.get("rate", item.get("amount", 0)) or 0))
        if basis in {"flat_per_customer", "per_customer"}:
            total += active_customers * rate
        else:
            total += revenue * rate
    return total


def _fixed_costs(costs: dict[str, Any], month: int) -> float:
    total = _number(costs, "fixed_monthly_costs", "fixed_costs", default=0.0)
    for item in costs.get("fixed_cost_items") or costs.get("fixed_cost_line_items") or []:
        start = int(item.get("start_month", 1) or 1)
        end = item.get("end_month")
        if month >= start and (end is None or month <= int(end)):
            total += max(0.0, float(item.get("monthly_amount", item.get("amount", 0)) or 0))
    return total


def _marketing_costs(costs: dict[str, Any], revenue: float) -> float:
    basis = costs.get("marketing_basis") or costs.get("marketing_spend_basis") or "flat"
    amount = _number(costs, "marketing_costs", "marketing_budget", "monthly_marketing_budget", default=0.0)
    if basis in {"percent_of_revenue", "pct_of_revenue"}:
        return revenue * amount
    return amount


def _payroll_costs(costs: dict[str, Any], month: int) -> float:
    total = _number(costs, "payroll_costs", "monthly_payroll", "employee_costs", default=0.0)
    for item in costs.get("headcount") or costs.get("payroll") or []:
        hire_month = int(item.get("hire_month", 1) or 1)
        if month >= hire_month:
            total += max(0.0, float(item.get("monthly_salary", item.get("salary", 0)) or 0)) * max(0, int(item.get("headcount", 1) or 0))
    return total


def _one_time_costs(costs: dict[str, Any], month: int) -> float:
    total = 0.0
    for item in costs.get("one_time_costs") or []:
        if int(item.get("month", item.get("incurred_month", 1)) or 1) == month:
            total += max(0.0, float(item.get("amount", 0) or 0))
    return total


def _funding_received(funding_events: list[dict[str, Any]], month: int) -> float:
    return sum(max(0.0, float(item.get("amount", 0) or 0)) for item in funding_events if int(item.get("month", 1) or 1) == month)


def _annual_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annual = []
    for year, start in enumerate(range(0, len(rows), 12), start=1):
        chunk = rows[start:start + 12]
        revenue = sum(row["monthly_revenue"] for row in chunk)
        net_profit = sum(row["net_profit"] for row in chunk)
        gross_profit = sum(row["gross_profit"] for row in chunk)
        annual.append({
            "year": year,
            "revenue": _money(revenue),
            "net_profit": _money(net_profit),
            "gross_margin_pct": _safe_div(gross_profit, revenue),
        })
    return annual


def _average_cac(rows: list[dict[str, Any]]) -> float | None:
    values = [
        row["marketing_costs"] / row["new_customers"]
        for row in rows
        if row.get("new_customers", 0) > 0 and row.get("marketing_costs", 0) > 0
    ]
    return sum(values) / len(values) if values else None


def _average_price(tiers: list[dict[str, Any]]) -> float:
    return sum(tier["monthly_price"] * tier["share"] for tier in tiers)


def _incomplete_sections(revenue: dict[str, Any], costs: dict[str, Any]) -> list[str]:
    missing = []
    if not revenue:
        missing.append("revenue_config")
    if not costs:
        missing.append("cost_config")
    return missing


def _unwrap_config(config: dict[str, Any] | None) -> dict[str, Any]:
    if not config:
        return {}
    value = config.get("config") if isinstance(config, dict) else None
    return value if isinstance(value, dict) else config


def _business_model(value: Any) -> str:
    normalized = str(value or "saas").strip().lower().replace("-", "_")
    aliases = {
        "subscription": "subscription",
        "saas": "saas",
        "service": "service",
        "consulting": "consulting",
    }
    return aliases.get(normalized, "saas")


def _planning_horizon(value: Any) -> int:
    try:
        months = int(value)
    except (TypeError, ValueError):
        return 36
    return months if months in VALID_HORIZONS else 36


def _rate(data: dict[str, Any], *keys: str, default: float) -> float:
    return max(0.0, _number(data, *keys, default=default))


def _number(data: dict[str, Any], *keys: str, default: float) -> float:
    for key in keys:
        if key in data and data[key] is not None:
            try:
                return float(data[key])
            except (TypeError, ValueError):
                return default
    return default


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(numerator / denominator, 4)


def _money(value: float | int | None) -> float:
    return round(float(value or 0.0), 2)


def _count(value: float | int | None) -> int:
    return max(0, int(value or 0))
