import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance_mvp import CostConfig, ForecastOutput, RevenueConfig, ValidationReport
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
