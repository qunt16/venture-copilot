from app.templates.business_plan_templates import (
    SECTION_HEADINGS,
    SUPPORTED_SECTION_KEYS,
    TEMPLATE_PRESETS,
)


def resolve_selected_sections(template_type: str, sections: list[str] | None) -> list[str]:
    if template_type == "custom":
        if not sections:
            raise ValueError("Custom template requires sections")
        selected = sections
    elif sections:
        selected = sections
    else:
        selected = TEMPLATE_PRESETS[template_type]

    unsupported = [key for key in selected if key not in SUPPORTED_SECTION_KEYS]
    if unsupported:
        raise ValueError(f"Unsupported sections: {', '.join(unsupported)}")

    return selected


def heading_for(section_key: str, language: str) -> str:
    return SECTION_HEADINGS[section_key][language]


def build_business_plan_content(
    *,
    project,
    forecast,
    language: str,
    template_type: str,
    selected_sections: list[str],
    framework_analysis: dict | None = None,
    research=None,
    review=None,
    financial_narrative: dict | None = None,
) -> dict:
    forecast_data = forecast.summary or {}
    summary = forecast_data.get("summary", forecast_data)
    context = {
        "title": project.title,
        "idea": project.idea_summary or "",
        "breakeven": summary.get("breakeven_month"),
        "funding_needed": summary.get("funding_needed", 0),
        "total_revenue": summary.get("total_revenue", 0),
        "ending_cash": summary.get("ending_cash", 0),
        "total_net_profit": summary.get("total_net_profit", 0),
        "framework_analysis": framework_analysis or {},
        "research": _research_context(research),
        "review": review.score if review else None,
        "financial_narrative": financial_narrative or {},
    }

    sections = [
        {
            "key": key,
            "heading": heading_for(key, language),
            "content": _section_content(key, language, context),
        }
        for key in selected_sections
    ]

    return {
        "language": language,
        "template_type": template_type,
        "selected_sections": selected_sections,
        "sections": sections,
    }


def _section_content(key: str, language: str, context: dict) -> str:
    if language == "zh-CN":
        return _zh_content(key, context)
    return _en_content(key, context)


def _zh_content(key: str, context: dict) -> str:
    title = context["title"]
    idea = context["idea"] or "围绕高校创业团队需求开展的项目。"
    breakeven = context["breakeven"] or "暂未达到"
    funding_needed = context["funding_needed"]
    total_revenue = context["total_revenue"]
    ending_cash = context["ending_cash"]
    total_net_profit = context["total_net_profit"]

    content = {
        "project_overview": f"{title} 面向中国高校创新创业竞赛场景，聚焦“{idea}”。项目以清晰的用户需求、可验证的商业闭环和可落地的执行计划作为核心。",
        "team_intro": "团队建议突出专业互补、校园资源、产品执行、市场调研与财务建模能力，并明确负责人分工和阶段性里程碑。",
        "pain_point_analysis": f"目标用户在创业项目梳理、商业计划书表达和财务测算方面存在效率低、结构不统一、验证不足等痛点，{title} 通过标准化流程降低参赛准备成本。",
        "product_service": f"{title} 提供从项目创建、财务预测、商业计划生成、研究引用到导出的完整后端能力，帮助团队快速形成可提交的创业计划材料。",
        "technology_innovation": "项目创新点在于将模板化计划书结构、结构化数据和引用型研究内容组合为可复用流程，优先服务挑战杯/互联网+等竞赛材料生产。",
        "market_analysis": "初期市场可聚焦高校创业团队、创新创业课程、学生社团和孵化器项目，后续扩展到高校双创中心和早期创业辅导机构。",
        "competitor_analysis": _competitor_text(context),
        "business_model": "商业模式可从校园团队订阅、赛事训练营工具包、双创课程配套服务切入，后续根据团队使用频次和组织采购意愿优化定价。",
        "marketing_strategy": "营销应优先覆盖高校双创社群、竞赛训练营、导师工作坊和学生组织，通过示例模板、案例演示和试点班级建立口碑。",
        "operation_plan": "运营计划以小规模试点、反馈迭代、模板沉淀和竞赛周期运营为主，围绕报名、初赛、复赛、决赛阶段提供不同深度材料支持。",
        "financial_forecast": context["financial_narrative"].get("content") or f"当前预测显示总收入约 {total_revenue:,.2f}，净利润约 {total_net_profit:,.2f}，预计盈亏平衡月份为 {breakeven}，期末现金约 {ending_cash:,.2f}。",
        "funding_plan": f"当前测算的资金缺口为 {funding_needed:,.2f}。若进入实际运营，可优先申请校内孵化基金、赛事奖金和小额天使资金。",
        "risk_analysis": "主要风险包括需求验证不足、竞赛格式差异、用户付费意愿不稳定、模板内容同质化以及导出材料质量预期提升。",
        "social_value": "项目有助于降低高校学生创新创业门槛，提升商业计划书质量，促进学生将创意转化为可验证、可展示、可迭代的创业方案。",
        "development_plan": "发展规划可分为模板完善、校园试点、赛事场景深化、组织级服务和多语言/多行业扩展五个阶段。",
        "appendix": "附录可包含财务假设、访谈摘要、功能清单、团队分工、竞赛材料版本记录和补充说明。",
        "references": _references_text(context),
        "swot_analysis": _format_framework(context["framework_analysis"].get("swot"), "暂无 SWOT 分析，请先运行框架分析。"),
        "pest_analysis": _format_framework(context["framework_analysis"].get("pest"), "暂无 PEST 分析，请先运行框架分析。"),
        "porter_five_forces": _format_framework(context["framework_analysis"].get("porter_five_forces"), "暂无波特五力分析，请先运行框架分析。"),
        "business_model_canvas": _format_framework(context["framework_analysis"].get("business_model_canvas"), "暂无商业模式画布，请先运行框架分析。"),
        "tam_sam_som": _format_framework(context["framework_analysis"].get("tam_sam_som"), _tam_text(context)),
        "risk_matrix": _format_framework(context["framework_analysis"].get("risk_matrix"), "暂无风险矩阵，请先运行框架分析。"),
        "competitor_matrix": _format_framework(context["framework_analysis"].get("competitor_matrix"), "暂无竞品矩阵，请先运行框架分析。"),
        "growth_strategy": _format_framework(context["framework_analysis"].get("growth_strategy"), "暂无增长策略，请先运行框架分析。"),
        "funding_suggestion": _format_framework(context["framework_analysis"].get("funding_suggestion"), "暂无融资建议，请先运行框架分析。"),
    }
    return content[key]


def _en_content(key: str, context: dict) -> str:
    title = context["title"]
    idea = context["idea"] or "a startup project for university teams"
    breakeven = context["breakeven"] or "not reached"
    funding_needed = context["funding_needed"]
    total_revenue = context["total_revenue"]
    ending_cash = context["ending_cash"]
    total_net_profit = context["total_net_profit"]

    content = {
        "project_overview": f"{title} is built around {idea}, with a clear project scope, practical execution plan, and competition-ready business narrative.",
        "team_intro": "The team should highlight complementary skills across product, research, finance, operations, and university entrepreneurship resources.",
        "pain_point_analysis": "Target users need a faster way to structure ideas, validate assumptions, and prepare consistent competition materials.",
        "product_service": f"{title} provides project setup, financial forecasting, business plan generation, mock research, citations, and export-ready documents.",
        "technology_innovation": "The innovation is a repeatable backend flow that combines finance-first planning, configurable templates, and structured export.",
        "market_analysis": "The initial market is university startup teams, entrepreneurship courses, student societies, and campus incubators.",
        "competitor_analysis": "Alternatives include generic templates, manual spreadsheets, advisor sessions, and broad business planning tools.",
        "business_model": "The business model can start with team subscriptions, course packages, and campus entrepreneurship program partnerships.",
        "marketing_strategy": "Marketing should focus on entrepreneurship centers, student founder communities, mentor workshops, and competition preparation cohorts.",
        "operation_plan": "Operations should begin with pilots, feedback loops, template refinement, and competition-cycle support.",
        "financial_forecast": f"The forecast projects total revenue of {total_revenue:,.2f}, net profit of {total_net_profit:,.2f}, breakeven month {breakeven}, and ending cash of {ending_cash:,.2f}.",
        "funding_plan": f"Estimated funding need is {funding_needed:,.2f}. Early funding can come from university grants, competition awards, or small angel checks.",
        "risk_analysis": "Key risks include weak demand validation, template commoditization, format differences across competitions, and uncertain willingness to pay.",
        "social_value": "The project lowers the barrier for student entrepreneurship and helps teams turn ideas into structured, testable venture plans.",
        "development_plan": "The roadmap moves from template refinement to campus pilots, competition specialization, institution-level services, and broader category expansion.",
        "appendix": "The appendix can include assumptions, team roles, feature lists, financial details, and version history.",
        "references": "References should use the mock research citations now and be replaced with live verified citations in a later research iteration.",
        "swot_analysis": _format_framework(context["framework_analysis"].get("swot"), "No SWOT analysis available. Run framework analysis first."),
        "pest_analysis": _format_framework(context["framework_analysis"].get("pest"), "No PEST analysis available. Run framework analysis first."),
        "porter_five_forces": _format_framework(context["framework_analysis"].get("porter_five_forces"), "No Porter analysis available. Run framework analysis first."),
        "business_model_canvas": _format_framework(context["framework_analysis"].get("business_model_canvas"), "No business model canvas available. Run framework analysis first."),
        "tam_sam_som": _format_framework(context["framework_analysis"].get("tam_sam_som"), "No TAM SAM SOM available. Run framework analysis first."),
        "risk_matrix": _format_framework(context["framework_analysis"].get("risk_matrix"), "No risk matrix available. Run framework analysis first."),
        "competitor_matrix": _format_framework(context["framework_analysis"].get("competitor_matrix"), "No competitor matrix available. Run framework analysis first."),
        "growth_strategy": _format_framework(context["framework_analysis"].get("growth_strategy"), "No growth strategy available. Run framework analysis first."),
        "funding_suggestion": _format_framework(context["framework_analysis"].get("funding_suggestion"), "No funding suggestion available. Run framework analysis first."),
    }
    return content[key]


def _format_framework(data, fallback: str) -> str:
    if not data:
        return fallback
    if isinstance(data, dict):
        parts = []
        for key, value in data.items():
            if isinstance(value, list):
                parts.append(f"{key}：" + "；".join(str(item) for item in value))
            else:
                parts.append(f"{key}：{value}")
        return "\n".join(parts)
    return str(data)


def _research_context(research) -> dict:
    if not research:
        return {}
    return {
        "summary": research.summary or "",
        "market_size": research.market_size or "",
        "industry_trends": research.industry_trends or [],
        "competitors": research.competitors or [],
        "risks": research.risks or [],
        "opportunities": research.opportunities or [],
        "citations": research.citations or [],
    }


def _tam_text(context: dict) -> str:
    research = context.get("research") or {}
    market_size = research.get("market_size")
    if market_size:
        return f"基于现有 Exa 研究，市场容量测算应从 TAM、SAM、SOM 三层展开。当前可引用的市场信息为：{market_size} 后续需要将高校数量、目标学生规模、试点校区渗透率和付费转化率进一步量化。"
    return "市场容量测算应分为 TAM、SAM、SOM：TAM 对应全部高校创新创业与相关场景，SAM 对应可服务高校团队和双创课程，SOM 对应首批可触达试点学校和参赛团队。"


def _competitor_text(context: dict) -> str:
    competitors = (context.get("research") or {}).get("competitors") or []
    base = "主要替代方案包括通用文档模板、人工导师辅导、电子表格和通用商业计划工具。本项目优势是围绕高校竞赛格式和中文材料输出进行定制。"
    if competitors:
        return base + " Exa 研究中可参考的竞品或替代方案包括：" + "；".join(str(item) for item in competitors[:5]) + "。"
    return base


def _references_text(context: dict) -> str:
    citations = (context.get("research") or {}).get("citations") or []
    if not citations:
        return "参考资料将在生成真实研究报告后补充。"
    lines = ["以下引用来自最新研究报告，标题和 URL 保持来源原文："]
    for index, item in enumerate(citations[:12], start=1):
        lines.append(f"[{index}] {item.get('title')} — {item.get('source')}: {item.get('url')}")
    return "\n".join(lines)
