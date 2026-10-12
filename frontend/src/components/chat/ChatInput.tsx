import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Plus, ArrowDown, FileText, Code2 } from 'lucide-react';

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
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
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
    <div className="p-3 sm:p-5 bg-gradient-to-t from-[#EDF2FA] to-transparent">
      <div className="max-w-3xl mx-auto">
        {/* Quick action prompts */}
        <div className="flex items-center gap-1.5 mb-2 overflow-x-auto pb-1 text-[11px] text-slate-500">
          <button
            type="button"
            onClick={() => handleInsertHelper('Write a Ship 30 for 30 essay on: ')}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/90 hover:bg-white text-slate-700 border border-slate-200/80 shadow-2xs hover:shadow-xs transition-all"
          >
            <FileText className="w-3 h-3 text-violet-600" />
            Ship 30 Essay
          </button>
          <button
            type="button"
            onClick={() => handleInsertHelper('Generate an interactive HTML/CSS UI component for: ')}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/90 hover:bg-white text-slate-700 border border-slate-200/80 shadow-2xs hover:shadow-xs transition-all"
          >
            <Code2 className="w-3 h-3 text-indigo-600" />
            HTML Web Artifact
          </button>
        </div>

        {/* Floating Rounded Card Input (TaskFlow Style) */}
        <div className="bg-white rounded-2xl shadow-[0_4px_24px_rgba(0,0,0,0.06)] border border-slate-200/90 p-2.5 sm:p-3 transition-all focus-within:shadow-[0_8px_30px_rgba(139,92,246,0.15)] focus-within:border-violet-300">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Anything"
            disabled={isLoading}
            className="w-full bg-transparent resize-none outline-none text-xs sm:text-sm text-slate-800 placeholder-slate-400 py-1 px-2 max-h-36 leading-relaxed disabled:opacity-50"
          />

          <div className="flex items-center justify-between pt-1 border-t border-slate-100 mt-1">
            <div className="flex items-center gap-1 text-slate-400">
              <button
                type="button"
                onClick={() => handleInsertHelper('How does Elena Verna reinvent growth loops?')}
                className="p-1.5 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                title="Prompt helper"
              >
                <Plus className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => handleInsertHelper('What are the counter-intuitive signals of PMF?')}
                className="p-1.5 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                title="Insert prompt"
              >
                <ArrowDown className="w-3.5 h-3.5" />
              </button>
            </div>

            <button
              type="button"
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isLoading}
              className={`w-8 h-8 rounded-xl flex items-center justify-center text-white transition-all shadow-sm ${
                input.trim() && !isLoading
                  ? 'bg-violet-600 hover:bg-violet-700 cursor-pointer'
                  : 'bg-violet-400 cursor-not-allowed opacity-60'
              }`}
              title="Send message"
              aria-label="Send message"
            >
              {isLoading ? (
                <div className="w-3.5 h-3.5 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              ) : (
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
