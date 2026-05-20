from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.errors import not_found
from app.core.responses import ok
from app.schemas.section import SectionPolishRequest
from app.services import project_service, section_service

router = APIRouter()

USER_ID = "demo_user"


@router.post("/{project_id}/sections/polish")
async def polish_section(
    project_id: str,
    body: SectionPolishRequest,
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, project_id, USER_ID)
    if not project:
        raise not_found("Project")

    result = section_service.polish_section(body)
    return ok(result.model_dump())
