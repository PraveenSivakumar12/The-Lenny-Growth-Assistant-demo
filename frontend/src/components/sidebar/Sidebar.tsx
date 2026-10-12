import React, { useState } from 'react';
import {
  Plus,
  Search,
  Sparkles,
  ChevronLeft,
  ChevronRight,
  Radio,
  BookOpen
} from 'lucide-react';
import { ConversationSummary, HealthStatus } from '../../types';
import { ConversationItem } from './ConversationItem';

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  health: HealthStatus | null;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onRenameConversation: (id: string, currentTitle: string) => void;
  onDeleteConversation: (id: string, title: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  health,
  isCollapsed,
  onToggleCollapse,
  onSelectConversation,
  onNewChat,
  onRenameConversation,
  onDeleteConversation,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside
      className={`relative flex flex-col h-full bg-navy-950 text-slate-200 border-r border-navy-800 transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Header / Brand */}
      <div className="flex items-center justify-between p-4 border-b border-navy-800/80">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center text-white shadow-md">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="leading-tight">
              <h1 className="text-sm font-bold tracking-tight text-white">Lenny Assistant</h1>
              <p className="text-[10px] text-slate-400 font-medium">Growth & PM Intelligence</p>
            </div>
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg hover:bg-navy-800 text-slate-400 hover:text-white transition-colors ml-auto"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={onNewChat}
          className={`w-full flex items-center justify-center gap-2 py-2 px-3 bg-violet-600 hover:bg-violet-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all ${
            isCollapsed ? 'px-0' : ''
          }`}
          title="Start new conversation"
        >
          <Plus className="w-4 h-4" />
          {!isCollapsed && <span>New Conversation</span>}
        </button>
      </div>

      {/* Search Input (only when expanded) */}
      {!isCollapsed && (
        <div className="px-3 pb-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full bg-navy-900 border border-navy-800 text-xs rounded-lg pl-8 pr-3 py-1.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-violet-500 transition-all"
            />
          </div>
        </div>
      )}

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-1 py-1">
        {!isCollapsed && filteredConversations.length === 0 && (
          <div className="text-center py-8 text-xs text-slate-500">
            {searchQuery ? 'No matching chats found.' : 'No conversations yet.'}
          </div>
        )}

        {filteredConversations.map((conv) => (
          <ConversationItem
            key={conv.id}
            conversation={conv}
            isActive={conv.id === activeConversationId}
            onSelect={onSelectConversation}
            onRename={onRenameConversation}
            onDelete={onDeleteConversation}
          />
        ))}
      </div>

      {/* Footer System Status Card */}
      {!isCollapsed && (
        <div className="p-3 border-t border-navy-800/80 bg-navy-900/40 text-[11px] text-slate-400">
          <div className="flex items-center justify-between mb-1.5">
            <span className="flex items-center gap-1.5 text-slate-300 font-medium">
              <Radio className="w-3 h-3 text-emerald-400 animate-pulse" />
              Engine Online
            </span>
            <span className="text-[10px] bg-navy-800 px-1.5 py-0.5 rounded text-slate-300">
              {health?.active_provider || 'ollama'}
            </span>
          </div>
          <div className="flex items-center gap-1 text-[10px] text-slate-500">
            <BookOpen className="w-3 h-3 text-violet-400" />
            <span>{health?.indexed_documents_count || 2483} transcript chunks indexed</span>
          </div>
        </div>
      )}
    </aside>
  );
};
