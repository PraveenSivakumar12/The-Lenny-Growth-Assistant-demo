import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, Quote } from 'lucide-react';
import { SourceCitation } from '../../types';

interface CitationCardProps {
  citation: SourceCitation;
  index: number;
}

export const CitationCard: React.FC<CitationCardProps> = ({ citation, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-slate-50 hover:bg-slate-100/80 border border-slate-200/80 rounded-lg p-2.5 text-xs transition-all">
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2 flex-1 min-w-0">
          <span className="flex-shrink-0 w-4 h-4 rounded bg-violet-100 text-violet-700 font-bold text-[10px] flex items-center justify-center mt-0.5">
            {index + 1}
          </span>
          <div className="min-w-0 flex-1">
            <h4 className="font-semibold text-slate-800 truncate" title={citation.title}>
              {citation.title}
            </h4>
            {citation.guest && (
              <p className="text-[11px] text-slate-500 font-medium truncate">
                Guest: {citation.guest} {citation.date ? `• ${citation.date}` : ''}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 flex-shrink-0">
          {citation.url && (
            <a
              href={citation.url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1 text-slate-400 hover:text-violet-600 transition-colors"
              title="View original episode post"
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 text-slate-400 hover:text-slate-600 transition-colors"
            title={isExpanded ? 'Collapse excerpt' : 'View excerpt'}
          >
            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-slate-600 text-[11px] leading-relaxed bg-white/70 p-2 rounded border border-slate-100">
          <div className="flex gap-1.5 items-start">
            <Quote className="w-3.5 h-3.5 text-violet-500 flex-shrink-0 mt-0.5" />
            <p className="italic">{citation.excerpt}</p>
          </div>
        </div>
      )}
    </div>
  );
};
