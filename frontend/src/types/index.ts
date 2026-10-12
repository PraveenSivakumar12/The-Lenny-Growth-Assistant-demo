export interface SourceCitation {
  title: string;
  guest?: string;
  date?: string;
  url?: string;
  excerpt: string;
  score?: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceCitation[];
  model_used?: string;
  created_at: string;
}

export interface Artifact {
  id: string;
  conversation_id: string;
  title: string;
  artifact_type: 'markdown' | 'html';
  content: string;
  metadata_info?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface ConversationSummary {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
  artifacts: Artifact[];
}

export interface ModelOption {
  id: string;
  name: string;
  provider: 'ollama' | 'openai' | 'anthropic';
  is_local: boolean;
  is_available: boolean;
  description: string;
}

export interface HealthStatus {
  status: string;
  app: string;
  version: string;
  database: string;
  active_provider: string;
  providers_status: Record<string, boolean>;
  indexed_documents_count: number;
}
