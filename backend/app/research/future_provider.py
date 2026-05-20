from app.research.base import BaseResearchProvider, ResearchProviderError


class TavilyResearchProvider(BaseResearchProvider):
    provider_name = "tavily"

    def validate_ready(self) -> None:
        raise ResearchProviderError("Tavily research provider is reserved for future use")


class SerpApiResearchProvider(BaseResearchProvider):
    provider_name = "serpapi"

    def validate_ready(self) -> None:
        raise ResearchProviderError("SerpApi research provider is reserved for future use")
