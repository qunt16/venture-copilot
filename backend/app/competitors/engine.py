def analyze_competitors(project_title: str, competitors: list[str], language: str = "zh-CN") -> dict:
    items = competitors or _default_competitors(language)
    matrix = [_row(project_title, name, index, language) for index, name in enumerate(items[:5], start=1)]
    evidence_mode = bool(competitors)
    if language == "zh-CN":
        return {
            "competitor_matrix": matrix,
            "market_gap": [
                "基于研究报告中的竞品来源，现有方案多集中在单点能力，完整创业材料闭环仍有空间。" if evidence_mode else "多数替代方案只解决单点问题，缺少从财务测算到计划书导出的完整闭环。",
                "若 Exa 研究已返回公司/报告来源，应继续核验定价页、产品页和案例页，形成可引用竞品证据。",
                "学生团队预算有限，低成本、可解释、可快速修改的方案更容易试点。",
            ],
            "recommended_positioning": f"{project_title} 应定位为“面向高校创业竞赛的财务优先型计划书与研究助手”。",
            "evidence_basis": "latest_research_competitors" if evidence_mode else "deterministic_fallback",
        }
    return {
        "competitor_matrix": matrix,
        "market_gap": [
            "Most alternatives solve isolated tasks rather than the full finance-to-export workflow.",
            "Competition-specific document structure remains underserved.",
            "Student teams need low-cost, explainable, easy-to-edit outputs.",
        ],
        "recommended_positioning": f"{project_title} should position as a finance-first planning assistant for university startup competitions.",
        "evidence_basis": "latest_research_competitors" if evidence_mode else "deterministic_fallback",
    }


def _default_competitors(language: str) -> list[str]:
    if language == "zh-CN":
        return ["通用文档模板", "人工导师辅导", "电子表格财务模型", "通用商业计划工具"]
    return ["Generic templates", "Advisor coaching", "Spreadsheet finance models", "General business planning tools"]


def _row(project_title: str, name: str, index: int, language: str) -> dict:
    if language == "zh-CN":
        strengths = ["上手门槛低"] if index == 1 else ["已有用户认知"]
        weaknesses = ["缺少自动化和结构化评分"] if index == 1 else ["难以稳定输出可复用格式"]
        return {
            "competitor": name,
            "positioning": "单点替代方案",
            "pricing": "免费到低价，或按服务收费",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "differentiation": f"{project_title} 的差异点是把财务、研究、框架、评分和导出串成一条后端流程。",
        }
    return {
        "competitor": name,
        "positioning": "Point solution",
        "pricing": "Free, low-cost, or service-based",
        "strengths": ["Easy to start"],
        "weaknesses": ["Limited structured scoring and export workflow"],
        "differentiation": f"{project_title} combines finance, research, frameworks, scoring, and export in one backend workflow.",
    }
