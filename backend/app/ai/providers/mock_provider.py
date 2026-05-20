from app.ai.base import AIConfig, BaseAIProvider


class MockProvider(BaseAIProvider):
    provider_name = "mock"

    def __init__(self, config: AIConfig | None = None) -> None:
        super().__init__(config)

    def validate_ready(self) -> None:
        return None

    def generate_business_plan_context(self, context: dict) -> dict:
        return {
            "provider_used": self.provider_name,
            "quality_note": "deterministic mock generation",
        }

    def generate_research_context(self, context: dict) -> dict:
        return {
            "provider_used": self.provider_name,
            "quality_note": "deterministic mock research",
        }

    def generate_framework_context(self, context: dict) -> dict:
        return {
            "provider_used": self.provider_name,
            "quality_note": "deterministic mock frameworks",
        }

    def generate_business_plan(self, project, forecast) -> dict[str, str]:
        summary = forecast.summary or {}
        assumptions = forecast.inputs or {}
        title = project.title
        idea = project.idea_summary or "A startup concept being shaped by the team."
        months = assumptions.get("months", len(forecast.monthly_rows or []))

        ending_cash = summary.get("ending_cash", 0)
        total_revenue = summary.get("total_revenue", 0)
        breakeven_month = summary.get("breakeven_month")
        funding_needed = summary.get("funding_needed", 0)

        breakeven_text = (
            f"break even around month {breakeven_month}"
            if breakeven_month
            else "not reach breakeven within the forecast period"
        )

        return {
            "executive_summary": (
                f"{title} is a finance-first startup plan for: {idea} "
                f"The current {months}-month forecast projects total revenue of {total_revenue:,.2f} "
                f"and ending cash of {ending_cash:,.2f}."
            ),
            "problem": (
                f"The target users face a practical gap that {title} can address with a focused, "
                "simple product that is easy for a university startup team to validate."
            ),
            "solution": (
                f"{title} should launch as a narrow MVP that proves the core user workflow, "
                "collects feedback quickly, and avoids unnecessary product scope."
            ),
            "market": (
                "The initial market should be defined around reachable university communities, "
                "student groups, and early adopters who can be interviewed and converted directly."
            ),
            "business_model": (
                "The business model should start with a simple paid plan or usage-based offer, "
                "then adjust pricing once retention and acquisition signals are clearer."
            ),
            "financial_overview": (
                f"The forecast expects {total_revenue:,.2f} in total revenue, "
                f"{summary.get('total_net_profit', 0):,.2f} in net profit, and is expected to "
                f"{breakeven_text}. Estimated funding need is {funding_needed:,.2f}."
            ),
            "risks": (
                "Key risks are weak demand validation, slow student adoption, underestimated support work, "
                "and cost assumptions drifting from the forecast."
            ),
            "roadmap": (
                "Roadmap: validate the problem, build the smallest useful MVP, run a pilot, "
                "measure willingness to pay, then expand only around proven usage."
            ),
        }
