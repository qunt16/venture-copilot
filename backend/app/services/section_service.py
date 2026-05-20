from app.ai.base import AIConfig, AIProviderError
from app.ai.provider_factory import get_provider
from app.schemas.section import SectionPolishRequest, SectionPolishResult
from app.services.language_service import detect_language_mixing, normalize_to_language


MODE_INSTRUCTIONS = {
    "polish": "润色表达，使语言更正式、清晰、适合创业计划书。",
    "expand": "在不虚构数据的前提下适度扩写，补充逻辑衔接和论证层次。",
    "shorten": "压缩为更精炼的版本，保留关键信息。",
    "challenge_cup_style": "改写为挑战杯风格，突出创新性、社会价值、实践过程和可落地性。",
    "internet_plus_style": "改写为互联网+风格，突出商业模式、市场空间、增长路径和运营闭环。",
    "fix_language_mixing": "清洗中英混杂内容，正文改为中文，仅保留必要的英文缩写、公司名、产品名、URL 和引用标题。",
}


def polish_section(request: SectionPolishRequest) -> SectionPolishResult:
    warnings = detect_language_mixing(request.text, request.language)
    try:
        provider = get_provider(AIConfig(provider="openrouter", model="deepseek/deepseek-chat", fallback_to_mock=False))
    except AIProviderError as exc:
        cleaned = normalize_to_language(request.text, request.language)
        warnings.append(str(exc))
        return SectionPolishResult(
            section_key=request.section_key,
            mode=request.mode,
            original_text=request.text,
            revised_text=cleaned,
            warnings=warnings,
        )

    if not hasattr(provider, "chat"):
        revised = normalize_to_language(request.text, request.language)
        return SectionPolishResult(
            section_key=request.section_key,
            mode=request.mode,
            original_text=request.text,
            revised_text=revised,
            warnings=warnings,
        )

    system = "你是中国高校创新创业竞赛商业计划书编辑。只返回改写后的正文，不要 Markdown，不要解释。"
    user = (
        f"语言：{request.language}\n"
        f"章节：{request.section_key}\n"
        f"任务：{MODE_INSTRUCTIONS[request.mode]}\n"
        "规则：保持原意；不编造财务或市场数据；保留原有引用标记；中文正文不得出现英文段落。\n"
        f"原文：\n{request.text}"
    )
    try:
        revised = provider.chat(system, user)
    except AIProviderError as exc:
        warnings.append(str(exc))
        revised = normalize_to_language(request.text, request.language)
    revised = normalize_to_language(revised, request.language)
    warnings.extend(detect_language_mixing(revised, request.language))
    return SectionPolishResult(
        section_key=request.section_key,
        mode=request.mode,
        original_text=request.text,
        revised_text=revised,
        warnings=warnings,
    )
