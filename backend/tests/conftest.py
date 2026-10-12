"""
Pytest Test Configuration and Fixtures
Sets up isolated test database, mock providers, and test client.
"""

import os
import tempfile
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Set test environment variables before importing app
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["DEFAULT_LLM_PROVIDER"] = "mock"
os.environ["VECTOR_INDEX_DIR"] = tempfile.mkdtemp(prefix="lenny_test_index_")

from app.main import app
from app.models.db_models import Base
from app.core.database import get_db
from app.rag.vector_store import get_vector_store

# Synthetic evidence lets tests run without committing or depending on licensed raw transcripts.
_test_chunks = [
    {
        "chunk_id": "fixture-elena-0",
        "doc_id": "fixture-elena",
        "title": "Test fixture: Elena Verna, growth and Lovable",
        "guest": "Elena Verna",
        "date": "2026-01-01",
        "url": "https://example.test/elena-growth",
        "text": (
            "Synthetic test fixture only. Keywords: Elena Verna, Lovable, growth, retention, "
            "acquisition, product-market fit, aha moment, B2B SaaS, pricing models, customer value."
        ),
        "word_count": 20,
        "chunk_index": 0,
    },
    {
        "chunk_id": "fixture-pricing-0",
        "doc_id": "fixture-pricing",
        "title": "Test fixture: SaaS pricing models",
        "guest": "Test Guest",
        "date": "2026-01-02",
        "url": "https://example.test/pricing",
        "text": (
            "Synthetic test fixture only. Keywords: SaaS pricing models, per-seat pricing, "
            "usage-based pricing, retention, acquisition, growth strategy."
        ),
        "word_count": 18,
        "chunk_index": 0,
    },
]
_test_store = get_vector_store()
_test_store.chunks = []
_test_store.vectors = __import__("numpy").empty((0, 512), dtype=__import__("numpy").float32)
_test_store._rebuild_lexical_index()
_test_store.add_documents(_test_chunks)

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
test_async_session_factory = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Provides an isolated database session with created tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session_factory() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Provides an async HTTP client for FastAPI testing."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
