import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, Sparkles, User, BookOpen } from 'lucide-react';
import { Message } from '../../types';
import { CitationCard } from './CitationCard';

interface MessageItemProps {
  message: Message;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isAssistant = message.role === 'assistant';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`py-4 px-4 sm:px-6 flex gap-3 ${isAssistant ? 'bg-white border-y border-slate-100' : 'bg-transparent'}`}>
      {/* Avatar Icon */}
      <div className="flex-shrink-0 mt-0.5">
        {isAssistant ? (
          <div className="w-7 h-7 rounded-lg bg-violet-600 text-white flex items-center justify-center shadow-sm">
            <Sparkles className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center">
            <User className="w-4 h-4" />
          </div>
        )}
      </div>

      {/* Message Body */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-800">
              {isAssistant ? 'Lenny Assistant' : 'You'}
            </span>
            {isAssistant && message.model_used && (
              <span className="text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded font-mono">
                {message.model_used}
              </span>
            )}
          </div>

          {/* Action buttons */}
          {isAssistant && (
            <button
              onClick={handleCopy}
              className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded"
              title="Copy response"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Content */}
        <div className="prose prose-sm prose-slate max-w-none leading-relaxed text-slate-800 break-words">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Citations Section */}
        {isAssistant && message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 mb-2">
              <BookOpen className="w-3.5 h-3.5 text-violet-600" />
              <span>Verified Podcast Sources ({message.sources.length})</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((citation, idx) => (
                <CitationCard key={idx} citation={citation} index={idx} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
