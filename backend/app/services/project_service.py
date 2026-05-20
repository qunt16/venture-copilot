import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate


async def create_project(db: AsyncSession, data: ProjectCreate, user_id: str) -> Project:
    project = Project(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=data.title,
        idea_summary=data.idea_summary,
        stage=data.stage or "idea",
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession, user_id: str) -> list[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: str, user_id: str) -> Optional[Project]:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()