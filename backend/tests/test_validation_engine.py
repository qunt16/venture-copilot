from app.finance.calculation_engine import calculate_forecast
from app.finance.validation_engine import validate_forecast


def _rule_ids(report):
    return {issue["rule_id"] for issue in report["issues"]}


def _saas_forecast(revenue=None, costs=None):
    revenue_config = {
        "monthly_price": 100,
        "initial_customers": 20,
        "monthly_growth_rate": 0.1,
        "churn_rate": 0.03,
        **(revenue or {}),
    }
    cost_config = {
        "starting_cash": 100000,
        "fixed_monthly_costs": 2000,
        "marketing_budget": 1000,
        "variable_costs": [{"category": "hosting", "basis": "percent_of_revenue", "rate": 0.1}],
        **(costs or {}),
    }
    forecast = calculate_forecast({"business_model": "saas", "planning_horizon": 36}, revenue_config, cost_config)
    return validate_forecast(forecast, "saas", revenue_config, cost_config)


def test_healthy_model_has_no_errors():
    report = _saas_forecast()

    assert report["issue_count"]["errors"] == 0


def test_runway_under_6_months_triggers_cf_003():
    revenue = {"initial_clients": 0, "average_monthly_revenue_per_client": 0}
    costs = {"starting_cash": 500, "fixed_monthly_costs": 200}
    forecast = calculate_forecast({"business_model": "service", "planning_horizon": 12}, revenue, costs)

    report = validate_forecast(forecast, "service", revenue, costs)

    assert "CF-003" in _rule_ids(report)


def test_monthly_growth_over_30_triggers_rev_001():
    report = _saas_forecast({"monthly_growth_rate": 0.31})

    assert "REV-001" in _rule_ids(report)


def test_monthly_growth_over_50_triggers_rev_002():
    report = _saas_forecast({"monthly_growth_rate": 0.51})

    assert "REV-001" in _rule_ids(report)
    assert "REV-002" in _rule_ids(report)


def test_churn_over_10_triggers_churn_001():
    report = _saas_forecast({"churn_rate": 0.10})

    assert "CHURN-001" in _rule_ids(report)


def test_zero_churn_triggers_churn_003():
    report = _saas_forecast({"churn_rate": 0})

    assert "CHURN-003" in _rule_ids(report)


def test_ltv_below_cac_triggers_unit_001():
    report = _saas_forecast(
        {"monthly_price": 100, "initial_customers": 10, "monthly_growth_rate": 0, "churn_rate": 0.10},
        {"marketing_budget": 50000},
    )

    assert "UNIT-001" in _rule_ids(report)


def test_ltv_cac_under_3_triggers_unit_002():
    report = _saas_forecast(
        {"monthly_price": 100, "initial_customers": 10, "monthly_growth_rate": 0, "churn_rate": 0.05},
        {"marketing_budget": 10000},
    )

    assert "UNIT-002" in _rule_ids(report)


def test_missing_saas_server_api_cost_triggers_cost_001():
    report = _saas_forecast(costs={"variable_costs": []})

    assert "COST-001" in _rule_ids(report)


def test_negative_gross_margin_triggers_margin_003():
    report = _saas_forecast(costs={
        "variable_costs": [{"category": "hosting", "basis": "percent_of_revenue", "rate": 1.2}]
    })

    assert "MARGIN-003" in _rule_ids(report)


def test_break_even_not_reached_triggers_margin_004():
    revenue = {
        "initial_clients": 1,
        "average_monthly_revenue_per_client": 100,
        "monthly_client_growth_rate": 0,
        "completion_rate": 1.0,
    }
    costs = {"starting_cash": 10000, "fixed_monthly_costs": 500}
    forecast = calculate_forecast({"business_model": "service", "planning_horizon": 12}, revenue, costs)

    report = validate_forecast(forecast, "service", revenue, costs)

    assert "MARGIN-004" in _rule_ids(report)
