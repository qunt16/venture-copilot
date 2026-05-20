import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_plan import BusinessPlan
from app.models.finance_forecast import FinanceForecast
from app.models.framework_analysis import FrameworkAnalysis
from app.models.financial_assumption import FinancialAssumption
from app.models.project import Project
from app.models.project_review import ProjectReview
from app.models.research_report import ResearchReport
from app.models.team_member import TeamMember
from app.schemas.review import ProjectReviewRead
from app.services.export_service import list_exports
from app.validators.consistency_engine import score_project


async def create_review(db: AsyncSession, project: Project) -> ProjectReviewRead:
    context = await _review_context(db, project)
    score = score_project(context)
    review = ProjectReview(id=str(uuid.uuid4()), project_id=project.id, score=score)
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return _to_read(review)


async def get_latest_review(db: AsyncSession, project_id: str) -> Optional[ProjectReviewRead]:
    review = await _latest(db, ProjectReview, project_id)
    if not review:
        return None
    return _to_read(review)


async def latest_review_score(db: AsyncSession, project_id: str) -> dict | None:
    review = await _latest(db, ProjectReview, project_id)
    return review.score if review else None


async def _review_context(db: AsyncSession, project: Project) -> dict:
    forecast = await _latest(db, FinanceForecast, project.id)
    research = await _latest(db, ResearchReport, project.id)
    frameworks = await _latest(db, FrameworkAnalysis, project.id)
    business_plan = await _latest(db, BusinessPlan, project.id)
    assumptions = await _latest(db, FinancialAssumption, project.id)
    team_size = await _team_size(db, project.id)

    forecast_data = forecast.summary if forecast else {}
    bp_content = _normalize_business_plan(business_plan.sections if business_plan else {})
    bp_text = "\n".join(section.get("content", "") for section in bp_content["sections"])
    research_text = _research_text(research)
    frameworks_data = frameworks.frameworks if frameworks else {}

    return {
        "project_title": project.title,
        "idea_summary": project.idea_summary or "",
        "team_size": team_size,
        "forecast_inputs": forecast.inputs if forecast else {},
        "financial_assumptions": assumptions.assumptions if assumptions else {},
        "financial_assumptions_confirmed": bool(assumptions and assumptions.confirmed),
        "financial_assumption_warnings": assumptions.warnings if assumptions else [],
        "forecast_summary": forecast_data.get("summary", forecast_data),
        "financing_needs": forecast_data.get("financing_needs", {}),
        "market_size": research.market_size if research else "",
        "citations": research.citations if research else [],
        "language": bp_content["language"],
        "template_type": bp_content["template_type"],
        "selected_sections": bp_content["selected_sections"],
        "business_plan_sections": bp_content["sections"],
        "business_plan_text": bp_text,
        "frameworks": frameworks_data,
        "exports": [item.model_dump() for item in list_exports(project.id)],
        "combined_text": "\n".join([project.title, project.idea_summary or "", bp_text, research_text, str(frameworks_data)]),
    }


async def _latest(db: AsyncSession, model, project_id: str):
    result = await db.execute(
        select(model)
        .where(model.project_id == project_id)
        .order_by(model.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _team_size(db: AsyncSession, project_id: str) -> int:
    result = await db.execute(select(func.count()).select_from(TeamMember).where(TeamMember.project_id == project_id))
    return int(result.scalar() or 0)


def _normalize_business_plan(content: dict | None) -> dict:
    content = content or {}
    if isinstance(content.get("sections"), list):
        return {
            "language": content.get("language", "zh-CN"),
            "template_type": content.get("template_type", "generic_startup"),
            "selected_sections": content.get("selected_sections", []),
            "sections": content.get("sections", []),
        }
    sections = [
        {"key": key, "heading": key.replace("_", " ").title(), "content": value}
        for key, value in content.items()
    ]
    return {
        "language": "en-US",
        "template_type": "generic_startup",
        "selected_sections": [section["key"] for section in sections],
        "sections": sections,
    }


def _research_text(research: ResearchReport | None) -> str:
    if not research:
        return ""
    parts = [research.summary or "", research.market_size or ""]
    parts.extend(research.industry_trends or [])
    parts.extend(research.competitors or [])
    parts.extend(research.risks or [])
    parts.extend(research.opportunities or [])
    return "\n".join(parts)


def _to_read(review: ProjectReview) -> ProjectReviewRead:
    score = review.score or {}
    return ProjectReviewRead(
        id=review.id,
        project_id=review.project_id,
        overall_score=score.get("overall_score", 0),
        dimensions=score.get("dimensions", {}),
        warnings=score.get("warnings", []),
        critical_conflicts=score.get("critical_conflicts", []),
        suggestions=score.get("suggestions", []),
        deductions=score.get("deductions", []),
        created_at=review.created_at,
        updated_at=review.updated_at,
    )
