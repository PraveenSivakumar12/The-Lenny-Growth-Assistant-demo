"""
Health and Diagnostics API
Provides /api/health endpoint verifying database, indexed knowledge, and provider connectivity.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import HealthResponse
from app.rag.vector_store import get_vector_store
from app.providers.router import get_provider_status

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint validating database connection, provider reachability, and index status."""
    # Check Database
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        logger.warning("Health check database query failed", exc_info=True)
        db_status = "unhealthy"

    # Check Vector Store
    vector_store = get_vector_store()
    doc_count = vector_store.count()

    # Check Providers
    providers_status = await get_provider_status()

    return HealthResponse(
        status="healthy" if "unhealthy" not in db_status else "degraded",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        database=db_status,
        active_provider=settings.DEFAULT_LLM_PROVIDER,
        providers_status=providers_status,
        indexed_documents_count=doc_count
    )
