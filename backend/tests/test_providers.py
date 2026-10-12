"""
Tests for Model Providers and Provider Router
"""

import pytest
from app.providers.router import get_provider, list_models, get_provider_status


@pytest.mark.asyncio
async def test_provider_resolution():
    ollama_p = get_provider("ollama")
    assert ollama_p.provider_name == "ollama"

    openai_p = get_provider("openai")
    assert openai_p.provider_name == "openai"

    anthropic_p = get_provider("anthropic")
    assert anthropic_p.provider_name == "anthropic"

    mock_p = get_provider("mock")
    assert mock_p.provider_name == "offline_fallback"


@pytest.mark.asyncio
async def test_list_models():
    models = await list_models()
    assert len(models) >= 3
    providers = [m.provider for m in models]
    assert "ollama" in providers
    assert "openai" in providers
    assert "anthropic" in providers


@pytest.mark.asyncio
async def test_provider_status_dict():
    status = await get_provider_status()
    assert "ollama" in status
    assert "openai" in status
    assert "anthropic" in status
