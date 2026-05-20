from pydantic import SecretStr

from app.core.config import settings
from app.research.base import ResearchConfig, ResearchProviderError
from app.research.exa_provider import ExaResearchProvider
from app.research.future_provider import SerpApiResearchProvider, TavilyResearchProvider
from app.research.mock_research_provider import MockResearchProvider


PROVIDERS = {
    "mock": MockResearchProvider,
    "exa": ExaResearchProvider,
    "tavily": TavilyResearchProvider,
    "serpapi": SerpApiResearchProvider,
}


def get_research_provider(config: ResearchConfig | None):
    safe_config = config or ResearchConfig()
    if safe_config.provider == "exa" and not safe_config.api_key and settings.EXA_API_KEY:
        safe_config = safe_config.model_copy(update={"api_key": SecretStr(settings.EXA_API_KEY)})
    provider_cls = PROVIDERS.get(safe_config.provider)
    if not provider_cls:
        raise ResearchProviderError("Unsupported research provider")
    provider = provider_cls(safe_config)
    try:
        provider.validate_ready()
    except ResearchProviderError as exc:
        if safe_config.fallback_to_mock:
            return MockResearchProvider(ResearchConfig(provider="mock"))
        raise exc
    return provider
