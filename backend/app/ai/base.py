import json
import logging
import re

import httpx
from pydantic import BaseModel, Field, SecretStr


ProviderName = str


class AIConfig(BaseModel):
    provider: ProviderName = "mock"
    api_key: SecretStr | None = Field(default=None, repr=False)
    model: str | None = None
    base_url: str | None = None
    fallback_to_mock: bool = True


class AIProviderError(Exception):
    pass


class BaseAIProvider:
    provider_name = "base"

    def __init__(self, config: AIConfig | None = None) -> None:
        self.config = config or AIConfig()

    def validate_ready(self) -> None:
        if self.provider_name != "mock" and not self.config.api_key:
            raise AIProviderError("Provider is not configured")

    def generate_business_plan_context(self, context: dict) -> dict:
        self.validate_ready()
        return {}

    def generate_research_context(self, context: dict) -> dict:
        self.validate_ready()
        return {}

    def generate_framework_context(self, context: dict) -> dict:
        self.validate_ready()
        return {}


class OpenAICompatibleChatProvider(BaseAIProvider):
    default_model = "gpt-4o-mini"
    default_base_url = "https://api.openai.com/v1"
    requires_api_key = True

    def validate_ready(self) -> None:
        if self.requires_api_key and not self.config.api_key:
            raise AIProviderError(
                f"{self.provider_name} provider failed: status=missing_api_key "
                f"model={self.model} body=api_key_required"
            )

    @property
    def model(self) -> str:
        return self.config.model or self.default_model

    @property
    def base_url(self) -> str:
        return (self.config.base_url or self.default_base_url).rstrip("/")

    def chat_json(self, system: str, user: str, fallback_key: str) -> dict:
        content = self.chat(system, user)
        try:
            return _extract_json(content, fallback_key)
        except AIProviderError as exc:
            raise AIProviderError(
                f"{self.provider_name} provider failed: status=parse_error "
                f"model={self.model} body={str(exc)}"
            ) from exc

    def chat(self, system: str, user: str) -> str:
        self.validate_ready()
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key.get_secret_value()}"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                logging.getLogger(__name__).info(
                    "ai_provider_response",
                    extra={"provider": self.provider_name, "model": self.model, "status_code": response.status_code},
                )
                if response.status_code >= 400:
                    raise AIProviderError(
                        f"{self.provider_name} provider failed: status={response.status_code} "
                        f"model={self.model} body={_safe_body(response.text)}"
                    )
                data = response.json()
        except httpx.HTTPError as exc:
            raise AIProviderError(
                f"{self.provider_name} provider failed: status=network_error "
                f"model={self.model} body={type(exc).__name__}"
            ) from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(
                f"{self.provider_name} provider failed: status=invalid_response "
                f"model={self.model} body=missing_choices_message_content"
            ) from exc

    def generate_business_plan_context(self, context: dict) -> dict:
        selected = context.get("selected_sections", [])
        section_meta = [
            {"key": section.get("key"), "heading": section.get("heading")}
            for section in context.get("sections", [])
        ]
        return self.chat_json(
            "你是中国高校创新创业竞赛商业计划书专家。只输出 JSON，不要输出 Markdown。zh-CN 正文必须全部为中文，不得出现英文段落。",
            json.dumps(
                {
                    "task": "为每个 selected section 生成正文。保留 key，不要新增章节；不要编造财务数据；引用和来源只能来自提供的 research。",
                    "project": context.get("project"),
                    "forecast_summary": context.get("forecast_summary"),
                    "research": context.get("research"),
                    "framework_analysis": context.get("framework_analysis"),
                    "review": context.get("review"),
                    "language": context.get("language"),
                    "template_type": context.get("template_type"),
                    "selected_sections": selected,
                    "sections": section_meta,
                    "output_schema": {"sections": [{"key": "section_key", "content": "正文"}]},
                },
                ensure_ascii=False,
            ),
            "sections",
        )

    def generate_research_context(self, context: dict) -> dict:
        return self.chat_json(
            "你是市场研究分析师。只输出 JSON，不要输出 Markdown。引用必须是公开网页 URL；不确定时降低结论强度。",
            json.dumps(
                {
                    "task": "生成市场研究报告，适合中国高校创业竞赛项目。",
                    "project": context.get("project"),
                    "output_schema": {
                        "summary": "string",
                        "market_size": "string",
                        "industry_trends": ["string"],
                        "competitors": ["string"],
                        "risks": ["string"],
                        "opportunities": ["string"],
                        "citations": [
                            {"title": "string", "source": "string", "url": "string", "source_type": "institution|company|government|report|news"}
                        ],
                    },
                },
                ensure_ascii=False,
            ),
            "summary",
        )

    def generate_framework_context(self, context: dict) -> dict:
        return self.chat_json(
            "你是战略分析顾问。只输出 JSON，不要输出 Markdown。中文请求必须输出中文正文。",
            json.dumps(
                {
                    "task": "基于项目、财务、研究内容生成指定战略框架。",
                    "language": context.get("language"),
                    "frameworks": context.get("frameworks"),
                    "project": context.get("project"),
                    "forecast_summary": context.get("forecast_summary"),
                    "research": context.get("research"),
                    "output_schema": {"frameworks": {"framework_key": {"field": "analysis"}}},
                },
                ensure_ascii=False,
            ),
            "frameworks",
        )


def _extract_json(text: str, fallback_key: str) -> dict:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        json_candidate = _extract_json_object(cleaned)
        if not json_candidate:
            raise AIProviderError("AI provider did not return valid JSON") from exc
        try:
            parsed = json.loads(json_candidate)
        except json.JSONDecodeError as nested_exc:
            raise AIProviderError("AI provider did not return valid JSON") from nested_exc
    if fallback_key == "sections" and isinstance(parsed, dict) and fallback_key not in parsed:
        section_items = []
        for key, value in parsed.items():
            if isinstance(value, str):
                section_items.append({"key": key, "content": value})
            elif isinstance(value, dict) and value.get("content"):
                section_items.append({"key": key, "content": value["content"]})
            elif isinstance(value, dict):
                section_items.append({"key": key, "content": json.dumps(value, ensure_ascii=False)})
        if section_items:
            return {"sections": section_items}
    if not isinstance(parsed, dict) or fallback_key not in parsed:
        raise AIProviderError("AI provider JSON did not match expected schema")
    return parsed


def _extract_json_object(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


def _safe_body(text: str) -> str:
    compact = " ".join((text or "").split())
    compact = re.sub(r"sk-[A-Za-z0-9_-]+", "[redacted]", compact)
    compact = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [redacted]", compact)
    return compact[:500]
