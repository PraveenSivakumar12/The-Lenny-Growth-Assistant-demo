"""
Pydantic Request and Response Schemas
Defines validation contracts for all API endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


# Source Citation Schema
class SourceCitation(BaseModel):
    title: str = Field(..., description="Episode or article title")
    guest: Optional[str] = Field(None, description="Podcast guest name")
    date: Optional[str] = Field(None, description="Publication date (YYYY-MM-DD)")
    url: Optional[str] = Field(None, description="Lenny's Newsletter or podcast URL")
    excerpt: str = Field(..., description="Verifiable transcript quote or passage")
    score: Optional[float] = Field(None, description="Similarity or relevance score")


# Message Schemas
class MessageBase(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[SourceCitation]] = None
    model_used: Optional[str] = None
    created_at: datetime


# Artifact Schemas
class ArtifactBase(BaseModel):
    title: str
    artifact_type: Literal["markdown", "html"]
    content: str
    metadata_info: Optional[Dict[str, Any]] = None


class ArtifactCreate(ArtifactBase):
    conversation_id: str


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    title: str
    artifact_type: str
    content: str
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


# Conversation Schemas
class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    user_id: Optional[str] = "default_user"


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    artifacts: List[ArtifactResponse] = []


# Chat Interaction Schemas
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Conversation UUID. If omitted, a new conversation is started.")
    message: str = Field(..., min_length=1, description="User prompt or follow-up question")
    provider: Optional[str] = Field(None, description="Model provider ('ollama', 'openai', 'anthropic')")
    model: Optional[str] = Field(None, description="Specific model name override")


class ChatResponse(BaseModel):
    conversation_id: str
    user_message_id: str
    assistant_message_id: str
    content: str
    sources: List[SourceCitation] = []
    model_used: str
    artifact: Optional[ArtifactResponse] = None


# Essay Generation Schema
class EssayRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Associated conversation thread")
    topic: str = Field(..., min_length=3, description="Topic or question to turn into a Ship 30 for 30 essay")
    target_words: int = Field(1250, ge=500, le=2500, description="Target word count (~1,250 words)")
    provider: Optional[str] = Field(None, description="Model provider override")


# Model Provider Status Schemas
class ModelOption(BaseModel):
    id: str
    name: str
    provider: str
    is_local: bool
    is_available: bool
    description: str


class ProviderStatus(BaseModel):
    active_provider: str
    models: List[ModelOption]


# Health Response Schema
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    database: str
    active_provider: str
    providers_status: Dict[str, bool]
    indexed_documents_count: int
