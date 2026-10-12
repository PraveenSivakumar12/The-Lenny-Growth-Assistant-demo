import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Code2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInsertHelper = (helperText: string) => {
    setInput(helperText);
    textareaRef.current?.focus();
  };

  return (
    <div className="border-t border-slate-200/80 bg-white p-3 sm:p-4">
      <div className="max-w-4xl mx-auto">
        {/* Quick Action Suggestion Pills */}
        <div className="flex items-center gap-1.5 mb-2 overflow-x-auto pb-1 text-[11px] text-slate-500">
          <span className="font-semibold text-slate-400 text-[10px] uppercase">Quick Skills:</span>
          <button
            type="button"
            onClick={() => handleInsertHelper('Write a Ship 30 for 30 essay on: ')}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 text-slate-700 transition-colors"
          >
            <FileText className="w-3 h-3 text-amber-600" />
            Ship 30 Essay
          </button>
          <button
            type="button"
            onClick={() => handleInsertHelper('Generate an interactive HTML/CSS UI component for: ')}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200/80 text-slate-700 transition-colors"
          >
            <Code2 className="w-3 h-3 text-emerald-600" />
            HTML Webpage
          </button>
        </div>

        {/* Input Box */}
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 focus-within:border-violet-500 focus-within:ring-1 focus-within:ring-violet-500 rounded-xl p-2 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a PM or growth question, or request a Ship 30 essay... (Enter to send, Shift+Enter for new line)"
            disabled={isLoading}
            className="w-full bg-transparent resize-none outline-none text-xs sm:text-sm text-slate-800 placeholder-slate-400 py-1 px-1.5 max-h-40 leading-relaxed disabled:opacity-50"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 p-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:bg-slate-200 text-white disabled:text-slate-400 transition-colors shadow-sm focus:outline-none"
            title="Send message"
            aria-label="Send message"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
