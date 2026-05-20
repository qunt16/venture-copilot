import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.calculation_engine import calculate_forecast as run_calculation_engine
from app.finance.validation_engine import validate_forecast as run_validation_engine
from app.models.finance_mvp import CostConfig, ForecastOutput, RevenueConfig, ValidationReport
from app.models.project import Project
from app.schemas.finance_mvp import CostConfigCreate, RevenueConfigCreate


async def upsert_revenue_config(
    db: AsyncSession,
    project_id: str,
    data: RevenueConfigCreate,
) -> RevenueConfig:
    config = await get_revenue_config_model(db, project_id)
    if config:
        config.config = data.config
        await db.flush()
        await db.refresh(config)
        return config

    config = RevenueConfig(id=str(uuid.uuid4()), project_id=project_id, config=data.config)
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


async def get_revenue_config_model(db: AsyncSession, project_id: str) -> RevenueConfig | None:
    result = await db.execute(select(RevenueConfig).where(RevenueConfig.project_id == project_id))
    return result.scalar_one_or_none()


async def upsert_cost_config(
    db: AsyncSession,
    project_id: str,
    data: CostConfigCreate,
) -> CostConfig:
    config = await get_cost_config_model(db, project_id)
    if config:
        config.config = data.config
        await db.flush()
        await db.refresh(config)
        return config

    config = CostConfig(id=str(uuid.uuid4()), project_id=project_id, config=data.config)
    db.add(config)
    await db.flush()
    await db.refresh(config)
    return config


async def get_cost_config_model(db: AsyncSession, project_id: str) -> CostConfig | None:
    result = await db.execute(select(CostConfig).where(CostConfig.project_id == project_id))
    return result.scalar_one_or_none()


async def list_forecast_outputs(db: AsyncSession, project_id: str) -> list[ForecastOutput]:
    result = await db.execute(
        select(ForecastOutput)
        .where(ForecastOutput.project_id == project_id)
        .order_by(ForecastOutput.created_at.desc())
    )
    return list(result.scalars().all())


async def get_latest_forecast_output(db: AsyncSession, project_id: str) -> ForecastOutput | None:
    result = await db.execute(
        select(ForecastOutput)
        .where(ForecastOutput.project_id == project_id)
        .order_by(ForecastOutput.created_at.desc(), ForecastOutput.updated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def calculate_forecast(db: AsyncSession, project: Project) -> ForecastOutput:
    revenue_config = await get_revenue_config_model(db, project.id)
    cost_config = await get_cost_config_model(db, project.id)
    if not revenue_config:
        raise ValueError("Revenue config is required before calculation")
    if not cost_config:
        raise ValueError("Cost config is required before calculation")

    output = run_calculation_engine(
        _project_setup(project),
        revenue_config.config,
        cost_config.config,
        project.planning_horizon,
    )
    return await create_forecast_output(db, project.id, output)


async def create_forecast_output(
    db: AsyncSession,
    project_id: str,
    output: dict,
) -> ForecastOutput:
    forecast = ForecastOutput(id=str(uuid.uuid4()), project_id=project_id, output=output)
    db.add(forecast)
    await db.flush()
    await db.refresh(forecast)
    return forecast


async def list_validation_reports(db: AsyncSession, project_id: str) -> list[ValidationReport]:
    result = await db.execute(
        select(ValidationReport)
        .where(ValidationReport.project_id == project_id)
        .order_by(ValidationReport.created_at.desc())
    )
    return list(result.scalars().all())


async def get_latest_validation_report(db: AsyncSession, project_id: str) -> ValidationReport | None:
    result = await db.execute(
        select(ValidationReport)
        .where(ValidationReport.project_id == project_id)
        .order_by(ValidationReport.created_at.desc(), ValidationReport.updated_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def validate_forecast(db: AsyncSession, project: Project) -> ValidationReport:
    forecast = await get_latest_forecast_output(db, project.id)
    if not forecast:
        raise ValueError("Forecast output is required before validation")
    revenue_config = await get_revenue_config_model(db, project.id)
    cost_config = await get_cost_config_model(db, project.id)
    if not revenue_config:
        raise ValueError("Revenue config is required before validation")
    if not cost_config:
        raise ValueError("Cost config is required before validation")

    report = run_validation_engine(
        forecast.output,
        project.business_model,
        revenue_config.config,
        cost_config.config,
    )
    return await create_validation_report(db, project.id, report)


async def create_validation_report(
    db: AsyncSession,
    project_id: str,
    report: dict,
) -> ValidationReport:
    validation = ValidationReport(id=str(uuid.uuid4()), project_id=project_id, report=report)
    db.add(validation)
    await db.flush()
    await db.refresh(validation)
    return validation


def _project_setup(project: Project) -> dict:
    return {
        "industry": project.industry,
        "competition_type": project.competition_type,
        "business_model": project.business_model,
        "planning_horizon": project.planning_horizon,
    }
