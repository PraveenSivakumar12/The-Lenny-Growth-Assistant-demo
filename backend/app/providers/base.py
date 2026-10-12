"""
Base LLM Provider Interface
Abstract foundation defining the contract for all AI model providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    model_used: str
    provider: str
    finish_reason: Optional[str] = "stop"
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0


class BaseLLMProvider(ABC):
    """Abstract interface for local and cloud LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider, e.g. 'ollama', 'openai', 'anthropic'."""
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model identifier for this provider."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Returns True if the provider is currently reachable and configured."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Executes a chat completion request."""
        pass
