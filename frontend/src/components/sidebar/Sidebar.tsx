import React, { useState } from 'react';
import {
  LayoutDashboard,
  Cpu,
  BookmarkCheck,
  Share2,
  Users,
  Mic,
  FileText,
  BarChart3,
  Database,
  CalendarCheck,
  Settings,
  HelpCircle,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Plus,
  Search,
  MessageSquare,
  Sparkles,
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
  activeNavTab: string;
  onSelectNavTab: (tab: string) => void;
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
  activeNavTab,
  onSelectNavTab,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showHistory, setShowHistory] = useState(false);

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside
      className={`relative flex flex-col h-full bg-[#EBF0FA]/90 text-slate-700 border-r border-[#D9E2F2] transition-all duration-300 ease-in-out select-none ${
        isCollapsed ? 'w-[72px]' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between px-4 py-4">
        {!isCollapsed ? (
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-purple-500 flex items-center justify-center text-white shadow-sm font-bold text-sm">
              TF
            </div>
            <div>
              <div className="text-sm font-extrabold text-slate-900 tracking-tight flex items-center gap-1">
                <span>TaskFlow</span>
                <span className="text-violet-600">AI</span>
              </div>
              <div className="text-[10px] text-slate-500 font-medium">Lenny Growth Intelligence</div>
            </div>
          </div>
        ) : (
          <div className="w-8 h-8 mx-auto rounded-xl bg-gradient-to-tr from-violet-600 via-indigo-600 to-purple-500 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            TF
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-white/60 transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-1 space-y-4 text-xs font-medium">
        {/* MAIN Section */}
        <div>
          {!isCollapsed && (
            <div className="px-3 pb-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              Main
            </div>
          )}
          <div className="space-y-0.5">
            <button
              onClick={() => {
                onSelectNavTab('dashboard');
                onNewChat();
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'dashboard' && !activeConversationId
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="Dashboard"
            >
              <LayoutDashboard className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Dashboard</span>}
            </button>

            <button
              onClick={() => {
                onSelectNavTab('history');
                setShowHistory(!showHistory);
              }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'history' || activeConversationId
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="Chat History"
            >
              <div className="flex items-center gap-3">
                <MessageSquare className="w-4 h-4 text-slate-500" />
                {!isCollapsed && <span>Chats & History</span>}
              </div>
              {!isCollapsed && conversations.length > 0 && (
                <span className="text-[10px] bg-slate-200/80 text-slate-600 px-1.5 py-0.5 rounded-full font-semibold">
                  {conversations.length}
                </span>
              )}
            </button>

            {/* Conversation list toggle */}
            {!isCollapsed && (activeNavTab === 'history' || activeConversationId || showHistory) && (
              <div className="pl-4 pr-1 py-1 space-y-1 mt-1 border-l-2 border-violet-200 ml-3">
                <div className="flex items-center justify-between pb-1">
                  <div className="relative flex-1">
                    <Search className="w-3 h-3 text-slate-400 absolute left-2 top-2" />
                    <input
                      type="text"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      placeholder="Search..."
                      className="w-full bg-white/80 border border-slate-200 text-[11px] rounded-lg pl-6 pr-2 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-violet-500"
                    />
                  </div>
                  <button
                    onClick={onNewChat}
                    className="p-1 text-violet-600 hover:bg-white rounded-lg ml-1"
                    title="New chat"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="max-h-36 overflow-y-auto space-y-0.5 pr-1">
                  {filteredConversations.length === 0 ? (
                    <div className="text-[11px] text-slate-400 italic py-1 px-2">No chats yet</div>
                  ) : (
                    filteredConversations.map((conv) => (
                      <ConversationItem
                        key={conv.id}
                        conversation={conv}
                        isActive={conv.id === activeConversationId}
                        onSelect={onSelectConversation}
                        onRename={onRenameConversation}
                        onDelete={onDeleteConversation}
                      />
                    ))
                  )}
                </div>
              </div>
            )}

            <button
              onClick={() => onSelectNavTab('flows')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'flows'
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="AI Flows"
            >
              <Cpu className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>AI Flows</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('library')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'library'
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="Library"
            >
              <BookmarkCheck className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Library</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('integrations')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'integrations'
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="Integrations"
            >
              <Share2 className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Integrations</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('team')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all ${
                activeNavTab === 'team'
                  ? 'bg-white text-violet-700 font-semibold shadow-sm'
                  : 'text-slate-600 hover:bg-white/60 hover:text-slate-900'
              } ${isCollapsed ? 'justify-center px-0' : ''}`}
              title="Team Workspace"
            >
              <Users className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Team Workspace</span>}
            </button>
          </div>
        </div>

        {/* AI TOOLS Section */}
        <div>
          {!isCollapsed && (
            <div className="px-3 pb-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
              AI Tools
            </div>
          )}
          <div className="space-y-0.5">
            <button
              onClick={() => onSelectNavTab('voice')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
                isCollapsed ? 'justify-center px-0' : ''
              }`}
              title="Voice Commands"
            >
              <Mic className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Voice Commands</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('smart_templates')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
                isCollapsed ? 'justify-center px-0' : ''
              }`}
              title="Smart Templates"
            >
              <FileText className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Smart Templates</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('auto_reports')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
                isCollapsed ? 'justify-center px-0' : ''
              }`}
              title="Auto Reports"
            >
              <BarChart3 className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Auto Reports</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('data_hub')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
                isCollapsed ? 'justify-center px-0' : ''
              }`}
              title="Data Source Hub"
            >
              <Database className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>Data Source Hub</span>}
            </button>

            <button
              onClick={() => onSelectNavTab('planner')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
                isCollapsed ? 'justify-center px-0' : ''
              }`}
              title="AI Planner"
            >
              <CalendarCheck className="w-4 h-4 text-slate-500" />
              {!isCollapsed && <span>AI Planner</span>}
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Footer Section (Setting, Support, Log Out) */}
      <div className="p-3 border-t border-[#D9E2F2]/80 space-y-0.5 text-xs font-medium">
        <button
          onClick={() => onSelectNavTab('settings')}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
            isCollapsed ? 'justify-center px-0' : ''
          }`}
          title="Setting"
        >
          <Settings className="w-4 h-4 text-slate-500" />
          {!isCollapsed && <span>Setting</span>}
        </button>

        <button
          onClick={() => onSelectNavTab('support')}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
            isCollapsed ? 'justify-center px-0' : ''
          }`}
          title="Support"
        >
          <HelpCircle className="w-4 h-4 text-slate-500" />
          {!isCollapsed && <span>Support</span>}
        </button>

        <button
          onClick={() => onSelectNavTab('logout')}
          className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-slate-600 hover:bg-white/60 hover:text-slate-900 transition-all ${
            isCollapsed ? 'justify-center px-0' : ''
          }`}
          title="Log Out"
        >
          <LogOut className="w-4 h-4 text-slate-500" />
          {!isCollapsed && <span>Log Out</span>}
        </button>

        {/* Index & health status pill */}
        {!isCollapsed && (
          <div className="pt-2 px-2 text-[10px] text-slate-400 flex items-center justify-between border-t border-slate-200/50 mt-1">
            <span className="flex items-center gap-1 text-slate-500">
              <Sparkles className="w-3 h-3 text-violet-500" />
              {health?.indexed_documents_count || 2461} chunks
            </span>
            <span className="bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-semibold text-[9px]">
              Ready
            </span>
          </div>
        )}
      </div>
    </aside>
  );
};
