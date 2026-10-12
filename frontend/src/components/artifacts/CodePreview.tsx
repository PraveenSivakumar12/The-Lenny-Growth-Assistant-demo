import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface CodePreviewProps {
  code: string;
  language?: string;
}

export const CodePreview: React.FC<CodePreviewProps> = ({ code, language = 'text' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split('\n');

  return (
    <div className="relative h-full flex flex-col bg-slate-900 text-slate-100 rounded-lg overflow-hidden border border-slate-800 text-xs font-mono">
      {/* Code Header Bar */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-950 border-b border-slate-800">
        <span className="text-[11px] text-slate-400 font-semibold uppercase">{language}</span>
        <button
          onClick={handleCopy}
          className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] transition-colors"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      {/* Code Body with Line Numbers */}
      <div className="flex-1 overflow-auto p-3 leading-relaxed">
        <table className="w-full border-collapse">
          <tbody>
            {lines.map((line, idx) => (
              <tr key={idx} className="hover:bg-slate-800/40">
                <td className="w-8 pr-4 text-right text-slate-600 select-none text-[11px] align-top">
                  {idx + 1}
                </td>
                <td className="whitespace-pre text-slate-200 align-top">
                  {line || ' '}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
