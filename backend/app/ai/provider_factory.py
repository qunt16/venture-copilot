from pydantic import SecretStr

from app.ai.base import AIConfig, AIProviderError, BaseAIProvider
from app.ai.providers.anthropic_provider import AnthropicProvider
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.openai_compatible_provider import OpenAICompatibleProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import settings


class DeepSeekProvider(OpenAICompatibleProvider):
    provider_name = "deepseek"
    default_base_url = "https://api.deepseek.com/v1"
    default_model = "deepseek-chat"


class QwenProvider(OpenAICompatibleProvider):
    provider_name = "qwen"
    default_base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    default_model = "qwen-plus"


class MoonshotProvider(OpenAICompatibleProvider):
    provider_name = "moonshot"
    default_base_url = "https://api.moonshot.cn/v1"
    default_model = "moonshot-v1-8k"


class OpenRouterProvider(OpenAICompatibleProvider):
    provider_name = "openrouter"
    default_base_url = "https://openrouter.ai/api/v1"
    default_model = "openai/gpt-4o-mini"


class OllamaProvider(OpenAICompatibleProvider):
    provider_name = "ollama"
    default_base_url = "http://host.docker.internal:11434/v1"
    default_model = "qwen2.5"
    requires_api_key = False


PROVIDERS: dict[str, type[BaseAIProvider]] = {
    "mock": MockProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "deepseek": DeepSeekProvider,
    "qwen": QwenProvider,
    "moonshot": MoonshotProvider,
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "openai_compatible": OpenAICompatibleProvider,
}


def get_provider(config: AIConfig | None) -> BaseAIProvider:
    safe_config = config or AIConfig()
    if safe_config.provider == "openai" and not safe_config.api_key and settings.OPENAI_API_KEY:
        safe_config = safe_config.model_copy(update={"api_key": SecretStr(settings.OPENAI_API_KEY)})
    if safe_config.provider == "openrouter" and not safe_config.api_key and settings.OPENROUTER_API_KEY:
        safe_config = safe_config.model_copy(update={"api_key": SecretStr(settings.OPENROUTER_API_KEY)})
    provider_cls = PROVIDERS.get(safe_config.provider)
    if not provider_cls:
        raise AIProviderError("Unsupported AI provider")

    provider = provider_cls(safe_config)
    try:
        provider.validate_ready()
    except AIProviderError as exc:
        if safe_config.fallback_to_mock:
            return MockProvider(AIConfig(provider="mock"))
        raise exc
    return provider


def provider_name(config: AIConfig | None) -> str:
    return get_provider(config).provider_name
