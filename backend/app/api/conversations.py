"""
Conversations API
Manages conversation sessions: creation, retrieval, renaming, listing, and deletion.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.core.database import get_db
from app.core.logging import logger, log_event
from app.models.db_models import Conversation, Message, Artifact
from app.models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationSummary,
    ConversationDetail,
    MessageResponse,
    ArtifactResponse
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationSummary, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Creates a new conversation session."""
    conv = Conversation(
        title=payload.title or "New Conversation",
        user_id=payload.user_id or "default_user"
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)

    log_event("conversation_created", id=conv.id, title=conv.title)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        user_id=conv.user_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )


@router.get("", response_model=List[ConversationSummary])
async def list_conversations(
    user_id: str = "default_user",
    db: AsyncSession = Depends(get_db)
):
    """Lists all conversations for a user, ordered by most recent activity."""
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(desc(Conversation.updated_at))
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    summaries = []
    for c in conversations:
        # Count messages
        cnt_stmt = select(func.count(Message.id)).where(Message.conversation_id == c.id)
        cnt_res = await db.execute(cnt_stmt)
        msg_count = cnt_res.scalar() or 0

        summaries.append(
            ConversationSummary(
                id=c.id,
                title=c.title,
                user_id=c.user_id,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=msg_count
            )
        )

    return summaries


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves conversation thread with all associated messages and generated artifacts."""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )

    # Fetch messages
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    msg_res = await db.execute(msg_stmt)
    messages = msg_res.scalars().all()

    # Fetch artifacts
    art_stmt = (
        select(Artifact)
        .where(Artifact.conversation_id == conversation_id)
        .order_by(Artifact.created_at)
    )
    art_res = await db.execute(art_stmt)
    artifacts = art_res.scalars().all()

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        user_id=conv.user_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
        artifacts=[ArtifactResponse.model_validate(a) for a in artifacts]
    )


@router.patch("/{conversation_id}", response_model=ConversationSummary)
async def rename_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Renames an existing conversation."""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )

    conv.title = payload.title
    await db.commit()
    await db.refresh(conv)

    log_event("conversation_renamed", id=conv.id, title=conv.title)
    return ConversationSummary(
        id=conv.id,
        title=conv.title,
        user_id=conv.user_id,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a conversation and all its messages and artifacts."""
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conv = result.scalar_one_or_none()

    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found."
        )

    await db.delete(conv)
    await db.commit()
    log_event("conversation_deleted", id=conversation_id)
    return None
