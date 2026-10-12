import React, { useRef, useEffect } from 'react';
import { Layout, Edit2, Bot } from 'lucide-react';
import { ConversationDetail, ModelOption, Artifact } from '../../types';
import { MessageItem } from './MessageItem';
import { WelcomeScreen } from './WelcomeScreen';
import { ChatInput } from './ChatInput';
import { ModelSelector } from '../ui/ModelSelector';

interface ChatWorkspaceProps {
  conversation: ConversationDetail | null;
  models: ModelOption[];
  activeProvider: string;
  onSelectProvider: (provider: string) => void;
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  onRenameTitle: () => void;
  activeArtifact: Artifact | null;
  isArtifactOpen: boolean;
  onToggleArtifact: () => void;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  conversation,
  models,
  activeProvider,
  onSelectProvider,
  onSendMessage,
  isLoading,
  onRenameTitle,
  activeArtifact,
  isArtifactOpen,
  onToggleArtifact,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages, isLoading]);

  const hasMessages = conversation && conversation.messages.length > 0;

  return (
    <main className="flex-1 flex flex-col h-full bg-slate-50/60 overflow-hidden">
      {/* Top Header Bar */}
      <header className="flex items-center justify-between px-4 sm:px-6 py-3 bg-white border-b border-slate-200/80 z-10 shadow-sm">
        <div className="flex items-center gap-2 min-w-0">
          <h2
            className="text-sm font-semibold text-slate-800 truncate cursor-pointer hover:text-violet-600 transition-colors"
            onClick={onRenameTitle}
            title="Click to rename conversation"
          >
            {conversation?.title || 'New Growth Chat'}
          </h2>
          <button
            onClick={onRenameTitle}
            className="text-slate-400 hover:text-slate-600 p-1 rounded"
            title="Rename chat"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="flex items-center gap-3">
          {/* Model Provider Picker */}
          <ModelSelector
            models={models}
            activeProvider={activeProvider}
            onSelectProvider={onSelectProvider}
          />

          {/* Artifact Viewer Toggle Button */}
          {activeArtifact && (
            <button
              onClick={onToggleArtifact}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                isArtifactOpen
                  ? 'bg-violet-50 text-violet-700 border-violet-200'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
              title="Toggle Artifact Viewer"
            >
              <Layout className="w-3.5 h-3.5 text-violet-600" />
              <span className="hidden sm:inline">Artifact</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Message Scroll Area */}
      <div className="flex-1 overflow-y-auto">
        {!hasMessages ? (
          <WelcomeScreen onSelectPrompt={onSendMessage} />
        ) : (
          <div className="divide-y divide-slate-100 max-w-4xl mx-auto py-2">
            {conversation.messages.map((msg) => (
              <MessageItem key={msg.id} message={msg} />
            ))}

            {/* Thinking / Searching Indicator */}
            {isLoading && (
              <div className="py-4 px-4 sm:px-6 flex gap-3 bg-white animate-pulse">
                <div className="w-7 h-7 rounded-lg bg-violet-100 text-violet-600 flex items-center justify-center">
                  <Bot className="w-4 h-4 animate-spin" />
                </div>
                <div className="flex-1 space-y-2 py-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-700">Lenny Assistant</span>
                    <span className="text-[10px] text-violet-600 bg-violet-50 px-2 py-0.5 rounded-full font-medium">
                      Searching Transcripts & Synthesizing...
                    </span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded w-3/4"></div>
                  <div className="h-2 bg-slate-200 rounded w-1/2"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </main>
  );
};
