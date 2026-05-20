from app.research.base import BaseResearchProvider, ResearchConfig


class MockResearchProvider(BaseResearchProvider):
    provider_name = "mock_research"

    def __init__(self, config: ResearchConfig | None = None) -> None:
        super().__init__(config)

    def validate_ready(self) -> None:
        return None

    def generate_report(self, project) -> dict:
        title = project.title
        idea = project.idea_summary or "面向高校创业团队验证的创业项目。"

        return {
            "provider_used": self.provider_name,
            "summary": (
                f"{title} 的模拟研究摘要：本报告使用稳定的占位型公开来源引用，"
                "不代表实时联网检索或网页抓取结果。"
                f"项目创意为：{idea}"
            ),
            "market_size": (
                "早期市场规模测算应优先聚焦可触达的高校学生、创新创业课程、学生社团和校内孵化器，"
                "在验证留存和付费意愿后，再扩展到毕业生、青年创业者和高校合作伙伴场景。"
            ),
            "industry_trends": [
                "高校持续通过双创课程、赛事训练营和孵化器支持学生创新创业。",
                "面向学生的产品需要在较短周期内证明节省时间、降低成本或提升成果质量。",
                "轻量化数字工具适合先通过校园试点验证需求，再逐步扩大运营投入。",
            ],
            "competitors": [
                "手工电子表格和通用计划书模板",
                "高校孵化器导师辅导",
                "通用商业计划书工具",
                "早期创业财务测算工具",
            ],
            "risks": [
                "在完成充分访谈前，市场规模假设可能过宽。",
                "如果节省时间或提升材料质量的价值不明显，学生可能倾向免费替代方案。",
                "如果过早面向学校组织销售，决策周期可能较长。",
            ],
            "opportunities": [
                "与学生社团、双创中心和课程班级开展试点。",
                "以财务优先的计划书生成为切入点，再扩展到更完整的创业辅导流程。",
                "沉淀适合常见高校创业项目类型的可复用模板。",
            ],
            "citations": [
                {
                    "title": "World Bank Data",
                    "source": "World Bank",
                    "url": "https://data.worldbank.org/",
                    "source_type": "institution",
                },
                {
                    "title": "OECD Data",
                    "source": "OECD",
                    "url": "https://data.oecd.org/",
                    "source_type": "institution",
                },
                {
                    "title": "Business and Self-employed",
                    "source": "GOV.UK",
                    "url": "https://www.gov.uk/browse/business",
                    "source_type": "government",
                },
                {
                    "title": "Companies House",
                    "source": "UK Government",
                    "url": "https://www.gov.uk/government/organisations/companies-house",
                    "source_type": "government",
                },
                {
                    "title": "Statista",
                    "source": "Statista",
                    "url": "https://www.statista.com/",
                    "source_type": "report",
                },
            ],
        }
