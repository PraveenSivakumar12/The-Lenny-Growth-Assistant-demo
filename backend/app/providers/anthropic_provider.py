"""
Anthropic Cloud Provider
Provides integration with Anthropic Claude models (e.g. Claude 3.5 Sonnet, Claude 3 Haiku).
"""

from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger, log_event
from app.providers.base import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self._default_model = default_model or settings.ANTHROPIC_MODEL

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not await self.is_available():
            raise ValueError(
                "Anthropic API key is missing or invalid. Please configure ANTHROPIC_API_KEY in your .env file."
            )

        target_model = model or self._default_model
        endpoint = "https://api.anthropic.com/v1/messages"

        # In Anthropic API, system prompt is passed as a top-level argument
        formatted_messages = []
        for m in messages:
            # Anthropic only allows 'user' and 'assistant' roles in messages array
            role = m["role"] if m["role"] in ["user", "assistant"] else "user"
            formatted_messages.append({"role": role, "content": m["content"]})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": target_model,
            "system": system_prompt,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                log_event("anthropic_request_start", model=target_model, message_count=len(messages))
                res = await client.post(endpoint, json=payload, headers=headers)

                if res.status_code != 200:
                    err_body = res.text
                    logger.error(f"Anthropic error {res.status_code}: {err_body}")
                    raise RuntimeError(f"Anthropic API error ({res.status_code}): {err_body}")

                data = res.json()
                content_blocks = data.get("content", [])
                text_content = "".join([block.get("text", "") for block in content_blocks if block.get("type") == "text"])
                usage = data.get("usage", {})

                log_event("anthropic_request_success", model=target_model, output_tokens=usage.get("output_tokens"))

                return LLMResponse(
                    content=text_content,
                    model_used=target_model,
                    provider="anthropic",
                    finish_reason=data.get("stop_reason", "end_turn"),
                    prompt_tokens=usage.get("input_tokens", 0),
                    completion_tokens=usage.get("output_tokens", 0),
                )
        except Exception as e:
            logger.error(f"Anthropic generation exception: {e}")
            raise
