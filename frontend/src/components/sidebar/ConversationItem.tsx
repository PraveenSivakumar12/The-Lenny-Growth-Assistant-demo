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
      className={`group relative flex items-center justify-between px-3 py-2.5 rounded-lg text-sm cursor-pointer transition-all ${
        isActive
          ? 'bg-navy-800 text-white font-medium border-l-2 border-violet-500'
          : 'text-slate-300 hover:bg-navy-800/60 hover:text-white'
      }`}
      onClick={() => onSelect(conversation.id)}
    >
      <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
        <MessageSquare
          className={`w-4 h-4 flex-shrink-0 ${
            isActive ? 'text-violet-400' : 'text-slate-400 group-hover:text-slate-300'
          }`}
        />
        <span className="truncate text-xs">{conversation.title}</span>
      </div>

      <div className="flex items-center gap-1">
        {conversation.message_count > 0 && (
          <span className="text-[10px] text-slate-400 group-hover:hidden px-1.5 py-0.5 rounded bg-navy-900/80">
            {conversation.message_count}
          </span>
        )}

        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRename(conversation.id, conversation.title);
            }}
            className="p-1 hover:text-violet-300 text-slate-400 rounded"
            title="Rename session"
            aria-label="Rename conversation"
          >
            <Edit2 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(conversation.id, conversation.title);
            }}
            className="p-1 hover:text-red-400 text-slate-400 rounded"
            title="Delete session"
            aria-label="Delete conversation"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
