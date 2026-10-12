"""
Models and Provider Management API
Allows UI to discover supported local & cloud models, view live availability status,
and update active model selection.
"""

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import logger, log_event
from app.models.schemas import ModelOption
from app.providers.router import list_models

router = APIRouter(prefix="/models", tags=["Models"])


class SetActiveProviderRequest(BaseModel):
    provider: str


@router.get("", response_model=List[ModelOption])
async def get_models():
    """Returns available local (Ollama) and cloud (OpenAI, Anthropic) models."""
    return await list_models()


@router.post("/active")
async def set_active_provider(payload: SetActiveProviderRequest):
    """Sets the active model provider for the running session."""
    valid_providers = ["ollama", "openai", "anthropic", "offline"]
    if payload.provider.lower() not in valid_providers:
        return {"error": f"Invalid provider. Choose from {valid_providers}"}

    settings.DEFAULT_LLM_PROVIDER = payload.provider.lower()
    log_event("active_provider_changed", new_provider=settings.DEFAULT_LLM_PROVIDER)
    return {
        "status": "success",
        "active_provider": settings.DEFAULT_LLM_PROVIDER
    }
