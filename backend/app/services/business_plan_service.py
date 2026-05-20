import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProviderError
from app.ai.provider_factory import get_provider
from app.models.business_plan import BusinessPlan
from app.models.finance_forecast import FinanceForecast
from app.models.framework_analysis import FrameworkAnalysis
from app.models.project import Project
from app.models.project_review import ProjectReview
from app.models.research_report import ResearchReport
from app.schemas.business_plan import BusinessPlanRead
from app.schemas.template import BusinessPlanTemplateRequest
from app.finance.narrative import build_financial_narrative
from app.services.language_service import normalize_to_language
from app.services import template_service
from app.services.document_service import sync_blocks_from_sections


async def create_business_plan(
    db: AsyncSession,
    project: Project,
    request: BusinessPlanTemplateRequest,
) -> BusinessPlanRead:
    forecast = await _get_latest_forecast(db, project.id)
    if not forecast:
        raise ValueError("Finance forecast required before business plan generation")

    try:
        provider = get_provider(request.ai_config)
    except AIProviderError as exc:
        raise ValueError(str(exc)) from exc
    selected_sections = template_service.resolve_selected_sections(
        request.template_type,
        request.sections,
    )
    if forecast and "financial_forecast" not in selected_sections:
        insert_at = selected_sections.index("funding_plan") if "funding_plan" in selected_sections else len(selected_sections)
        selected_sections = selected_sections[:insert_at] + ["financial_forecast"] + selected_sections[insert_at:]
    framework_analysis = await _get_latest_frameworks(db, project.id)
    research = await _get_latest_research(db, project.id)
    review = await _get_latest_review(db, project.id)
    content = template_service.build_business_plan_content(
        project=project,
        forecast=forecast,
        language=request.language,
        template_type=request.template_type,
        selected_sections=selected_sections,
        framework_analysis=framework_analysis,
        research=research,
        review=review,
        financial_narrative=build_financial_narrative(forecast),
    )
    if provider.provider_name != "mock":
        try:
            ai_sections = [
                section for section in content.get("sections", [])
                if section.get("key") not in {"financial_forecast", "references"}
            ]
            generated = provider.generate_business_plan_context(
                {
                    "project": {"title": project.title, "idea_summary": project.idea_summary},
                    "forecast_summary": (forecast.summary or {}).get("summary", forecast.summary or {}),
                    "research": _research_context(research),
                    "framework_analysis": framework_analysis or {},
                    "review": review.score if review else None,
                    "language": request.language,
                    "template_type": request.template_type,
                    "selected_sections": [section["key"] for section in ai_sections],
                    "sections": ai_sections,
                }
            )
        except AIProviderError as exc:
            raise ValueError(str(exc)) from exc
        _apply_generated_sections(content, generated)
    _normalize_content_language(content)
    plan = BusinessPlan(
        id=str(uuid.uuid4()),
        project_id=project.id,
        provider_used=provider.provider_name,
        sections=content,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    await sync_blocks_from_sections(db, project.id, content.get("sections", []))
    return _to_read(plan)


async def get_latest_business_plan(
    db: AsyncSession, project_id: str
) -> Optional[BusinessPlanRead]:
    result = await db.execute(
        select(BusinessPlan)
        .where(BusinessPlan.project_id == project_id)
        .order_by(BusinessPlan.created_at.desc())
        .limit(1)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return None
    return _to_read(plan)


async def _get_latest_forecast(
    db: AsyncSession, project_id: str
) -> Optional[FinanceForecast]:
    result = await db.execute(
        select(FinanceForecast)
        .where(FinanceForecast.project_id == project_id)
        .order_by(FinanceForecast.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_latest_frameworks(db: AsyncSession, project_id: str) -> dict | None:
    result = await db.execute(
        select(FrameworkAnalysis)
        .where(FrameworkAnalysis.project_id == project_id)
        .order_by(FrameworkAnalysis.created_at.desc())
        .limit(1)
    )
    analysis = result.scalar_one_or_none()
    return analysis.frameworks if analysis else None


async def _get_latest_research(db: AsyncSession, project_id: str) -> ResearchReport | None:
    result = await db.execute(
        select(ResearchReport)
        .where(ResearchReport.project_id == project_id)
        .order_by(ResearchReport.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_latest_review(db: AsyncSession, project_id: str) -> ProjectReview | None:
    result = await db.execute(
        select(ProjectReview)
        .where(ProjectReview.project_id == project_id)
        .order_by(ProjectReview.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _to_read(plan: BusinessPlan) -> BusinessPlanRead:
    content = plan.sections or {}
    if isinstance(content.get("sections"), list):
        return BusinessPlanRead(
            id=plan.id,
            project_id=plan.project_id,
            provider_used=plan.provider_used,
            language=content.get("language", "zh-CN"),
            template_type=content.get("template_type", "generic_startup"),
            selected_sections=content.get("selected_sections", []),
            sections=content.get("sections", []),
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    legacy_sections = [
        {"key": key, "heading": key.replace("_", " ").title(), "content": value}
        for key, value in content.items()
    ]
    return BusinessPlanRead(
        id=plan.id,
        project_id=plan.project_id,
        provider_used=plan.provider_used,
        language="en-US",
        template_type="generic_startup",
        selected_sections=[item["key"] for item in legacy_sections],
        sections=legacy_sections,
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


def _apply_generated_sections(content: dict, generated: dict) -> None:
    sections = generated.get("sections") or []
    by_key = {
        item.get("key"): item.get("content")
        for item in sections
        if isinstance(item, dict) and item.get("key") and item.get("content")
    }
    for section in content.get("sections", []):
        replacement = by_key.get(section.get("key"))
        if replacement:
            section["content"] = replacement


def _normalize_content_language(content: dict) -> None:
    language = content.get("language", "zh-CN")
    for section in content.get("sections", []):
        section["content"] = normalize_to_language(section.get("content"), language)


def _research_context(research: ResearchReport | None) -> dict:
    if not research:
        return {}
    return {
        "summary": research.summary,
        "market_size": research.market_size,
        "industry_trends": research.industry_trends or [],
        "competitors": research.competitors or [],
        "risks": research.risks or [],
        "opportunities": research.opportunities or [],
        "citations": research.citations or [],
    }
