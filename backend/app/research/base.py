from typing import Literal

from pydantic import BaseModel, Field, SecretStr


ResearchProviderName = Literal["mock", "exa", "tavily", "serpapi"]


class ResearchConfig(BaseModel):
    provider: ResearchProviderName = "mock"
    api_key: SecretStr | None = Field(default=None, repr=False)
    type: Literal["auto", "fast", "instant", "deep-lite", "deep", "deep-reasoning"] = "auto"
    num_results: int = Field(default=8, ge=1, le=20)
    fallback_to_mock: bool = True


class ResearchProviderError(Exception):
    pass


class BaseResearchProvider:
    provider_name = "base"

    def __init__(self, config: ResearchConfig | None = None) -> None:
        self.config = config or ResearchConfig()

    def validate_ready(self) -> None:
        if self.provider_name != "mock" and not self.config.api_key:
            raise ResearchProviderError("Research provider is not configured")

    def generate_report(self, project) -> dict:
        self.validate_ready()
        raise NotImplementedError
