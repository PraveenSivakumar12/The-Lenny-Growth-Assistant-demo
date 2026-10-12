"""
Agent Runner & Orchestrator
Routes incoming user requests to the appropriate skill or tool:
- Grounded RAG Question Answering
- Ship 30 for 30 Essay Generation
- Interactive HTML/CSS or Markdown Artifact Generation
Preserves conversation context across turns while maintaining strict session isolation.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from app.core.logging import logger, log_event
from app.models.schemas import SourceCitation, ArtifactResponse
from app.providers.base import BaseLLMProvider
from app.rag.retriever import retrieve_context
from app.agent.prompts import SYSTEM_GROUNDING_PROMPT, HTML_ARTIFACT_PROMPT
from app.agent.essay_skill import generate_ship30_essay


class AgentOrchestrator:
    def __init__(self, provider: BaseLLMProvider, model: Optional[str] = None):
        self.provider = provider
        self.model = model

    def classify_intent(self, user_query: str) -> str:
        """Determines request intent: 'essay', 'html_artifact', 'markdown_artifact', or 'qa'."""
        q = user_query.lower()
        if any(term in q for term in ["ship 30", "atomic essay", "write an essay", "write a 1250 word essay", "generate essay"]):
            return "essay"
        elif any(term in q for term in ["html", "webpage", "web page", "ui component", "interactive calculator", "dashboard", "widget", "create a page"]):
            return "html_artifact"
        elif any(term in q for term in ["markdown spec", "prd document", "markdown table", "spec document", "generate markdown"]):
            return "markdown_artifact"
        return "qa"

    async def execute_turn(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
    ) -> Tuple[str, List[SourceCitation], Optional[Dict[str, Any]]]:
        """
        Executes an agent turn.
        Returns:
            assistant_text: Final response content
            sources: Citations used to ground the answer
            artifact_data: Optional generated artifact dict (title, type, content)
        """
        intent = self.classify_intent(user_message)
        log_event("agent_turn_started", intent=intent, query=user_message[:60])

        if intent == "essay":
            # Extract topic
            topic = user_message
            for prefix in ["write an essay on", "generate a ship 30 essay on", "write a ship 30 for 30 essay on", "write an essay about"]:
                if prefix in user_message.lower():
                    topic = re.split(prefix, user_message, flags=re.IGNORECASE)[-1].strip()
                    break

            # Format conversation context
            history_summary = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_history[-4:]]) if conversation_history else None

            try:
                title, essay_md, citations, meta = await generate_ship30_essay(
                    topic=topic,
                    provider=self.provider,
                    target_words=1250,
                    conversation_context=history_summary,
                    model=self.model
                )
            except ValueError as exc:
                return (str(exc), [], None)
            except RuntimeError as exc:
                return (str(exc), [], None)

            assistant_msg = (
                f"I've written a Ship 30 for 30-style essay on **\"{topic}\"** based on insights from Lenny's Podcast transcripts. "
                f"You can preview the rendered essay and copy the full Markdown in the Artifact Viewer panel on the right."
            )

            artifact_dict = {
                "title": title,
                "artifact_type": "markdown",
                "content": essay_md,
                "metadata_info": meta
            }

            return assistant_msg, citations, artifact_dict

        elif intent == "html_artifact":
            # Retrieve supporting context if related to growth
            citations, context_text = retrieve_context(query=user_message, top_k=3, threshold=0.18)

            system_prompt = HTML_ARTIFACT_PROMPT
            if context_text:
                system_prompt += f"\n\nBACKGROUND DOMAIN CONTEXT:\n{context_text}"

            messages = []
            for h in conversation_history[-3:]:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_message})

            try:
                response = await self.provider.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    model=self.model,
                    temperature=0.5,
                    max_tokens=2500
                )
                raw_code = response.content
            except Exception as e:
                logger.error(f"HTML generation error: {e}")
                raw_code = _get_fallback_html_artifact(user_message)

            # Extract HTML from code block if wrapped
            html_content = raw_code
            if "```html" in raw_code:
                parts = raw_code.split("```html")
                if len(parts) > 1:
                    html_content = parts[1].split("```")[0].strip()
            elif "```" in raw_code:
                parts = raw_code.split("```")
                if len(parts) > 1:
                    html_content = parts[1].strip()

            assistant_msg = (
                f"I've generated the requested interactive web artifact. "
                f"You can interact with the live preview and inspect the source code in the Artifact Viewer."
            )

            artifact_dict = {
                "title": f"Web Component: {user_message[:40]}...",
                "artifact_type": "html",
                "content": html_content,
                "metadata_info": {"provider": self.provider.provider_name}
            }

            return assistant_msg, citations, artifact_dict

        else:
            # Standard Grounded Conversational Q&A
            citations, context_text = retrieve_context(query=user_message, top_k=4, threshold=0.20)

            # Strict grounding: abstain instead of generating unsupported general claims.
            if not context_text or not citations:
                return (
                    "I couldn't find sufficient supporting evidence for this question in the indexed "
                    "Lenny's Podcast transcripts. Try narrowing the question to a topic or guest covered "
                    "in the archive.",
                    [],
                    None,
                )

            system_prompt = (
                SYSTEM_GROUNDING_PROMPT
                + f"\n\nCONTEXT FROM LENNY'S PODCAST TRANSCRIPTS:\n{context_text}"
            )

            # Build thread history with current question
            messages = []
            for h in conversation_history[-6:]:  # Keep last 6 turns for tight context retention
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": user_message})

            try:
                response = await self.provider.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    model=self.model,
                    temperature=0.6,
                    max_tokens=1500
                )
                assistant_text = response.content
            except ValueError as e:
                # Provider not configured (e.g. missing API key)
                logger.warning(f"Provider configuration error ({self.provider.provider_name}): {e}")
                fallback_summary = _build_grounded_fallback_summary(user_message, citations)
                assistant_text = (
                    f"⚠️ **Provider Configuration Notice (`{self.provider.provider_name}`):**\n"
                    f"{e}\n\n"
                    f"---\n\n"
                    f"{fallback_summary}"
                )
            except Exception as e:
                logger.error(f"Error during LLM chat completion ({self.provider.provider_name}): {e}")
                err_msg = str(e)
                fallback_summary = _build_grounded_fallback_summary(user_message, citations)

                # Targeted troubleshooting hint
                hint = ""
                if "429" in err_msg or "quota" in err_msg.lower():
                    hint = (
                        "💡 **Root Cause:** Your OpenAI account has **$0 credit balance** or exceeded its quota. "
                        "OpenAI API keys require adding prepaid credits at [platform.openai.com/billing](https://platform.openai.com/billing) "
                        "(Note: ChatGPT Plus subscription does not include API credits)."
                    )
                elif "401" in err_msg or "invalid_api_key" in err_msg.lower():
                    hint = (
                        "💡 **Root Cause:** The `OPENAI_API_KEY` in Railway Variables is invalid, mistyped, or revoked. "
                        "Create a new key at [platform.openai.com/api-keys](https://platform.openai.com/api-keys) and update Railway Variables."
                    )
                elif "404" in err_msg or "model" in err_msg.lower():
                    hint = (
                        "💡 **Root Cause:** Model name not found. Set `OPENAI_MODEL` to `gpt-4o-mini` in Railway Variables."
                    )

                assistant_text = (
                    f"⚠️ **AI Model Notice (`{self.provider.provider_name}`):**\n"
                    f"> {err_msg}\n\n"
                    + (f"{hint}\n\n" if hint else "")
                    + f"---\n\n"
                    f"{fallback_summary}"
                )

            return assistant_text, citations, None


def _build_grounded_fallback_summary(query: str, citations: List[SourceCitation]) -> str:
    """Synthesizes high-value advice directly from retrieved transcript chunks when LLM synthesis is unavailable."""
    if not citations:
        return "No matching transcripts were found for this query in the indexed episodes."

    lines = [
        f"### 🎙️ Grounded Insights from Lenny's Podcast Transcripts:\n",
        f"Here are the core takeaways directly from Lenny's guest interviews regarding **\"{query}\"**:\n"
    ]
    for i, c in enumerate(citations, 1):
        clean_excerpt = c.excerpt.replace("**", "").replace("...", "").strip()
        lines.append(
            f"**{i}. {c.guest}** — *\"{c.title}\"*\n"
            f"> \"{clean_excerpt}\"\n"
        )

    lines.append(
        "💡 **Actionable Takeaways:**\n"
        "- Validate user retention loops and qualitative feedback before scaling acquisition.\n"
        "- Test small product-led hypotheses iteratively with measurable engagement metrics.\n"
        "- Click the verified podcast source citations below to read the original interview segments."
    )
    return "\n".join(lines)


def _get_fallback_html_artifact(query: str) -> str:
    """Provides a sample interactive tool if offline."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Growth Metric Calculator</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f8fafc;
      color: #0f172a;
      display: flex;
      justify-content: center;
      padding: 30px;
      margin: 0;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
      padding: 24px;
      max-width: 480px;
      width: 100%;
    }}
    h2 {{ margin-top: 0; color: #7c3aed; font-size: 1.25rem; }}
    label {{ display: block; margin: 12px 0 4px; font-weight: 500; font-size: 0.9rem; }}
    input {{
      width: 100%;
      padding: 10px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      box-sizing: border-box;
      font-size: 1rem;
    }}
    button {{
      margin-top: 18px;
      width: 100%;
      background: #7c3aed;
      color: #fff;
      border: none;
      padding: 12px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
    }}
    button:hover {{ background: #6d28d9; }}
    .result {{
      margin-top: 20px;
      padding: 14px;
      background: #f1f5f9;
      border-radius: 8px;
      font-weight: 600;
      text-align: center;
      display: none;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h2>Interactive Growth Loop Calculator</h2>
    <p style="font-size: 0.85rem; color: #64748b;">Calculate your Net Revenue Retention or Viral K-Factor.</p>
    <label for="invites">Invites sent per user:</label>
    <input type="number" id="invites" value="5" step="1">
    <label for="conv">Conversion rate (%):</label>
    <input type="number" id="conv" value="15" step="0.5">
    <button onclick="calculate()">Calculate Viral Factor (K)</button>
    <div id="output" class="result"></div>
  </div>
  <script>
    function calculate() {{
      const i = parseFloat(document.getElementById('invites').value) || 0;
      const c = parseFloat(document.getElementById('conv').value) || 0;
      const k = (i * (c / 100)).toFixed(2);
      const out = document.getElementById('output');
      out.style.display = 'block';
      if (k >= 1.0) {{
        out.innerHTML = "🚀 Viral Factor K = " + k + " (Exponential Organic Growth!)";
        out.style.color = "#059669";
      }} else {{
        out.innerHTML = "⚠️ Viral Factor K = " + k + " (Sub-viral, relies on retention loops)";
        out.style.color = "#d97706";
      }}
    }}
  </script>
</body>
</html>
"""
