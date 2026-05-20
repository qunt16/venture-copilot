import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.charts import generate_finance_charts
from app.finance.engine import run_forecast
from app.finance.interpreter import interpret_forecast
from app.models.finance_forecast import FinanceForecast
from app.models.financial_assumption import FinancialAssumption
from app.schemas.finance import FinanceForecastCreate
from app.schemas.financial_assumption import FinancialAssumptionPayload, FinancialAssumptionRead


async def upsert_assumptions(db: AsyncSession, project_id: str, payload: FinancialAssumptionPayload) -> FinancialAssumptionRead:
    warnings = validate_assumptions(payload)
    if payload.ai_suggested and not payload.confirmed:
        warnings.append("AI 建议数字处于待用户确认状态，不能进入预测。")
        assumption = await _save_assumption(db, project_id, payload, warnings)
        return _to_read(assumption, None, None)
    assumption = await _save_assumption(db, project_id, payload, warnings)
    forecast = await recalculate_from_assumptions(db, project_id, assumption)
    return _to_read(assumption, forecast.summary, forecast.summary.get("interpretation"))


async def patch_assumptions(db: AsyncSession, project_id: str, updates: dict) -> FinancialAssumptionRead:
    current = await get_latest_assumption_model(db, project_id)
    if not current:
        raise ValueError("Financial assumptions required before patch")
    merged = {**(current.assumptions or {}), **updates}
    return await upsert_assumptions(db, project_id, FinancialAssumptionPayload(**merged))


async def get_latest_assumptions(db: AsyncSession, project_id: str) -> FinancialAssumptionRead | None:
    assumption = await get_latest_assumption_model(db, project_id)
    if not assumption:
        return None
    forecast = await _latest_forecast(db, project_id)
    return _to_read(assumption, forecast.summary if forecast else None, (forecast.summary or {}).get("interpretation") if forecast else None)


async def get_latest_assumption_model(db: AsyncSession, project_id: str) -> FinancialAssumption | None:
    result = await db.execute(
        select(FinancialAssumption)
        .where(FinancialAssumption.project_id == project_id)
        .order_by(FinancialAssumption.updated_at.desc(), FinancialAssumption.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def recalculate_from_assumptions(
    db: AsyncSession,
    project_id: str,
    assumption: FinancialAssumption | None = None,
) -> FinanceForecast:
    assumption = assumption or await get_latest_assumption_model(db, project_id)
    if not assumption:
        raise ValueError("Missing financial assumptions")
    if not assumption.confirmed:
        raise ValueError("Financial assumptions are not confirmed")
    data = forecast_input_from_assumptions(assumption.assumptions)
    forecast_data = run_forecast(data)
    interpretation = interpret_forecast(forecast_data, assumption.assumptions)
    charts = generate_finance_charts(project_id, forecast_data)
    forecast_data["interpretation"] = interpretation
    forecast_data["chart_files"] = charts
    forecast = FinanceForecast(
        id=str(uuid.uuid4()),
        project_id=project_id,
        inputs=assumption.assumptions,
        monthly_rows=forecast_data["monthly_rows"],
        summary=forecast_data,
    )
    db.add(forecast)
    await db.flush()
    await db.refresh(forecast)
    return forecast


def validate_assumptions(payload: FinancialAssumptionPayload) -> list[str]:
    warnings = []
    if payload.growth_rate > 0.25:
        warnings.append("增长率高于 25%，请确认是否有渠道、产能和市场证据支撑。")
    if payload.price and payload.unit_cost / payload.price > 0.8:
        warnings.append("单位成本接近售价，毛利空间较低。")
    if payload.cac and payload.ltv and payload.cac > payload.ltv:
        warnings.append("CAC 高于 LTV，获客经济性存在风险。")
    if payload.ai_suggested:
        warnings.append("包含 AI 建议数字，请用户确认后再用于正式预测。")
    return warnings


def forecast_input_from_assumptions(data: dict) -> FinanceForecastCreate:
    price = float(data.get("price") or 0)
    unit_cost = float(data.get("unit_cost") or 0)
    first_units = float(data.get("first_month_units") or 0)
    variable_cost_rate = min(unit_cost / price, 1.0) if price else 0.0
    fixed_costs = (
        float(data.get("fixed_costs") or 0)
        + float(data.get("marketing_budget") or 0)
        + float(data.get("employee_costs") or 0)
        + float(data.get("r_and_d_costs") or 0)
        + float(data.get("channel_costs") or 0)
    )
    return FinanceForecastCreate(
        starting_revenue=price * first_units,
        monthly_growth_rate=float(data.get("growth_rate") or 0),
        gross_margin=max(0.0, min(1.0, 1 - variable_cost_rate)),
        fixed_monthly_costs=fixed_costs,
        variable_cost_rate=variable_cost_rate,
        starting_cash=float(data.get("startup_funds") or 0),
        months=int(data.get("forecast_months") or 36),
        discount_rate=0.1,
        initial_investment=float(data.get("startup_funds") or 0),
        financing_amount=float(data.get("financing_amount") or 0),
    )


async def _save_assumption(
    db: AsyncSession,
    project_id: str,
    payload: FinancialAssumptionPayload,
    warnings: list[str],
) -> FinancialAssumption:
    current = await get_latest_assumption_model(db, project_id)
    if current:
        current.assumptions = payload.model_dump()
        current.warnings = warnings
        current.confirmed = payload.confirmed
        await db.flush()
        await db.refresh(current)
        return current
    assumption = FinancialAssumption(
        id=str(uuid.uuid4()),
        project_id=project_id,
        assumptions=payload.model_dump(),
        warnings=warnings,
        confirmed=payload.confirmed,
    )
    db.add(assumption)
    await db.flush()
    await db.refresh(assumption)
    return assumption


async def _latest_forecast(db: AsyncSession, project_id: str) -> FinanceForecast | None:
    result = await db.execute(
        select(FinanceForecast)
        .where(FinanceForecast.project_id == project_id)
        .order_by(FinanceForecast.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _to_read(assumption: FinancialAssumption, forecast: dict | None, interpretation: dict | None) -> FinancialAssumptionRead:
    return FinancialAssumptionRead(
        id=assumption.id,
        project_id=assumption.project_id,
        assumptions=assumption.assumptions,
        warnings=assumption.warnings or [],
        confirmed=assumption.confirmed,
        forecast=forecast,
        interpretation=interpretation,
        created_at=assumption.created_at,
        updated_at=assumption.updated_at,
    )
