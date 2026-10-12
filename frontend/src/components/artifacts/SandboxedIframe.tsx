import React, { useMemo } from 'react';

interface SandboxedIframeProps {
  htmlContent: string;
  title?: string;
}

/**
 * Sandboxed Iframe Component
 * 
 * SECURITY BOUNDARY SPECIFICATION:
 * 1. sandbox="allow-scripts" enables internal interactivity (buttons, form inputs, local JS calculations).
 * 2. Noticeably OMITS 'allow-same-origin': The frame is treated as a unique, opaque origin.
 *    - Cannot read window.parent or window.top
 *    - Cannot access parent localStorage, sessionStorage, or document cookies
 *    - Cannot execute privileged API calls on behalf of the host application
 * 3. Noticeably OMITS 'allow-top-navigation' and 'allow-modals' to prevent phishing or frame breakouts.
 */
const ARTIFACT_CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; font-src data:; media-src data: blob:; connect-src 'none'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'";

function addArtifactCsp(html: string): string {
  // Put the CSP in the outer document before parsing any generated HTML. The
  // untrusted document is nested in the body; sandboxing plus CSP blocks network
  // requests and embedded frames while still allowing inline artifact scripts.
  const meta = `<meta http-equiv="Content-Security-Policy" content="${ARTIFACT_CSP}">`;
  return `<!doctype html><html><head>${meta}</head><body>${html}</body></html>`;
}

export const SandboxedIframe: React.FC<SandboxedIframeProps> = ({ htmlContent, title = 'Artifact Preview' }) => {
  const safeSrcDoc = useMemo(() => addArtifactCsp(htmlContent), [htmlContent]);
  return (
    <div className="w-full h-full flex flex-col bg-white rounded-lg overflow-hidden border border-slate-200">
      <iframe
        title={title}
        srcDoc={safeSrcDoc}
        sandbox="allow-scripts"
        className="w-full h-full border-none"
        loading="lazy"
      />
    </div>
  );
};
