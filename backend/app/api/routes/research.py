from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import not_found
from app.core.responses import ok
from app.core.errors import bad_request
from app.schemas.research import ResearchReportRequest
from app.services import project_service, research_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/research", status_code=201)
async def create_research_report(
    project_id: str,
    body: ResearchReportRequest = ResearchReportRequest(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    try:
        report = await research_service.create_research_report(db, project, body.ai_config, body.research_config)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc
    return ok(report.model_dump())


@router.get("/{project_id}/research")
async def get_research_report(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    report = await research_service.get_latest_research_report(db, project_id)
    if not report:
        raise not_found("Research report")

    return ok(report.model_dump())
