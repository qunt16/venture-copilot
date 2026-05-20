import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.engine import run_forecast
from app.models.finance_forecast import FinanceForecast
from app.schemas.finance import FinanceForecastCreate, FinanceForecastRead
from app.services.financial_assumption_service import get_latest_assumption_model


async def create_forecast(
    db: AsyncSession, project_id: str, data: FinanceForecastCreate
) -> FinanceForecastRead:
    assumption = await get_latest_assumption_model(db, project_id)
    if not assumption or not assumption.confirmed:
        raise ValueError("Confirmed financial assumptions are required before forecast generation")
    forecast_data = run_forecast(data)

    forecast = FinanceForecast(
        id=str(uuid.uuid4()),
        project_id=project_id,
        inputs=data.model_dump(),
        monthly_rows=forecast_data["monthly_rows"],
        summary=forecast_data,
    )
    db.add(forecast)
    await db.flush()
    await db.refresh(forecast)

    return _to_read(forecast)


async def get_latest_forecast(
    db: AsyncSession, project_id: str
) -> Optional[FinanceForecastRead]:
    result = await db.execute(
        select(FinanceForecast)
        .where(FinanceForecast.project_id == project_id)
        .order_by(FinanceForecast.created_at.desc())
        .limit(1)
    )
    forecast = result.scalar_one_or_none()
    if not forecast:
        return None
    return _to_read(forecast)


def _to_read(forecast: FinanceForecast) -> FinanceForecastRead:
    stored = forecast.summary or {}
    if "summary" in stored and "monthly_rows" in stored:
        forecast_data = stored
    else:
        forecast_data = {
            "summary": stored,
            "monthly_rows": forecast.monthly_rows or [],
            "income_statement": [],
            "cash_flow_statement": [],
            "balance_sheet": [],
            "financing_needs": {"funding_needed": stored.get("funding_needed", 0)},
            "break_even": {"breakeven_month": stored.get("breakeven_month"), "breakeven_revenue": None},
            "valuation": {"npv": None, "irr": None, "roi": None, "dcf_value": None},
            "sensitivity_analysis": [],
            "markdown_tables": {},
            "csv_exports": {},
            "charts": {},
        }
    return FinanceForecastRead(
        id=forecast.id,
        project_id=forecast.project_id,
        assumptions=forecast.inputs or {},
        summary=forecast_data.get("summary", {}),
        months=forecast_data.get("monthly_rows", []),
        forecast_data=forecast_data,
        markdown_tables=forecast_data.get("markdown_tables", {}),
        csv_exports=forecast_data.get("csv_exports", {}),
        charts=forecast_data.get("charts", {}),
    )
