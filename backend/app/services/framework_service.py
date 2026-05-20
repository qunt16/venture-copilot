import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProviderError
from app.ai.provider_factory import get_provider
from app.frameworks.engine import generate_frameworks
from app.models.finance_forecast import FinanceForecast
from app.models.framework_analysis import FrameworkAnalysis
from app.models.project import Project
from app.models.research_report import ResearchReport
from app.schemas.framework import FrameworkAnalysisRead, FrameworkAnalysisRequest


async def create_analysis(
    db: AsyncSession,
    project: Project,
    request: FrameworkAnalysisRequest,
) -> FrameworkAnalysisRead:
    forecast = await _latest(db, FinanceForecast, project.id)
    research = await _latest(db, ResearchReport, project.id)
    if not forecast:
        raise ValueError("Finance forecast required before framework analysis")
    if not research:
        raise ValueError("Research report required before framework analysis")
    try:
        provider = get_provider(request.ai_config)
    except AIProviderError as exc:
        raise ValueError(str(exc)) from exc

    frameworks = generate_frameworks(project, forecast, research, request.language, request.frameworks)
    if provider.provider_name != "mock":
        try:
            generated = provider.generate_framework_context(
                {
                    "language": request.language,
                    "frameworks": request.frameworks or list(frameworks.keys()),
                    "project": {"title": project.title, "idea_summary": project.idea_summary},
                    "forecast_summary": (forecast.summary or {}).get("summary", forecast.summary or {}),
                    "research": {
                        "summary": research.summary,
                        "market_size": research.market_size,
                        "competitors": research.competitors or [],
                        "citations": research.citations or [],
                    },
                }
            )
        except AIProviderError as exc:
            raise ValueError(str(exc)) from exc
        if isinstance(generated.get("frameworks"), dict):
            frameworks = generated["frameworks"]
    analysis = FrameworkAnalysis(
        id=str(uuid.uuid4()),
        project_id=project.id,
        language=request.language,
        frameworks=frameworks,
    )
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    return FrameworkAnalysisRead.model_validate(analysis)


async def get_latest_analysis(db: AsyncSession, project_id: str) -> Optional[FrameworkAnalysisRead]:
    analysis = await _latest(db, FrameworkAnalysis, project_id)
    if not analysis:
        return None
    return FrameworkAnalysisRead.model_validate(analysis)


async def _latest(db: AsyncSession, model, project_id: str):
    result = await db.execute(
        select(model)
        .where(model.project_id == project_id)
        .order_by(model.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
