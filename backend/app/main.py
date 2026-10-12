"""
FastAPI Application Entry Point
Mounts routers, configures CORS middleware, initializes database, and provides API documentation.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from app.core.config import settings
from app.core.logging import logger, log_event
from app.core.database import init_db

# Import API Routers
from app.api.health import router as health_router
from app.api.conversations import router as conversations_router
from app.api.chat import router as chat_router
from app.api.skills import router as skills_router
from app.api.artifacts import router as artifacts_router
from app.api.models import router as models_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database Tables
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} on {settings.HOST}:{settings.PORT}")
    await init_db()
    log_event("app_startup", env=settings.APP_ENV, default_provider=settings.DEFAULT_LLM_PROVIDER)
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-grade AI Assistant grounded in Lenny's Podcast transcripts. "
        "Supports RAG retrieval, conversation persistence, local Ollama & cloud LLMs, "
        "Ship 30 for 30 essays, and sandboxed HTML/CSS artifacts."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred. Please check logs."
        }
    )

# Include Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(artifacts_router, prefix="/api")
app.include_router(models_router, prefix="/api")


# In the production image the Vite build is copied here by the root Dockerfile.
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/", include_in_schema=False)
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    # Keep the API discoverable during backend-only local development.
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
        "status": "online"
    }


@app.get("/{asset_path:path}", include_in_schema=False)
async def serve_frontend_or_404(asset_path: str):
    """Serve Vite assets and SPA routes without masking missing API endpoints."""
    if asset_path == "api" or asset_path.startswith(("api/", "docs/", "redoc/")) or asset_path in {
        "openapi.json", "docs", "redoc"
    }:
        raise HTTPException(status_code=404, detail="Not Found")

    static_root = STATIC_DIR.resolve()
    candidate = (STATIC_DIR / asset_path).resolve()
    if candidate.is_relative_to(static_root) and candidate.is_file():
        return FileResponse(candidate)

    index_file = STATIC_DIR / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
