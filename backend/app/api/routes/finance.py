from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.responses import ok
from app.schemas.finance import FinanceForecastCreate
from app.schemas.financial_assumption import FinancialAssumptionPayload
from app.services import finance_service, financial_assumption_service, project_service

router = APIRouter()

USER_ID = "demo_user"


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
