import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  X,
  Eye,
  Code2,
  Copy,
  Check,
  Download,
  FileText,
  Layout,
  Maximize2,
  Minimize2,
} from 'lucide-react';
import { Artifact } from '../../types';
import { SandboxedIframe } from './SandboxedIframe';
import { CodePreview } from './CodePreview';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  if (!artifact) {
    return (
      <div className="w-80 sm:w-96 border-l border-slate-200 bg-white flex flex-col items-center justify-center p-6 text-center text-slate-400">
        <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-3 text-slate-400">
          <Layout className="w-6 h-6" />
        </div>
        <h4 className="text-sm font-semibold text-slate-700 mb-1">No Active Artifact</h4>
        <p className="text-xs text-slate-500 max-w-xs">
          Ask the assistant to write a Ship 30 essay or generate an interactive HTML component to preview it here.
        </p>
      </div>
    );
  }

  const isHtml = artifact.artifact_type === 'html';

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const extension = isHtml ? 'html' : 'md';
    const mime = isHtml ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className={`border-l border-slate-200 bg-white flex flex-col h-full transition-all duration-200 z-30 shadow-lg ${
        isExpanded ? 'w-full fixed inset-0 sm:static sm:w-[680px]' : 'w-full sm:w-[480px] lg:w-[540px]'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-slate-50/70">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1 rounded bg-violet-100 text-violet-700">
            {isHtml ? <Layout className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
          </div>
          <div className="min-w-0">
            <h3 className="text-xs sm:text-sm font-semibold text-slate-800 truncate" title={artifact.title}>
              {artifact.title}
            </h3>
            <span className="text-[10px] text-slate-500 font-medium uppercase">
              {isHtml ? 'HTML / CSS Web Component' : 'Markdown Atomic Essay'}
            </span>
          </div>
        </div>

        {/* Header Action Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-200/60"
            title={isExpanded ? 'Restore size' : 'Expand panel'}
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-200/60"
            title="Close viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs & Toolbar Bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100 bg-white">
        {/* Tab Switcher */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-xs">
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all ${
              activeTab === 'preview'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Preview</span>
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all ${
              activeTab === 'code'
                ? 'bg-white text-slate-800 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            <Code2 className="w-3.5 h-3.5" />
            <span>Code</span>
          </button>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/70 rounded-md transition-colors"
            title="Copy artifact source"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            <span className="hidden sm:inline">{copied ? 'Copied' : 'Copy'}</span>
          </button>
          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/70 rounded-md transition-colors"
            title="Download file"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export</span>
          </button>
        </div>
      </div>

      {/* Main View Area */}
      <div className="flex-1 overflow-auto p-4 bg-slate-50/50">
        {activeTab === 'preview' ? (
          isHtml ? (
            <SandboxedIframe htmlContent={artifact.content} title={artifact.title} />
          ) : (
            <div className="bg-white p-6 sm:p-8 rounded-xl border border-slate-200 shadow-sm max-w-2xl mx-auto prose prose-sm prose-slate leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {artifact.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <CodePreview
            code={artifact.content}
            language={isHtml ? 'html' : 'markdown'}
          />
        )}
      </div>
    </div>
  );
};
