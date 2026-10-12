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
    <main className="flex-1 flex flex-col h-full bg-[#EDF2FA] overflow-hidden">
      {/* Top Header Bar - Matches TaskFlow Header with centered 'AI Assistant' and user avatar */}
      <header className="flex items-center justify-between px-6 py-3.5 bg-transparent border-b border-[#DDE5F2] z-10">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {hasMessages && (
            <div className="flex items-center gap-2">
              <h2
                className="text-xs sm:text-sm font-semibold text-slate-700 truncate cursor-pointer hover:text-violet-600 transition-colors"
                onClick={onRenameTitle}
                title="Click to rename"
              >
                {conversation?.title}
              </h2>
              <button
                onClick={onRenameTitle}
                className="text-slate-400 hover:text-slate-600 p-0.5 rounded"
                title="Rename"
              >
                <Edit2 className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>

        {/* Center Title */}
        <div className="text-center font-bold text-slate-800 text-sm tracking-tight flex items-center justify-center gap-1.5">
          <span>AI Assistant</span>
        </div>

        {/* Right Actions: Model selector & user profile avatar */}
        <div className="flex items-center justify-end gap-3 flex-1">
          {/* Artifact Viewer Toggle */}
          {activeArtifact && (
            <button
              onClick={onToggleArtifact}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                isArtifactOpen
                  ? 'bg-violet-100 text-violet-700 border-violet-300 shadow-2xs'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
              title="Toggle Artifact"
            >
              <Layout className="w-3.5 h-3.5 text-violet-600" />
              <span className="hidden sm:inline">Artifact</span>
            </button>
          )}

          {/* Model Selector */}
          <ModelSelector
            models={models}
            activeProvider={activeProvider}
            onSelectProvider={onSelectProvider}
          />

          {/* User Profile Avatar (from reference screenshot) */}
          <div className="relative group cursor-pointer">
            <img
              src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"
              alt="User profile"
              className="w-8 h-8 rounded-full object-cover ring-2 ring-violet-400/50 shadow-sm"
              title="Sarah (Logged In)"
            />
          </div>
        </div>
      </header>

      {/* Main Workspace Body */}
      <div className="flex-1 overflow-y-auto">
        {!hasMessages ? (
          <WelcomeScreen onSelectPrompt={onSendMessage} />
        ) : (
          <div className="divide-y divide-slate-200/60 max-w-3xl mx-auto py-4 px-3 sm:px-4">
            {conversation.messages.map((msg) => (
              <MessageItem key={msg.id} message={msg} />
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="py-4 px-4 flex gap-3 bg-white/80 rounded-2xl border border-slate-200/80 shadow-2xs animate-pulse my-2">
                <div className="w-8 h-8 rounded-xl bg-violet-600 text-white flex items-center justify-center shadow-xs">
                  <Bot className="w-4 h-4 animate-spin" />
                </div>
                <div className="flex-1 space-y-2 py-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-800">TaskFlow Lenny AI</span>
                    <span className="text-[10px] text-violet-700 bg-violet-100 px-2 py-0.5 rounded-full font-medium">
                      Retrieving transcripts & generating...
                    </span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded w-2/3"></div>
                  <div className="h-2 bg-slate-200 rounded w-1/3"></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Chat Input for ongoing conversation */}
      {hasMessages && <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />}
    </main>
  );
};
