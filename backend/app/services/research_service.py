import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIConfig, AIProviderError
from app.ai.provider_factory import get_provider
from app.models.project import Project
from app.models.research_report import ResearchReport
from app.research.base import ResearchConfig, ResearchProviderError
from app.research.provider_factory import get_research_provider
from app.schemas.research import ResearchReportRead
from app.services.language_service import normalize_research_payload


async def create_research_report(
    db: AsyncSession,
    project: Project,
    ai_config: AIConfig | None = None,
    research_config: ResearchConfig | None = None,
) -> ResearchReportRead:
    try:
        ai_provider = get_provider(ai_config)
    except AIProviderError as exc:
        raise ValueError(str(exc)) from exc
    try:
        research_provider = get_research_provider(research_config)
    except ResearchProviderError as exc:
        raise ValueError(str(exc)) from exc
    try:
        data = research_provider.generate_report(project)
        if ai_provider.provider_name != "mock" and research_provider.provider_name == "mock_research":
            ai_data = ai_provider.generate_research_context(
                {"project": {"title": project.title, "idea_summary": project.idea_summary}}
            )
            data.update(_normalize_ai_research(ai_data))
            data["provider_used"] = ai_provider.provider_name
        data = normalize_research_payload(data, "zh-CN")
    except (AIProviderError, ResearchProviderError) as exc:
        raise ValueError(str(exc)) from exc
    report = ResearchReport(
        id=str(uuid.uuid4()),
        project_id=project.id,
        provider_used=data["provider_used"],
        summary=data["summary"],
        market_size=data["market_size"],
        industry_trends=data["industry_trends"],
        competitors=data["competitors"],
        risks=data["risks"],
        opportunities=data["opportunities"],
        citations=data["citations"],
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return _to_read(report)


async def get_latest_research_report(
    db: AsyncSession, project_id: str
) -> Optional[ResearchReportRead]:
    result = await db.execute(
        select(ResearchReport)
        .where(ResearchReport.project_id == project_id)
        .order_by(ResearchReport.created_at.desc())
        .limit(1)
    )
    report = result.scalar_one_or_none()
    if not report:
        return None
    return _to_read(report)


def _to_read(report: ResearchReport) -> ResearchReportRead:
    return ResearchReportRead(
        id=report.id,
        project_id=report.project_id,
        provider_used=report.provider_used or "mock_research",
        summary=report.summary or "",
        market_size=report.market_size or "",
        industry_trends=report.industry_trends or [],
        competitors=report.competitors or [],
        risks=report.risks or [],
        opportunities=report.opportunities or [],
        citations=report.citations or [],
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


def _normalize_ai_research(data: dict) -> dict:
    return {
        "summary": str(data.get("summary") or ""),
        "market_size": str(data.get("market_size") or ""),
        "industry_trends": _list(data.get("industry_trends")),
        "competitors": _list(data.get("competitors")),
        "risks": _list(data.get("risks")),
        "opportunities": _list(data.get("opportunities")),
        "citations": data.get("citations") if isinstance(data.get("citations"), list) else [],
    }


def _list(value) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []
