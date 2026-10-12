"""
OpenAI Cloud Provider
Provides integration with OpenAI GPT models (e.g. gpt-4o, gpt-4o-mini).
"""

from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger, log_event
from app.providers.base import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self._explicit_api_key = api_key
        self._explicit_default_model = default_model

    @property
    def api_key(self) -> str:
        raw = self._explicit_api_key or settings.OPENAI_API_KEY or ""
        # Strip whitespace, quotes, and newlines that can happen when pasting into Railway variables
        return raw.strip().strip("'\"")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        raw = (self._explicit_default_model or settings.OPENAI_MODEL or "gpt-4o-mini").strip().strip("'\"")
        if raw.startswith("openai-"):
            raw = raw[len("openai-"):]
        return raw or "gpt-4o-mini"

    async def is_available(self) -> bool:
        key = self.api_key
        return bool(key and len(key) > 10)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        key = self.api_key
        if not key or len(key) <= 10:
            raise ValueError(
                "OpenAI API key is missing or invalid. Please configure OPENAI_API_KEY in your Railway Variables or .env file."
            )

        # Clean target model
        target_model = (model or self.default_model).strip().strip("'\"")
        if target_model.startswith("openai-"):
            target_model = target_model[len("openai-"):]
        if not target_model:
            target_model = "gpt-4o-mini"

        endpoint = "https://api.openai.com/v1/chat/completions"

        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                log_event("openai_request_start", model=target_model, message_count=len(messages))
                res = await client.post(endpoint, json=payload, headers=headers)

                if res.status_code != 200:
                    err_body = res.text
                    err_message = err_body
                    try:
                        err_json = res.json()
                        if "error" in err_json and isinstance(err_json["error"], dict):
                            err_message = err_json["error"].get("message", err_body)
                    except Exception:
                        pass

                    logger.error(f"OpenAI error {res.status_code}: {err_message}")
                    raise RuntimeError(f"OpenAI API error ({res.status_code}): {err_message}")

                data = res.json()
                choice = data["choices"][0]
                content = choice["message"]["content"]
                usage = data.get("usage", {})

                log_event("openai_request_success", model=target_model, total_tokens=usage.get("total_tokens"))

                return LLMResponse(
                    content=content,
                    model_used=target_model,
                    provider="openai",
                    finish_reason=choice.get("finish_reason", "stop"),
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                )
        except Exception as e:
            logger.error(f"OpenAI generation exception: {e}")
            raise
