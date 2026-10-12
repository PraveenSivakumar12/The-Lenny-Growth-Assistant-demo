"""
Chat Interaction API
Handles incoming user turns, thread context preservation, RAG grounding,
and model response persistence.
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.logging import logger, log_event
from app.models.db_models import Conversation, Message, Artifact
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation, ArtifactResponse
from app.providers.router import get_provider
from app.agent.runner import AgentOrchestrator

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Processes a user message, performs semantic retrieval, executes agent routing, and persists results."""
    # 1. Resolve or Create Conversation
    conv = None
    if payload.conversation_id:
        stmt = select(Conversation).where(Conversation.id == payload.conversation_id)
        res = await db.execute(stmt)
        conv = res.scalar_one_or_none()
        if not conv:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation '{payload.conversation_id}' not found."
            )
    else:
        # Create a new conversation thread
        # Generate initial title from first 6 words of message
        words = payload.message.strip().split()
        title_candidate = " ".join(words[:6])
        if len(words) > 6:
            title_candidate += "..."

        conv = Conversation(title=title_candidate or "New Growth Chat")
        db.add(conv)
        await db.commit()
        await db.refresh(conv)

    # 2. Retrieve Conversation History for Thread Context
    msg_stmt = (
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    msg_res = await db.execute(msg_stmt)
    history_messages = msg_res.scalars().all()
    history = [{"role": m.role, "content": m.content} for m in history_messages]

    # 3. Save User Message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=payload.message
    )
    db.add(user_msg)
    await db.commit()
    await db.refresh(user_msg)

    # 4. Resolve Model Provider & Execute Agent Turn
    provider = get_provider(payload.provider)
    orchestrator = AgentOrchestrator(provider=provider, model=payload.model)

    assistant_text, citations, artifact_data = await orchestrator.execute_turn(
        user_message=payload.message,
        conversation_history=history
    )

    # 5. Save Assistant Message
    sources_dicts = [c.model_dump() for c in citations]
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_text,
        sources=sources_dicts,
        model_used=(payload.model or provider.default_model)
    )
    db.add(assistant_msg)

    # 6. Save Artifact if generated
    saved_artifact: Optional[ArtifactResponse] = None
    if artifact_data:
        artifact_record = Artifact(
            conversation_id=conv.id,
            title=artifact_data["title"],
            artifact_type=artifact_data["artifact_type"],
            content=artifact_data["content"],
            metadata_info=artifact_data.get("metadata_info")
        )
        db.add(artifact_record)
        await db.commit()
        await db.refresh(artifact_record)
        saved_artifact = ArtifactResponse.model_validate(artifact_record)

    # Update conversation timestamp
    conv.updated_at = datetime.utcnow()
    # Update title if it was default
    if conv.title == "New Conversation":
        words = payload.message.strip().split()
        conv.title = " ".join(words[:6])

    await db.commit()
    await db.refresh(assistant_msg)

    log_event("chat_turn_completed", conversation_id=conv.id, provider=provider.provider_name)

    return ChatResponse(
        conversation_id=conv.id,
        user_message_id=user_msg.id,
        assistant_message_id=assistant_msg.id,
        content=assistant_text,
        sources=citations,
        model_used=(payload.model or provider.default_model),
        artifact=saved_artifact
    )
