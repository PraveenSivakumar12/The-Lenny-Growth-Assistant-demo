import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Cpu, Cloud, Check } from 'lucide-react';
import { ModelOption } from '../../types';

interface ModelSelectorProps {
  models: ModelOption[];
  activeProvider: string;
  onSelectProvider: (provider: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  models,
  activeProvider,
  onSelectProvider,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedModel = models.find((m) => m.provider === activeProvider) || models[0];

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 px-3 py-1.5 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-violet-500"
      >
        {selectedModel?.is_local ? (
          <Cpu className="w-3.5 h-3.5 text-violet-600" />
        ) : (
          <Cloud className="w-3.5 h-3.5 text-blue-600" />
        )}
        <span className="font-semibold">{selectedModel?.name || 'Select Model'}</span>
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            selectedModel?.is_available ? 'bg-emerald-500' : 'bg-amber-400'
          }`}
        />
        <ChevronDown className="w-3.5 h-3.5 text-slate-400 ml-0.5" />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-40 animate-in fade-in zoom-in-95 duration-100">
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
            Select Model Provider
          </div>
          {models.map((m) => {
            const isSelected = m.provider === activeProvider;
            return (
              <button
                key={m.id}
                onClick={() => {
                  onSelectProvider(m.provider);
                  setIsOpen(false);
                }}
                className={`w-full text-left px-3 py-2 text-xs flex items-start gap-2.5 hover:bg-slate-50 transition-colors ${
                  isSelected ? 'bg-violet-50/70 text-violet-900' : 'text-slate-700'
                }`}
              >
                <div className="mt-0.5">
                  {m.is_local ? (
                    <Cpu className="w-3.5 h-3.5 text-violet-600" />
                  ) : (
                    <Cloud className="w-3.5 h-3.5 text-blue-600" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800">{m.name}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                        m.is_local
                          ? 'bg-violet-100 text-violet-700'
                          : 'bg-blue-100 text-blue-700'
                      }`}
                    >
                      {m.is_local ? 'Local' : 'Cloud'}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                    {m.description}
                  </p>
                </div>
                {isSelected && <Check className="w-4 h-4 text-violet-600 mt-0.5" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
