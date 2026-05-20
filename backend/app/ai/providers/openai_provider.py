from app.ai.base import OpenAICompatibleChatProvider


class OpenAIProvider(OpenAICompatibleChatProvider):
    provider_name = "openai"
    default_base_url = "https://api.openai.com/v1"
    default_model = "gpt-4o-mini"
