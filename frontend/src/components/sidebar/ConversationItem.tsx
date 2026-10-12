import React from 'react';
import { MessageSquare, Edit2, Trash2 } from 'lucide-react';
import { ConversationSummary } from '../../types';

interface ConversationItemProps {
  conversation: ConversationSummary;
  isActive: boolean;
  onSelect: (id: string) => void;
  onRename: (id: string, currentTitle: string) => void;
  onDelete: (id: string, title: string) => void;
}

export const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onRename,
  onDelete,
}) => {
  return (
    <div
      className={`group relative flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs cursor-pointer transition-all ${
        isActive
          ? 'bg-white text-violet-700 font-medium shadow-xs border-l-2 border-violet-600'
          : 'text-slate-600 hover:bg-white/70 hover:text-slate-900'
      }`}
      onClick={() => onSelect(conversation.id)}
    >
      <div className="flex items-center gap-2 min-w-0 flex-1 pr-1">
        <MessageSquare
          className={`w-3.5 h-3.5 flex-shrink-0 ${
            isActive ? 'text-violet-600' : 'text-slate-400 group-hover:text-slate-500'
          }`}
        />
        <span className="truncate">{conversation.title}</span>
      </div>

      <div className="flex items-center gap-1">
        {conversation.message_count > 0 && (
          <span className="text-[9px] text-slate-400 group-hover:hidden px-1 py-0.2 rounded bg-slate-200/60">
            {conversation.message_count}
          </span>
        )}

        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRename(conversation.id, conversation.title);
            }}
            className="p-0.5 hover:text-violet-600 text-slate-400 rounded"
            title="Rename session"
            aria-label="Rename conversation"
          >
            <Edit2 className="w-3 h-3" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conversation.id, conversation.title);
            }}
            className="p-0.5 hover:text-red-600 text-slate-400 rounded"
            title="Delete session"
            aria-label="Delete conversation"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};
