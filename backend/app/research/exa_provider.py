from exa_py import Exa

from app.research.base import BaseResearchProvider, ResearchProviderError


class ExaResearchProvider(BaseResearchProvider):
    provider_name = "exa"

    def generate_report(self, project) -> dict:
        self.validate_ready()
        idea = project.idea_summary or project.title
        per_query = max(1, min(self.config.num_results, 12) // 3)
        market_results = self._search(f"{project.title} {idea} 市场规模 行业趋势 政策 高校 创业", per_query)
        company_results = self._search(f"{project.title} 竞品 公司 替代方案 定价", per_query, category="company")
        news_results = self._search(f"{project.title} {idea} 最新 新闻 市场 报告", per_query, category="news")
        all_results = market_results + company_results + news_results
        if not all_results:
            raise ResearchProviderError("Exa returned no research results")

        citations = [_citation(item) for item in all_results[:8]]
        competitors = _competitors(company_results) or _competitors(all_results)
        highlights = _highlights(all_results)
        return {
            "provider_used": self.provider_name,
            "summary": f"{project.title} 的 Exa 实时研究共返回 {len(all_results)} 条网页结果，覆盖市场、竞品和新闻/报告来源。以下结论仅基于 Exa 返回的公开网页标题、摘要和高亮信息。",
            "market_size": _sentence(market_results, "市场规模与行业背景需要结合以下来源继续量化"),
            "industry_trends": highlights[:5] or ["Exa 返回了相关来源，但未提供可提取摘要。"],
            "competitors": competitors[:6] or ["未从 Exa 结果中稳定提取竞品名称"],
            "risks": [
                "实时搜索结果需要人工复核来源权威性和发布时间。",
                "竞品名称来自网页标题/摘要抽取，可能包含媒体或机构名称。",
                "市场规模结论需要结合官方统计或行业报告进一步校验。",
            ],
            "opportunities": [
                "优先使用 Exa 返回的公司、新闻和机构来源补强竞赛计划书引用。",
                "将竞品结果输入 competitor_matrix 生成定位和市场空白分析。",
                "围绕政策和高校场景来源增强项目的社会价值论证。",
            ],
            "citations": citations,
        }

    def _search(self, query: str, num_results: int, category: str | None = None) -> list[dict]:
        try:
            client = Exa(api_key=self.config.api_key.get_secret_value())
            kwargs = {
                "type": self.config.type,
                "num_results": num_results,
                "highlights": True,
                "summary": True,
            }
            if category:
                kwargs["category"] = category
            data = client.search_and_contents(query, **kwargs)
        except Exception as exc:
            raise ResearchProviderError(f"Exa provider failed: status=sdk_error body={_safe_body(str(exc))}") from exc
        return [_result_to_dict(item) for item in getattr(data, "results", [])]


def _result_to_dict(item) -> dict:
    if isinstance(item, dict):
        return item
    return {
        "title": getattr(item, "title", None),
        "url": getattr(item, "url", None),
        "summary": getattr(item, "summary", None),
        "highlights": getattr(item, "highlights", None),
    }


def _citation(item: dict) -> dict:
    return {
        "title": item.get("title") or item.get("url") or "Untitled Exa result",
        "source": _host(item.get("url", "")) or "Exa",
        "url": item.get("url") or "",
        "source_type": _source_type(item.get("url", ""), item.get("title", "")),
        "snippet": _snippet(item),
    }


def _highlights(results: list[dict]) -> list[str]:
    output = []
    for item in results:
        summary = item.get("summary")
        if summary:
            output.append(str(summary)[:300])
            continue
        highlights = item.get("highlights") or []
        if highlights:
            output.append(str(highlights[0])[:300])
    return output


def _snippet(item: dict) -> str:
    summary = item.get("summary")
    if summary:
        return str(summary)[:500]
    highlights = item.get("highlights") or []
    if highlights:
        return str(highlights[0])[:500]
    return ""


def _competitors(results: list[dict]) -> list[str]:
    names = []
    for item in results:
        title = item.get("title") or ""
        candidate = title.split("|")[0].split("-")[0].strip()
        if candidate and candidate not in names:
            names.append(candidate[:80])
    return names


def _sentence(results: list[dict], fallback: str) -> str:
    highlights = _highlights(results)
    if not highlights:
        return fallback
    return "；".join(highlights[:2])


def _host(url: str) -> str:
    return url.split("//")[-1].split("/")[0] if url else ""


def _source_type(url: str, title: str) -> str:
    lower = f"{url} {title}".lower()
    if ".gov" in lower or "government" in lower:
        return "government"
    if any(token in lower for token in ["report", "pdf", "research", "data"]):
        return "report"
    if any(token in lower for token in ["news", "36kr", "techcrunch", "reuters"]):
        return "news"
    if any(token in lower for token in ["company", "about", "pricing"]):
        return "company"
    return "institution"


def _safe_body(text: str) -> str:
    compact = " ".join((text or "").split())
    return compact[:500]
