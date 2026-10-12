"""
Ollama Local Model Provider
Connects to local Ollama instance (default: http://localhost:11434).
Designed for offline privacy, 16GB RAM Windows environments, and local model demonstration.
"""

from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger, log_event
from app.providers.base import BaseLLMProvider, LLMResponse


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self._default_model = default_model or settings.OLLAMA_MODEL

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        return self._default_model

    async def is_available(self) -> bool:
        """Checks if the local Ollama server is reachable."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def list_installed_models(self) -> List[str]:
        """Lists models currently installed and available in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        target_model = model or self._default_model
        endpoint = f"{self.base_url}/api/chat"

        # Format messages with system prompt at the beginning
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for m in messages:
            formatted_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": target_model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                log_event("ollama_request_start", model=target_model, message_count=len(messages))
                response = await client.post(endpoint, json=payload)

                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"Ollama returned HTTP {response.status_code}: {error_detail}")
                    raise RuntimeError(
                        f"Ollama error ({response.status_code}): {error_detail}. "
                        f"Ensure model '{target_model}' is pulled using 'ollama run {target_model}'."
                    )

                data = response.json()
                assistant_message = data.get("message", {}).get("content", "")
                prompt_eval_count = data.get("prompt_eval_count", 0)
                eval_count = data.get("eval_count", 0)

                log_event(
                    "ollama_request_success",
                    model=target_model,
                    prompt_tokens=prompt_eval_count,
                    completion_tokens=eval_count
                )

                return LLMResponse(
                    content=assistant_message,
                    model_used=target_model,
                    provider="ollama",
                    finish_reason="stop",
                    prompt_tokens=prompt_eval_count,
                    completion_tokens=eval_count,
                )

        except httpx.ConnectError:
            logger.warning("Ollama connection failed: server not reachable.")
            raise RuntimeError(
                f"Cannot connect to local Ollama server at {self.base_url}. "
                "Please verify that Ollama is installed and running (run 'ollama serve' in terminal)."
            )
        except Exception as e:
            logger.error(f"Ollama generation failure: {e}")
            raise
