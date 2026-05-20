from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import not_found
from app.core.responses import ok
from app.services import project_service, review_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/review", status_code=201)
async def create_project_review(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    review = await review_service.create_review(db, project)
    return ok(review.model_dump())


@router.get("/{project_id}/review")
async def get_project_review(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    review = await review_service.get_latest_review(db, project_id)
    if not review:
        raise not_found("Project review")
    return ok(review.model_dump())
