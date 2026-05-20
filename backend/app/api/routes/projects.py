from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import not_found
from app.core.responses import ok
from app.schemas.project import ProjectCreate, ProjectListItem, ProjectRead
from app.services import project_service

router = APIRouter()

USER_ID = "demo_user"  # placeholder until real auth is added


@router.post("", status_code=201)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = await project_service.create_project(db, body, USER_ID)
    return ok(ProjectRead.model_validate(project))


@router.get("")
async def list_projects(db: AsyncSession = Depends(get_db)):
    projects = await project_service.list_projects(db, USER_ID)
    items = [ProjectListItem.model_validate(p) for p in projects]
    return ok([i.model_dump() for i in items])


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")
    return ok(ProjectRead.model_validate(project))
