import re


ALLOWED_ENGLISH_TERMS = {"DCF", "IRR", "NPV", "ROI", "API", "SaaS", "URL", "TAM", "SAM", "SOM"}
RAW_EXA_PREFIX_RE = re.compile(
    r"^\s*(summary\s*(for)?\s*:|key features\s*:|this page\s+(markets|describes|explains)|overview\s*:)\s*",
    re.IGNORECASE,
)
ENGLISH_PARAGRAPH_RE = re.compile(r"[A-Z][A-Za-z]{2,}(?:[\s,;:.()/-]+[A-Za-z]{2,}){8,}")


def normalize_to_language(text: str | None, language: str) -> str:
    value = str(text or "").strip()
    if language != "zh-CN" or not value:
        return value
    value = RAW_EXA_PREFIX_RE.sub("", value)
    value = value.replace("Summary:\n", "").replace("Summary:", "")
    value = value.replace("Key features:", "要点：").replace("This page markets", "该页面介绍")
    value = value.replace("Summary for:", "摘要：")
    lines = [_normalize_zh_line(line) for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def detect_language_mixing(text: str | None, language: str) -> list[str]:
    if language != "zh-CN":
        return []
    warnings = []
    value = str(text or "")
    if RAW_EXA_PREFIX_RE.search(value) or "Summary:" in value or "Key features:" in value:
        warnings.append("检测到未清洗的 Exa 英文摘要前缀。")
    for match in ENGLISH_PARAGRAPH_RE.findall(value):
        cleaned = _remove_allowed_terms(match)
        if len(cleaned.split()) >= 8:
            warnings.append("检测到英文正文段落污染。")
            break
    return warnings


def clean_research_snippets_for_bp(items: list[str] | None, language: str = "zh-CN") -> list[str]:
    return [normalize_to_language(item, language) for item in (items or []) if normalize_to_language(item, language)]


def normalize_research_payload(data: dict, language: str = "zh-CN") -> dict:
    if language != "zh-CN":
        return data
    normalized = dict(data)
    for key in ("summary", "market_size"):
        normalized[key] = normalize_to_language(normalized.get(key), language)
    for key in ("industry_trends", "competitors", "risks", "opportunities"):
        normalized[key] = clean_research_snippets_for_bp(normalized.get(key), language)
    citations = []
    for item in normalized.get("citations") or []:
        citation = dict(item)
        if citation.get("snippet"):
            citation["snippet"] = normalize_to_language(citation.get("snippet"), language)
        citations.append(citation)
    normalized["citations"] = citations
    return normalized


def _normalize_zh_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return ""
    stripped = RAW_EXA_PREFIX_RE.sub("", stripped)
    if _looks_like_english_paragraph(stripped):
        return "该来源显示：" + _english_to_zh_summary(stripped)
    return stripped


def _looks_like_english_paragraph(text: str) -> bool:
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        return False
    words = re.findall(r"[A-Za-z]{3,}", _remove_allowed_terms(text))
    return len(words) >= 8


def _remove_allowed_terms(text: str) -> str:
    value = text
    for term in ALLOWED_ENGLISH_TERMS:
        value = re.sub(rf"\b{re.escape(term)}\b", "", value)
    value = re.sub(r"https?://\S+", "", value)
    return value


def _english_to_zh_summary(text: str) -> str:
    lower = text.lower()
    topics = []
    if "recycling" in lower or "waste" in lower:
        topics.append("智能回收与垃圾分类")
    if "campus" in lower or "university" in lower:
        topics.append("高校校园场景")
    if "pricing" in lower or "cost" in lower:
        topics.append("成本与定价信息")
    if "company" in lower or "startup" in lower:
        topics.append("相关企业与替代方案")
    if not topics:
        topics.append("相关市场资料")
    return "、".join(topics) + "可作为市场分析和竞品判断的参考，具体结论需结合引用来源复核。"
