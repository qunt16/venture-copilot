from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import bad_request, not_found
from app.core.responses import ok
from app.schemas.export import ExportRequest
from app.services import export_service, project_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/export/pdf", status_code=201)
async def create_pdf_export(
    project_id: str,
    body: ExportRequest = ExportRequest(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    try:
        result = await export_service.create_pdf_export(db, project, body.include_review)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

    return ok(result.model_dump())


@router.post("/{project_id}/export/docx", status_code=201)
async def create_docx_export(
    project_id: str,
    body: ExportRequest = ExportRequest(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    try:
        result = await export_service.create_docx_export(db, project, body.include_review)
    except ValueError as exc:
        raise bad_request(str(exc)) from exc

    return ok(result.model_dump())


@router.get("/{project_id}/exports")
async def list_exports(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    files = export_service.list_exports(project_id)
    return ok([file.model_dump() for file in files])
