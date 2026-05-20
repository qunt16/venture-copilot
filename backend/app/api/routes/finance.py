from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.responses import ok
from app.schemas.finance import FinanceForecastCreate
from app.schemas.finance_mvp import (
    CostConfigCreate,
    CostConfigRead,
    ForecastOutputRead,
    RevenueConfigCreate,
    RevenueConfigRead,
    ValidationReportRead,
)
from app.schemas.financial_assumption import FinancialAssumptionPayload
from app.services import finance_mvp_service, finance_service, financial_assumption_service, project_service

router = APIRouter()

USER_ID = "demo_user"


@router.put("/{project_id}/finance/revenue")
async def put_revenue_config(
    project_id: str,
    body: RevenueConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    config = await finance_mvp_service.upsert_revenue_config(db, project_id, body)
    return ok(RevenueConfigRead.model_validate(config).model_dump())


@router.get("/{project_id}/finance/revenue")
async def get_revenue_config(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    config = await finance_mvp_service.get_revenue_config_model(db, project_id)
    if not config:
        raise not_found("Revenue config")
    return ok(RevenueConfigRead.model_validate(config).model_dump())


@router.put("/{project_id}/finance/costs")
async def put_cost_config(
    project_id: str,
    body: CostConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    config = await finance_mvp_service.upsert_cost_config(db, project_id, body)
    return ok(CostConfigRead.model_validate(config).model_dump())


@router.get("/{project_id}/finance/costs")
async def get_cost_config(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    config = await finance_mvp_service.get_cost_config_model(db, project_id)
    if not config:
        raise not_found("Cost config")
    return ok(CostConfigRead.model_validate(config).model_dump())


@router.get("/{project_id}/finance/forecasts")
async def list_forecast_outputs(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    outputs = await finance_mvp_service.list_forecast_outputs(db, project_id)
    return ok([ForecastOutputRead.model_validate(item).model_dump() for item in outputs])


@router.get("/{project_id}/finance/validations")
async def list_validation_reports(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    reports = await finance_mvp_service.list_validation_reports(db, project_id)
    return ok([ValidationReportRead.model_validate(item).model_dump() for item in reports])


@router.post("/{project_id}/calculate", status_code=201)
async def calculate_finance_forecast(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        forecast = await finance_mvp_service.calculate_forecast(db, project)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(ForecastOutputRead.model_validate(forecast).model_dump())


@router.get("/{project_id}/forecast")
async def get_latest_finance_forecast(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    forecast = await finance_mvp_service.get_latest_forecast_output(db, project_id)
    if not forecast:
        raise not_found("Forecast output")
    return ok(ForecastOutputRead.model_validate(forecast).model_dump())


@router.post("/{project_id}/validate", status_code=201)
async def validate_finance_forecast(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        report = await finance_mvp_service.validate_forecast(db, project)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(ValidationReportRead.model_validate(report).model_dump())


@router.get("/{project_id}/validation")
async def get_latest_finance_validation(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    report = await finance_mvp_service.get_latest_validation_report(db, project_id)
    if not report:
        raise not_found("Validation report")
    return ok(ValidationReportRead.model_validate(report).model_dump())


@router.get("/{project_id}/export/csv")
async def export_finance_csv(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        csv_text = await finance_mvp_service.export_forecast_csv(db, project_id)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{project_id}_forecast.csv"'},
    )


@router.get("/{project_id}/summary")
async def get_finance_summary(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    return ok(await finance_mvp_service.project_summary(db, project))


@router.post("/{project_id}/finance/forecast", status_code=201)
async def create_forecast(
    project_id: str,
    body: FinanceForecastCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    try:
        forecast = await finance_service.create_forecast(db, project_id, body)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(forecast.model_dump())


@router.post("/{project_id}/finance/assumptions", status_code=201)
async def create_assumptions(
    project_id: str,
    body: FinancialAssumptionPayload,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        result = await financial_assumption_service.upsert_assumptions(db, project_id, body)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(result.model_dump())


@router.get("/{project_id}/finance/assumptions")
async def get_assumptions(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    result = await financial_assumption_service.get_latest_assumptions(db, project_id)
    if not result:
        raise not_found("Financial assumptions")
    return ok(result.model_dump())


@router.patch("/{project_id}/finance/assumptions")
async def patch_assumptions(project_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        result = await financial_assumption_service.patch_assumptions(db, project_id, body)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(result.model_dump())


@router.get("/{project_id}/finance/forecast")
async def get_forecast(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    forecast = await finance_service.get_latest_forecast(db, project_id)
    if not forecast:
        raise not_found("Finance forecast")

    return ok(forecast.model_dump())
