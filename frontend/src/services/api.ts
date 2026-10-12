import {
  ConversationSummary,
  ConversationDetail,
  ModelOption,
  HealthStatus,
  Artifact,
} from '../types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchConversations(): Promise<ConversationSummary[]> {
  const res = await fetch(`${API_BASE}/conversations`);
  if (!res.ok) throw new Error(`Failed to fetch conversations: ${res.statusText}`);
  return res.json();
}

export async function createConversation(title?: string): Promise<ConversationSummary> {
  const res = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title: title || 'New Conversation' }),
  });
  if (!res.ok) throw new Error(`Failed to create conversation: ${res.statusText}`);
  return res.json();
}

export async function fetchConversation(id: string): Promise<ConversationDetail> {
  const res = await fetch(`${API_BASE}/conversations/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch conversation ${id}: ${res.statusText}`);
  return res.json();
}

export async function renameConversation(id: string, title: string): Promise<ConversationSummary> {
  const res = await fetch(`${API_BASE}/conversations/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to rename conversation: ${res.statusText}`);
  return res.json();
}

export async function deleteConversation(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/conversations/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete conversation: ${res.statusText}`);
}

export async function sendChatMessage(params: {
  conversationId?: string | null;
  message: string;
  provider?: string;
  model?: string;
}): Promise<{
  conversation_id: string;
  user_message_id: string;
  assistant_message_id: string;
  content: string;
  sources: any[];
  model_used: string;
  artifact?: Artifact | null;
}> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      conversation_id: params.conversationId || null,
      message: params.message,
      provider: params.provider || null,
      model: params.model || null,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(errorData.detail || errorData.error || 'Failed to send message');
  }

  return res.json();
}

export async function fetchModels(): Promise<ModelOption[]> {
  const res = await fetch(`${API_BASE}/models`);
  if (!res.ok) throw new Error(`Failed to fetch models: ${res.statusText}`);
  return res.json();
}

export async function setActiveProvider(provider: string): Promise<void> {
  const res = await fetch(`${API_BASE}/models/active`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ provider }),
  });
  if (!res.ok) throw new Error(`Failed to set provider: ${res.statusText}`);
}

export async function generateEssaySkill(params: {
  topic: string;
  conversationId?: string | null;
  provider?: string;
}): Promise<Artifact> {
  const res = await fetch(`${API_BASE}/skills/essay`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      topic: params.topic,
      conversation_id: params.conversationId || null,
      provider: params.provider || null,
      target_words: 1250,
    }),
  });
  if (!res.ok) throw new Error(`Failed to generate essay: ${res.statusText}`);
  return res.json();
}
