"""
Artifacts API
Handles listing, fetching, and manual creation of Markdown and HTML artifacts.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.core.logging import logger, log_event
from app.models.db_models import Artifact, Conversation
from app.models.schemas import ArtifactCreate, ArtifactResponse

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("", response_model=List[ArtifactResponse])
async def list_artifacts(
    conversation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Lists saved artifacts, optionally filtered by conversation ID."""
    stmt = select(Artifact).order_by(desc(Artifact.created_at))
    if conversation_id:
        stmt = stmt.where(Artifact.conversation_id == conversation_id)

    result = await db.execute(stmt)
    artifacts = result.scalars().all()
    return [ArtifactResponse.model_validate(a) for a in artifacts]


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves a specific artifact by its unique ID."""
    stmt = select(Artifact).where(Artifact.id == artifact_id)
    result = await db.execute(stmt)
    artifact = result.scalar_one_or_none()

    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact '{artifact_id}' not found."
        )

    return ArtifactResponse.model_validate(artifact)


@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    payload: ArtifactCreate,
    db: AsyncSession = Depends(get_db)
):
    """Stores an artifact and links it to a conversation thread."""
    # Verify conversation exists
    c_stmt = select(Conversation).where(Conversation.id == payload.conversation_id)
    c_res = await db.execute(c_stmt)
    conv = c_res.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{payload.conversation_id}' not found."
        )

    artifact = Artifact(
        conversation_id=payload.conversation_id,
        title=payload.title,
        artifact_type=payload.artifact_type,
        content=payload.content,
        metadata_info=payload.metadata_info
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)

    log_event("artifact_persisted", id=artifact.id, title=artifact.title, type=artifact.artifact_type)
    return ArtifactResponse.model_validate(artifact)
