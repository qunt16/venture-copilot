from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import not_found
from app.core.responses import ok
from app.schemas.document import CommentCreate, CommentResolve, DocumentAutosaveRequest
from app.services import document_service, project_service

router = APIRouter()

USER_ID = "demo_user"


@router.get("/{project_id}/document/blocks")
async def get_blocks(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    blocks = await document_service.get_blocks(db, project_id)
    return ok([block.model_dump() for block in blocks])


@router.patch("/{project_id}/document/autosave")
async def autosave(project_id: str, body: DocumentAutosaveRequest, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    blocks = await document_service.autosave_blocks(db, project_id, body)
    return ok([block.model_dump() for block in blocks])


@router.post("/{project_id}/sections/{section_id}/comment", status_code=201)
async def create_comment(
    project_id: str,
    section_id: str,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    comment = await document_service.create_comment(db, project_id, section_id, body)
    return ok(comment.model_dump())


@router.get("/{project_id}/sections/{section_id}/comments")
async def get_comments(project_id: str, section_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    comments = await document_service.list_comments(db, project_id, section_id)
    return ok([comment.model_dump() for comment in comments])


@router.patch("/{project_id}/comments/{comment_id}/resolve")
async def resolve_comment(
    project_id: str,
    comment_id: str,
    body: CommentResolve = CommentResolve(),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    comment = await document_service.resolve_comment(db, project_id, comment_id, body.status)
    if not comment:
        raise not_found("Comment")
    return ok(comment.model_dump())
