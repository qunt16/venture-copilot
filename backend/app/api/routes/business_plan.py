from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.responses import ok
from app.schemas.template import BusinessPlanTemplateRequest
from app.services import business_plan_service, project_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/business-plan", status_code=201)
async def create_business_plan(
    project_id: str,
    body: BusinessPlanTemplateRequest = BusinessPlanTemplateRequest(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    try:
        plan = await business_plan_service.create_business_plan(db, project, body)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

    return ok(plan.model_dump())


@router.get("/{project_id}/business-plan")
async def get_business_plan(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    plan = await business_plan_service.get_latest_business_plan(db, project_id)
    if not plan:
        raise not_found("Business plan")

    return ok(plan.model_dump())
