from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.responses import ok
from app.schemas.framework import FrameworkAnalysisRequest
from app.services import framework_service, project_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/frameworks/analyze", status_code=201)
async def create_framework_analysis(
    project_id: str,
    body: FrameworkAnalysisRequest = FrameworkAnalysisRequest(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    try:
        analysis = await framework_service.create_analysis(db, project, body)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(analysis.model_dump())


@router.get("/{project_id}/frameworks/analysis")
async def get_framework_analysis(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    analysis = await framework_service.get_latest_analysis(db, project_id)
    if not analysis:
        raise not_found("Framework analysis")
    return ok(analysis.model_dump())
