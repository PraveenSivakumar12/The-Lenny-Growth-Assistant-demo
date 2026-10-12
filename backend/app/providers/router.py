"""
Model Provider Router & Factory
Resolves the requested or default provider, checks service availability,
and surfaces available models to the frontend.
"""

from typing import Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import ModelOption
from app.providers.base import BaseLLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.mock_provider import MockOfflineProvider


class ProviderRouter:
    def __init__(self):
        self.ollama = OllamaProvider()
        self.openai = OpenAIProvider()
        self.anthropic = AnthropicProvider()
        self.mock = MockOfflineProvider()

    def get_provider(self, requested_name: Optional[str] = None) -> BaseLLMProvider:
        """Returns the appropriate provider based on parameter or default config."""
        name = (requested_name or settings.DEFAULT_LLM_PROVIDER).lower()

        if name == "ollama":
            return self.ollama
        elif name == "openai":
            return self.openai
        elif name == "anthropic":
            return self.anthropic
        elif name in ["offline", "mock"]:
            return self.mock
        else:
            logger.warning(f"Unrecognized provider '{name}', falling back to default '{settings.DEFAULT_LLM_PROVIDER}'")
            return self.ollama

    async def get_provider_status(self) -> Dict[str, bool]:
        """Checks availability of all configured providers."""
        return {
            "ollama": await self.ollama.is_available(),
            "openai": await self.openai.is_available(),
            "anthropic": await self.anthropic.is_available(),
        }

    async def list_available_models(self) -> List[ModelOption]:
        """Returns catalog of models with live availability status."""
        ollama_ok = await self.ollama.is_available()
        openai_ok = await self.openai.is_available()
        anthropic_ok = await self.anthropic.is_available()

        models: List[ModelOption] = [
            ModelOption(
                id="ollama-llama3.2",
                name=f"Ollama ({settings.OLLAMA_MODEL})",
                provider="ollama",
                is_local=True,
                is_available=ollama_ok,
                description="Local model running via Ollama. 100% private, zero API cost."
            ),
            ModelOption(
                id="openai-gpt4o-mini",
                name="OpenAI GPT-4o Mini",
                provider="openai",
                is_local=False,
                is_available=openai_ok,
                description="Fast and cost-effective cloud model by OpenAI."
            ),
            ModelOption(
                id="anthropic-claude35",
                name="Anthropic Claude 3.5 Sonnet",
                provider="anthropic",
                is_local=False,
                is_available=anthropic_ok,
                description="State-of-the-art reasoning and agent execution by Anthropic."
            )
        ]
        return models


    async def resolve_provider(self, requested_name: Optional[str] = None) -> BaseLLMProvider:
        """Returns the requested provider, or auto-fallbacks to the first available cloud/local provider."""
        provider = self.get_provider(requested_name)
        if not await provider.is_available():
            if await self.openai.is_available():
                logger.info(f"Requested provider '{provider.provider_name}' is unavailable. Auto-routing to OpenAI.")
                return self.openai
            if await self.anthropic.is_available():
                logger.info(f"Requested provider '{provider.provider_name}' is unavailable. Auto-routing to Anthropic.")
                return self.anthropic
        return provider


# Global singleton router
router_instance = ProviderRouter()


def get_provider(name: Optional[str] = None) -> BaseLLMProvider:
    return router_instance.get_provider(name)


async def resolve_provider(name: Optional[str] = None) -> BaseLLMProvider:
    return await router_instance.resolve_provider(name)


async def get_provider_status() -> Dict[str, bool]:
    return await router_instance.get_provider_status()


async def list_models() -> List[ModelOption]:
    return await router_instance.list_available_models()
