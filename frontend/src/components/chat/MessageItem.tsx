import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Copy, Check, Sparkles, BookOpen } from 'lucide-react';
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
    <div
      className={`py-4 px-4 sm:px-6 my-2 rounded-2xl flex gap-3.5 transition-all ${
        isAssistant
          ? 'bg-white shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-200/80'
          : 'bg-[#F2F6FC] border border-slate-200/50'
      }`}
    >
      {/* Avatar Icon */}
      <div className="flex-shrink-0 mt-0.5">
        {isAssistant ? (
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white flex items-center justify-center shadow-xs">
            <Sparkles className="w-4 h-4" />
          </div>
        ) : (
          <img
            src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces"
            alt="Sarah"
            className="w-8 h-8 rounded-xl object-cover ring-1 ring-slate-300"
          />
        )}
      </div>

      {/* Message Body */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-800">
              {isAssistant ? 'TaskFlow AI' : 'Sarah'}
            </span>
            {isAssistant && message.model_used && (
              <span className="text-[10px] text-violet-700 bg-violet-50 px-2 py-0.5 rounded-full font-medium">
                {message.model_used}
              </span>
            )}
          </div>

          {/* Copy action */}
          {isAssistant && (
            <button
              onClick={handleCopy}
              className="text-slate-400 hover:text-slate-600 transition-colors p-1 rounded-lg hover:bg-slate-50"
              title="Copy response"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>

        {/* Content */}
        <div className="prose prose-sm prose-slate max-w-none leading-relaxed text-slate-800 break-words text-xs sm:text-sm">
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
