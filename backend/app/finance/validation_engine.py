from __future__ import annotations

from typing import Any


def validate_forecast(
    forecast_output: dict[str, Any] | None,
    business_model: str | None,
    revenue_config: dict[str, Any] | None,
    cost_config: dict[str, Any] | None,
) -> dict[str, Any]:
    forecast = forecast_output or {}
    revenue = _unwrap_config(revenue_config)
    costs = _unwrap_config(cost_config)
    model = _normalize_model(business_model or forecast.get("business_model"))
    rows = forecast.get("monthly_rows") or []
    summary = forecast.get("summary") or {}
    issues: list[dict[str, Any]] = []

    issues.extend(_cashflow_rules(rows, summary, costs))
    issues.extend(_revenue_rules(rows, model, revenue))
    if model in {"saas", "subscription"}:
        issues.extend(_churn_rules(rows, revenue))
        issues.extend(_unit_economics_rules(summary, costs))
    issues.extend(_cost_completeness_rules(rows, model, costs))
    issues.extend(_margin_rules(rows, summary, model))

    return {
        "summary_narrative": None,
        "judge_perspective": None,
        "issue_count": {
            "errors": sum(1 for issue in issues if issue["severity"] == "error"),
            "warnings": sum(1 for issue in issues if issue["severity"] == "warning"),
            "suggestions": sum(1 for issue in issues if issue["severity"] == "suggestion"),
        },
        "issues": issues,
    }


def _cashflow_rules(rows: list[dict[str, Any]], summary: dict[str, Any], costs: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    first_cash = _row_value(rows, 0, "cumulative_cash_balance", "cash_balance")
    starting_cash = _number(costs, "starting_cash", "starting_cash_balance", default=0.0)
    runway = summary.get("runway_months")

    if first_cash is not None and first_cash < 0:
        issues.append(_issue(
            "CF-001",
            "error",
            "Starting cash is negative",
            "Starting cash is zero or negative, so the model cannot run from Month 1.",
            "Add starting cash, reduce Month 1 costs, or model a confirmed funding event.",
            ["costs.starting_cash", "forecast.monthly_rows[0].cash_balance"],
        ))

    if starting_cash == 0 and rows and all((_row_value([row], 0, "cumulative_cash_balance", "cash_balance") or 0) <= 0 for row in rows):
        issues.append(_issue(
            "CF-002",
            "error",
            "No financial foundation",
            "No starting cash and no funding are defined, so cash balance never exceeds zero.",
            "Add a realistic starting cash balance or a confirmed funding event.",
            ["costs.starting_cash", "costs.funding_events"],
        ))

    if runway is not None and runway < 6:
        issues.append(_issue(
            "CF-003",
            "warning",
            "Runway under 6 months",
            "Runway is under 6 months; most competitions and investors expect at least 12 months.",
            "Increase starting cash or funding, reduce burn, or phase costs more gradually.",
            ["forecast.summary.runway_months", "costs.starting_cash", "costs.fixed_monthly_costs"],
        ))
    elif runway is not None and 6 <= runway < 12:
        issues.append(_issue(
            "CF-004",
            "warning",
            "Runway between 6 and 12 months",
            "Runway is between 6 and 12 months, which may look tight to judges.",
            "Consider modeling a funding event or reducing monthly burn.",
            ["forecast.summary.runway_months", "costs.funding_events"],
        ))
    elif runway is not None and 12 <= runway < 18:
        issues.append(_issue(
            "CF-005",
            "suggestion",
            "Runway below 18-month benchmark",
            "Runway is healthy but tighter than the 18-month benchmark many seed investors prefer.",
            "Explain why the shorter runway is acceptable or add a realistic funding milestone.",
            ["forecast.summary.runway_months"],
        ))

    return issues


def _revenue_rules(rows: list[dict[str, Any]], model: str, revenue: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    growth_rate = _monthly_growth_rate(revenue, model)
    month_1_revenue = _row_value(rows, 0, "monthly_revenue", "revenue")
    month_12_revenue = _row_value(rows, 11, "monthly_revenue", "revenue")
    initial_customers = _initial_customers(revenue, model)

    if growth_rate > 0.30:
        issues.append(_issue(
            "REV-001",
            "warning",
            "Aggressive monthly growth",
            "Monthly growth above 30% is aggressive and will need strong evidence.",
            "Add a clear acquisition rationale or lower the monthly growth assumption.",
            ["revenue.monthly_growth_rate"],
        ))
    if growth_rate > 0.50:
        issues.append(_issue(
            "REV-002",
            "warning",
            "Very aggressive monthly growth",
            "Monthly growth above 50% is rarely seen outside viral consumer apps.",
            "Use a more defensible growth rate or document a specific viral/channel strategy.",
            ["revenue.monthly_growth_rate"],
        ))
    if month_1_revenue and month_12_revenue and month_12_revenue > month_1_revenue * 50:
        issues.append(_issue(
            "REV-003",
            "warning",
            "Year 1 revenue grows over 50x",
            "Year 1 revenue grows more than 50x, which may signal unrealistic growth.",
            "Check customer growth and pricing assumptions, then document the acquisition plan.",
            ["forecast.monthly_rows[11].monthly_revenue", "revenue.monthly_growth_rate"],
        ))
    if month_1_revenue == 0 and initial_customers == 0 and model != "pre_launch":
        issues.append(_issue(
            "REV-004",
            "error",
            "Month 1 revenue is zero",
            "Month 1 revenue is zero; verify pricing and initial customer count.",
            "Enter a price and initial customers, or explicitly mark the model as pre-launch later.",
            ["revenue.price", "revenue.initial_customers"],
        ))
    if initial_customers > 1000:
        # Round 1/2 do not yet model a formal pre-revenue/pre-competition flag, so this applies
        # whenever the available initial customer count alone is enough to raise the concern.
        issues.append(_issue(
            "REV-005",
            "suggestion",
            "High initial customer count",
            "1,000+ initial customers in Month 1 is a strong assumption for a student startup.",
            "Be ready to explain the acquisition source and evidence behind this starting point.",
            ["revenue.initial_customers"],
        ))

    return issues


def _churn_rules(rows: list[dict[str, Any]], revenue: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    churn_rate = _number(revenue, "monthly_churn_rate", "churn_rate", default=0.0)

    if churn_rate >= 0.10:
        issues.append(_issue(
            "CHURN-001",
            "warning",
            "High monthly churn",
            "Monthly churn of 10%+ means you lose over half your customers each year.",
            "Lower churn only if you have evidence, or explain retention tactics clearly.",
            ["revenue.churn_rate"],
        ))
    if any((row.get("new_customers") or 0) < (row.get("churned_customers") or 0) for row in rows[:12]):
        issues.append(_issue(
            "CHURN-002",
            "warning",
            "Churn exceeds acquisition",
            "Churn exceeds new customer acquisition in at least one of the first 12 months.",
            "Improve acquisition, reduce churn, or explain why temporary contraction is acceptable.",
            ["forecast.monthly_rows.new_customers", "forecast.monthly_rows.churned_customers"],
        ))
    if churn_rate == 0:
        issues.append(_issue(
            "CHURN-003",
            "suggestion",
            "Zero churn assumption",
            "Zero churn is unrealistic for most subscription businesses.",
            "Use a modest churn assumption such as 1–2% monthly unless you can justify zero churn.",
            ["revenue.churn_rate"],
        ))

    return issues


def _unit_economics_rules(summary: dict[str, Any], costs: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    ltv = summary.get("ltv")
    cac = summary.get("cac")
    ratio = summary.get("ltv_cac_ratio")
    marketing_spend = _marketing_spend(costs)

    if ltv is not None and cac is not None and ltv < cac:
        issues.append(_issue(
            "UNIT-001",
            "warning",
            "LTV below CAC",
            "Customer Lifetime Value is less than Customer Acquisition Cost.",
            "Reduce acquisition cost, improve retention, or raise ARPU before presenting this model.",
            ["forecast.summary.ltv", "forecast.summary.cac"],
        ))
    if ratio is not None and ratio < 3:
        issues.append(_issue(
            "UNIT-002",
            "warning",
            "LTV:CAC below 3:1",
            "LTV:CAC ratio is below the general SaaS benchmark of 3:1.",
            "Improve LTV or lower CAC until the ratio is closer to a sustainable range.",
            ["forecast.summary.ltv_cac_ratio"],
        ))
    if ratio is not None and 3 <= ratio < 5:
        issues.append(_issue(
            "UNIT-003",
            "suggestion",
            "Healthy but improvable LTV:CAC",
            "LTV:CAC is in the healthy range, while strong models often target 5:1 or above.",
            "Explain why the current acquisition economics are acceptable for this stage.",
            ["forecast.summary.ltv_cac_ratio"],
        ))
    if cac is None or marketing_spend == 0:
        issues.append(_issue(
            "UNIT-004",
            "suggestion",
            "CAC cannot be supported",
            "No marketing spend is defined, so CAC will appear as zero or undefined.",
            "Add a realistic marketing budget so judges can evaluate acquisition economics.",
            ["costs.marketing_budget", "forecast.summary.cac"],
        ))

    return issues


def _cost_completeness_rules(rows: list[dict[str, Any]], model: str, costs: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []
    fixed_month_1 = _row_value(rows, 0, "fixed_costs") or 0
    marketing_spend = _marketing_spend(costs)

    if model in {"saas", "subscription"} and not _has_hosting_or_api_cost(costs):
        issues.append(_issue(
            "COST-001",
            "warning",
            "Missing hosting or API cost",
            "SaaS products typically have hosting or API costs, but these are missing.",
            "Add hosting, API, infrastructure, or server costs as variable or fixed costs.",
            ["costs.variable_costs", "costs.fixed_cost_items"],
        ))

    # COST-002 is product-specific and skipped in Round 3 because product models are not
    # implemented in the Round 2 calculation engine.

    if fixed_month_1 < 500:
        issues.append(_issue(
            "COST-003",
            "suggestion",
            "Very low fixed costs",
            "Month 1 fixed costs are under $500, which may omit common startup costs.",
            "Check software, hosting, domain, accounting, legal, and operating subscriptions.",
            ["costs.fixed_monthly_costs"],
        ))

    # COST-004 depends on a richer team/headcount intent model. Round 1/2 only expose
    # optional headcount line items, so there is no reliable way to know intended roles.

    if marketing_spend < 100:
        issues.append(_issue(
            "COST-005",
            "suggestion",
            "Low or missing marketing budget",
            "No meaningful marketing budget is defined, so judges may question acquisition.",
            "Add a first-customer marketing budget or explain organic acquisition assumptions.",
            ["costs.marketing_budget"],
        ))

    return issues


def _margin_rules(rows: list[dict[str, Any]], summary: dict[str, Any], model: str) -> list[dict[str, Any]]:
    issues = []
    year_1_rows = rows[:12]
    year_1_revenue = sum(row.get("monthly_revenue", row.get("revenue", 0)) or 0 for row in year_1_rows)
    year_1_gross_profit = sum(row.get("gross_profit", 0) or 0 for row in year_1_rows)
    avg_margin = None if year_1_revenue == 0 else year_1_gross_profit / year_1_revenue
    break_even_month = summary.get("break_even_month")

    if model in {"saas", "subscription"} and avg_margin is not None and avg_margin < 0.50:
        issues.append(_issue(
            "MARGIN-001",
            "warning",
            "Low SaaS gross margin",
            "Gross margin below 50% is unusual for SaaS.",
            "Review variable infrastructure, API, and delivery costs or explain the margin profile.",
            ["forecast.summary.gross_margin_pct", "costs.variable_costs"],
        ))

    # MARGIN-002 is product-specific and skipped in Round 3 because product models are not
    # implemented in the Round 2 calculation engine.

    if avg_margin is not None and avg_margin < 0:
        issues.append(_issue(
            "MARGIN-003",
            "warning",
            "Negative gross margin",
            "Negative gross margin means direct costs exceed revenue.",
            "Reduce variable costs or increase price before scaling sales.",
            ["forecast.summary.gross_margin_pct", "costs.variable_costs", "revenue.price"],
        ))
    if break_even_month is None:
        issues.append(_issue(
            "MARGIN-004",
            "suggestion",
            "Break-even not reached",
            "The model does not reach break-even within the forecast period.",
            "Show a credible path to profitability by adjusting growth, pricing, or cost timing.",
            ["forecast.summary.break_even_month"],
        ))

    return issues


def _issue(
    rule_id: str,
    severity: str,
    title: str,
    description: str,
    fix_suggestion: str,
    affected_fields: list[str],
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "title": title,
        "description": description,
        "fix_suggestion": fix_suggestion,
        "affected_fields": affected_fields,
    }


def _unwrap_config(config: dict[str, Any] | None) -> dict[str, Any]:
    if not config:
        return {}
    value = config.get("config") if isinstance(config, dict) else None
    return value if isinstance(value, dict) else config


def _normalize_model(value: str | None) -> str:
    normalized = str(value or "saas").strip().lower().replace("-", "_")
    if normalized in {"subscription", "saas"}:
        return normalized
    if normalized in {"service", "consulting"}:
        return normalized
    if normalized == "pre_launch":
        return normalized
    return "saas"


def _monthly_growth_rate(revenue: dict[str, Any], model: str) -> float:
    if model in {"service", "consulting"}:
        return _number(revenue, "monthly_client_growth_rate", "client_growth_rate", "growth_rate", default=0.0)
    return _number(revenue, "monthly_growth_rate", "growth_rate", default=0.0)


def _initial_customers(revenue: dict[str, Any], model: str) -> int:
    if model in {"service", "consulting"}:
        return int(_number(revenue, "initial_clients", "active_clients", "month_1_clients", default=0.0))
    tiers = revenue.get("pricing_tiers") or revenue.get("tiers")
    if tiers:
        return int(sum(_number(tier, "initial_customers", "month_1_customers", default=0.0) for tier in tiers))
    return int(_number(revenue, "initial_customers", "month_1_customers", "starting_customers", default=0.0))


def _marketing_spend(costs: dict[str, Any]) -> float:
    return _number(costs, "marketing_costs", "marketing_budget", "monthly_marketing_budget", default=0.0)


def _has_hosting_or_api_cost(costs: dict[str, Any]) -> bool:
    keywords = ("hosting", "api", "server", "infrastructure", "cloud")
    for collection_name in ("variable_costs", "fixed_cost_items", "fixed_cost_line_items"):
        for item in costs.get(collection_name) or []:
            text = " ".join(str(item.get(key, "")) for key in ("category", "label", "description", "name")).lower()
            if any(keyword in text for keyword in keywords):
                return True
    return False


def _row_value(rows: list[dict[str, Any]], index: int, *keys: str) -> float | None:
    if index >= len(rows):
        return None
    row = rows[index]
    for key in keys:
        if key in row and row[key] is not None:
            return float(row[key])
    return None


def _number(data: dict[str, Any], *keys: str, default: float) -> float:
    for key in keys:
        if key in data and data[key] is not None:
            try:
                return float(data[key])
            except (TypeError, ValueError):
                return default
    return default
