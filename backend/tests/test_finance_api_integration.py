import pytest
from httpx import ASGITransport, AsyncClient

from app.ai.base import AIProviderError
import app.finance.ai_narrative as ai_narrative
from app.main import app


@pytest.mark.asyncio
async def test_finance_round4_calculate_validate_flow(monkeypatch):
    def fail_provider(_config):
        raise AIProviderError("openrouter disabled in test")

    monkeypatch.setattr(ai_narrative, "get_provider", fail_provider)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        project = await client.post(
            "/projects",
            json={
                "title": "Round 4 API Test",
                "idea_summary": "Finance API integration smoke test",
                "industry": "education technology",
                "competition_type": "challenge_cup",
                "business_model": "saas",
                "planning_horizon": 12,
            },
        )
        assert project.status_code == 201
        project_id = project.json()["data"]["id"]

        revenue = await client.put(
            f"/projects/{project_id}/finance/revenue",
            json={
                "config": {
                    "monthly_price": 100,
                    "initial_customers": 20,
                    "monthly_growth_rate": 0.1,
                    "churn_rate": 0.03,
                }
            },
        )
        assert revenue.status_code == 200

        costs = await client.put(
            f"/projects/{project_id}/finance/costs",
            json={
                "config": {
                    "starting_cash": 100000,
                    "fixed_monthly_costs": 2000,
                    "marketing_budget": 1000,
                    "variable_costs": [
                        {"category": "hosting", "basis": "percent_of_revenue", "rate": 0.1}
                    ],
                }
            },
        )
        assert costs.status_code == 200

        calculated = await client.post(f"/projects/{project_id}/calculate")
        assert calculated.status_code == 201
        forecast_data = calculated.json()["data"]
        assert forecast_data["project_id"] == project_id
        assert forecast_data["output"]["planning_horizon"] == 12
        assert forecast_data["output"]["monthly_rows"][0]["monthly_revenue"] == 2000.0

        forecast = await client.get(f"/projects/{project_id}/forecast")
        assert forecast.status_code == 200
        assert forecast.json()["data"]["id"] == forecast_data["id"]

        validated = await client.post(f"/projects/{project_id}/validate")
        assert validated.status_code == 201
        validation_data = validated.json()["data"]
        assert validation_data["project_id"] == project_id
        assert "issue_count" in validation_data["report"]
        assert validation_data["report"]["issue_count"]["errors"] == 0

        validation = await client.get(f"/projects/{project_id}/validation")
        assert validation.status_code == 200
        assert validation.json()["data"]["id"] == validation_data["id"]

        csv_export = await client.get(f"/projects/{project_id}/export/csv")
        assert csv_export.status_code == 200
        assert "text/csv" in csv_export.headers["content-type"]
        assert "month, new_customers".replace(" ", "")[:5] in csv_export.text.replace(" ", "")[:20]
        assert "monthly_revenue" in csv_export.text

        summary = await client.get(f"/projects/{project_id}/summary")
        assert summary.status_code == 200
        summary_data = summary.json()["data"]
        assert summary_data["project"]["id"] == project_id
        assert "total_revenue" in summary_data["forecast_metrics"]
        assert summary_data["validation_issue_counts"]["errors"] == 0

        missing_config_project = await client.post(
            "/projects",
            json={
                "title": "Round 4 Missing Config Test",
                "idea_summary": "Missing config check",
                "business_model": "saas",
                "planning_horizon": 12,
            },
        )
        assert missing_config_project.status_code == 201
        missing_config_project_id = missing_config_project.json()["data"]["id"]

        missing_config_response = await client.post(f"/projects/{missing_config_project_id}/calculate")

        assert missing_config_response.status_code == 400
        missing_config_body = missing_config_response.json()
        assert missing_config_body["success"] is False
        assert "Revenue config is required" in missing_config_body["message"]

        missing_forecast_project = await client.post(
            "/projects",
            json={
                "title": "Round 4 Missing Forecast Test",
                "idea_summary": "Missing forecast check",
                "business_model": "service",
                "planning_horizon": 12,
            },
        )
        assert missing_forecast_project.status_code == 201
        missing_forecast_project_id = missing_forecast_project.json()["data"]["id"]

        await client.put(
            f"/projects/{missing_forecast_project_id}/finance/revenue",
            json={"config": {"initial_clients": 2, "average_monthly_revenue_per_client": 1000}},
        )
        await client.put(
            f"/projects/{missing_forecast_project_id}/finance/costs",
            json={"config": {"starting_cash": 5000, "fixed_monthly_costs": 500}},
        )
        missing_forecast_response = await client.post(f"/projects/{missing_forecast_project_id}/validate")

        assert missing_forecast_response.status_code == 400
        missing_forecast_body = missing_forecast_response.json()
        assert missing_forecast_body["success"] is False
        assert "Forecast output is required" in missing_forecast_body["message"]
