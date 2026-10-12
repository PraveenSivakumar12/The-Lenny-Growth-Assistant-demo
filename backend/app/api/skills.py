"""
Skills API
Dedicated endpoints for invoked agent skills such as Ship 30 for 30 Essay writing.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.logging import logger, log_event
from app.models.db_models import Conversation, Artifact, Message
from app.models.schemas import EssayRequest, ArtifactResponse
from app.providers.router import get_provider
from app.agent.essay_skill import generate_ship30_essay

router = APIRouter(prefix="/skills", tags=["Agent Skills"])


@router.post("/essay", response_model=ArtifactResponse)
async def create_essay_skill(
    payload: EssayRequest,
    db: AsyncSession = Depends(get_db)
):
    """Executes the Ship 30 for 30 essay generation skill and persists the resulting artifact."""
    conv = None
    if payload.conversation_id:
        stmt = select(Conversation).where(Conversation.id == payload.conversation_id)
        res = await db.execute(stmt)
        conv = res.scalar_one_or_none()

    if not conv:
        # Create dedicated conversation for this essay
        conv = Conversation(title=f"Essay: {payload.topic[:30]}")
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

    provider = get_provider(payload.provider)

    # Fetch recent conversation context if available
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    msg_res = await db.execute(msg_stmt)
    history_messages = msg_res.scalars().all()
    history_summary = "\n".join([f"{m.role}: {m.content}" for m in history_messages[-4:]]) if history_messages else None

    try:
        title, essay_md, citations, meta = await generate_ship30_essay(
            topic=payload.topic,
            provider=provider,
            target_words=payload.target_words,
            conversation_context=history_summary
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    # Persist as Artifact
    artifact = Artifact(
        conversation_id=conv.id,
        title=title,
        artifact_type="markdown",
        content=essay_md,
        metadata_info=meta
    )
    db.add(artifact)

    # Add message notification in conversation
    notif = Message(
        conversation_id=conv.id,
        role="assistant",
        content=f"Generated Ship 30 for 30 essay: **{title}** (~{meta.get('word_count', 1250)} words). View it in the Artifact panel.",
        sources=[c.model_dump() for c in citations],
        model_used=provider.default_model
    )
    db.add(notif)

    await db.commit()
    await db.refresh(artifact)

    log_event("skill_essay_completed", topic=payload.topic, conversation_id=conv.id)
    return ArtifactResponse.model_validate(artifact)
