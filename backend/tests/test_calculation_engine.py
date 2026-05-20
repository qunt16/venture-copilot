from app.finance.calculation_engine import calculate_forecast


def test_saas_revenue_growth():
    result = calculate_forecast(
        {"business_model": "saas", "planning_horizon": 12},
        {"monthly_price": 100, "initial_customers": 10, "monthly_growth_rate": 0.1, "churn_rate": 0},
        {"starting_cash": 10000},
    )

    rows = result["monthly_rows"]
    assert len(rows) == 12
    assert rows[0]["active_customers"] == 10
    assert rows[1]["new_customers"] == 11
    assert rows[1]["active_customers"] == 21
    assert rows[1]["monthly_revenue"] == 2100.0
    assert result["summary"]["mrr"] > rows[0]["mrr"]


def test_saas_churn_behavior_clamps_customers_to_zero():
    result = calculate_forecast(
        {"business_model": "subscription", "planning_horizon": 12},
        {"monthly_price": 50, "initial_customers": 1, "monthly_growth_rate": 0, "churn_rate": 2.0},
        {"starting_cash": 0},
    )

    rows = result["monthly_rows"]
    assert rows[1]["churned_customers"] == 2
    assert rows[1]["active_customers"] == 0
    assert all(row["active_customers"] >= 0 for row in rows)


def test_cash_balance_calculation():
    result = calculate_forecast(
        {"business_model": "saas", "planning_horizon": 12},
        {"monthly_price": 100, "initial_customers": 1, "monthly_growth_rate": 0, "churn_rate": 0},
        {"starting_cash": 1000, "fixed_monthly_costs": 200, "variable_cost_rate": 0.1},
    )

    first = result["monthly_rows"][0]
    assert first["monthly_revenue"] == 100.0
    assert first["variable_costs"] == 10.0
    assert first["net_cashflow"] == -110.0
    assert first["cumulative_cash_balance"] == 890.0


def test_runway_and_zero_cash_month():
    result = calculate_forecast(
        {"business_model": "service", "planning_horizon": 12},
        {"initial_clients": 0, "average_monthly_revenue_per_client": 0},
        {"starting_cash": 500, "fixed_monthly_costs": 200},
    )

    assert result["summary"]["zero_cash_month"] == 3
    assert result["summary"]["runway_months"] == 2


def test_break_even_calculation():
    result = calculate_forecast(
        {"business_model": "service", "planning_horizon": 12},
        {
            "initial_clients": 1,
            "monthly_client_growth_rate": 1.0,
            "average_monthly_revenue_per_client": 100,
            "completion_rate": 0,
        },
        {"starting_cash": 1000, "fixed_monthly_costs": 250},
    )

    assert result["monthly_rows"][0]["net_profit"] == -150.0
    assert result["summary"]["break_even_month"] == 2


def test_zero_revenue_zero_cost_edge_case():
    result = calculate_forecast(
        {"business_model": "saas", "planning_horizon": 12},
        {},
        {},
    )

    first = result["monthly_rows"][0]
    assert first["monthly_revenue"] == 0.0
    assert first["total_costs"] == 0.0
    assert first["gross_margin_pct"] is None
    assert result["summary"]["zero_cash_month"] is None
    assert result["summary"]["runway_months"] == 12


def test_division_by_zero_metrics_are_none():
    result = calculate_forecast(
        {"business_model": "saas", "planning_horizon": 12},
        {"monthly_price": 0, "initial_customers": 0, "churn_rate": 0},
        {"marketing_budget": 0},
    )

    summary = result["summary"]
    assert summary["ltv"] is None
    assert summary["cac"] is None
    assert summary["ltv_cac_ratio"] is None
    assert summary["arpu"] is None
