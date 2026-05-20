from app.competitors.engine import analyze_competitors


DEFAULT_FRAMEWORKS = ["swot", "pest", "porter_five_forces", "business_model_canvas"]
SUPPORTED_FRAMEWORKS = {
    "swot",
    "pest",
    "porter_five_forces",
    "business_model_canvas",
    "tam_sam_som",
    "stp",
    "marketing_4p",
    "value_chain",
    "risk_matrix",
    "competitor_matrix",
    "growth_strategy",
    "funding_suggestion",
}


def generate_frameworks(project, forecast, research, language: str, selected: list[str] | None) -> dict:
    framework_keys = selected or DEFAULT_FRAMEWORKS
    unsupported = [key for key in framework_keys if key not in SUPPORTED_FRAMEWORKS]
    if unsupported:
        raise ValueError(f"Unsupported frameworks: {', '.join(unsupported)}")

    context = _context(project, forecast, research)
    return {key: _generate_one(key, language, context) for key in framework_keys}


def _context(project, forecast, research) -> dict:
    forecast_data = forecast.summary or {}
    summary = forecast_data.get("summary", forecast_data)
    return {
        "title": project.title,
        "idea": project.idea_summary or "高校创新创业项目",
        "total_revenue": summary.get("total_revenue", 0),
        "ending_cash": summary.get("ending_cash", 0),
        "funding_needed": summary.get("funding_needed", 0),
        "breakeven_month": summary.get("breakeven_month"),
        "market_size": getattr(research, "market_size", "") or "",
        "competitors": getattr(research, "competitors", []) or [],
        "risks": getattr(research, "risks", []) or [],
    }


def _generate_one(key: str, language: str, c: dict) -> dict:
    if language == "zh-CN":
        return _zh(key, c)
    return _en(key, c)


def _zh(key: str, c: dict) -> dict:
    title = c["title"]
    if key == "swot":
        return {
            "优势": [f"{title} 聚焦高校竞赛场景，定位清晰。", "具备财务预测、研究引用和导出的一体化流程。"],
            "劣势": ["当前仍依赖模拟研究内容，真实数据验证不足。", "品牌和渠道仍处于早期阶段。"],
            "机会": ["高校双创赛事参与度高，计划书生成需求集中。", "可与课程、社团和孵化器形成试点合作。"],
            "威胁": ["通用模板和人工辅导可替代部分功能。", "不同赛事格式变化可能增加模板维护成本。"],
        }
    if key == "pest":
        return {
            "政治": "高校创新创业教育和双创赛事持续获得政策支持。",
            "经济": "学生团队预算有限，因此工具需要证明明确的效率提升和材料质量提升。",
            "社会": "学生创业团队更重视低门槛、可协作、可快速产出的工具。",
            "技术": "结构化模板、自动财务测算和文档导出降低了计划书生产成本。",
        }
    if key == "porter_five_forces":
        return {
            "现有竞争者": "通用文档模板、导师辅导和商业计划工具竞争强度中等。",
            "潜在进入者": "模板类工具进入门槛较低，但深度适配竞赛格式需要积累。",
            "替代品": "人工撰写、电子表格和免费模板是主要替代品。",
            "供应商议价能力": "核心依赖为软件能力和内容模板，供应商议价能力较低。",
            "买方议价能力": "学生团队价格敏感，学校组织采购则更看重稳定性和服务。",
        }
    if key == "business_model_canvas":
        return {
            "客户细分": "高校创业团队、双创课程学生、学生社团和孵化器项目。",
            "价值主张": "快速生成符合竞赛表达习惯的财务优先型创业计划书。",
            "渠道通路": "双创中心、赛事训练营、课程合作和学生社群。",
            "客户关系": "模板自助生成结合导师式材料检查。",
            "收入来源": "团队订阅、课程包、训练营工具包和组织级授权。",
            "关键资源": "模板库、财务引擎、研究引用结构和导出能力。",
            "关键活动": "模板迭代、试点运营、赛事周期支持和用户反馈分析。",
            "关键合作": "高校双创中心、导师、学生组织和孵化器。",
            "成本结构": "产品开发、模板维护、运营支持和校园推广。",
        }
    if key == "tam_sam_som":
        return {"TAM": "全国高校创新创业训练和竞赛参与人群。", "SAM": "重点高校双创课程、赛事团队和孵化器项目。", "SOM": "首批试点学校和训练营中可转化的学生团队。"}
    if key == "stp":
        return {"细分": "按赛事类型、项目阶段和团队能力细分。", "目标": "优先服务准备挑战杯/互联网+材料的早期团队。", "定位": "中文竞赛场景下的财务优先创业计划书助手。"}
    if key == "marketing_4p":
        return {"产品": "模板化计划书与财务测算后端服务。", "价格": "低门槛团队订阅或课程包。", "渠道": "高校社群、课程、双创中心。", "推广": "案例演示、训练营和导师推荐。"}
    if key == "value_chain":
        return {"输入": "项目创意、财务假设、研究引用。", "处理": "模板生成、框架分析、导出整合。", "输出": "可提交的 PDF/DOCX 创业计划材料。", "支持活动": "模板维护、数据校验和用户反馈。"}
    if key == "risk_matrix":
        return {"高概率/高影响": "需求验证不足。", "高概率/低影响": "模板表述需要反复调整。", "低概率/高影响": "竞赛规则大幅变化。", "应对策略": "持续访谈、模板版本化、保留 custom 模式。"}
    if key == "competitor_matrix":
        return analyze_competitors(title, c.get("competitors", []), "zh-CN")
    if key == "growth_strategy":
        return {
            "阶段": "先校内试点，再课程/训练营合作，最后扩展到组织级授权。",
            "优先渠道": ["双创中心", "创业课程", "学生社团", "赛事训练营"],
            "核心指标": ["激活率", "导出完成率", "复用率", "推荐率"],
        }
    if key == "funding_suggestion":
        return {
            "建议": "优先使用校内孵化基金、赛事奖金和小额天使资金覆盖试点期成本。",
            "金额参考": f"当前资金缺口为 {c['funding_needed']:,.2f}，建议至少覆盖 3 个月固定成本缓冲。",
            "投资人视角": "重点证明高频使用、材料质量提升和校内可复制获客路径。",
        }
    return {"分析": "暂未生成该框架内容。"}


def _en(key: str, c: dict) -> dict:
    title = c["title"]
    if key == "swot":
        return {"strengths": [f"{title} has a focused university competition positioning."], "weaknesses": ["Research is still mock-based."], "opportunities": ["Campus entrepreneurship programs create repeatable demand."], "threats": ["Generic templates and manual coaching can substitute part of the workflow."]}
    if key == "pest":
        return {"political": "University entrepreneurship remains policy-supported.", "economic": "Student teams are price-sensitive.", "social": "Teams need low-friction planning tools.", "technology": "Template automation and export reduce planning cost."}
    if key == "porter_five_forces":
        return {"rivalry": "Moderate", "new_entrants": "Moderate", "substitutes": "High", "supplier_power": "Low", "buyer_power": "High"}
    if key == "business_model_canvas":
        return {"customer_segments": "University startup teams", "value_proposition": "Competition-ready finance-first business plans", "channels": "Courses and incubators", "revenue_streams": "Subscriptions and program packages"}
    if key == "competitor_matrix":
        return analyze_competitors(title, c.get("competitors", []), "en-US")
    if key == "growth_strategy":
        return {"phase": "Pilot on campus, partner with courses, then expand to institution packages.", "channels": ["incubators", "courses", "student clubs"], "metrics": ["activation", "export completion", "reuse", "referrals"]}
    if key == "funding_suggestion":
        return {"recommendation": "Use grants, competition awards, and small angel checks to fund the pilot.", "investor_view": "Prove repeated use and scalable campus acquisition."}
    return {"analysis": f"{key} analysis for {title}."}
