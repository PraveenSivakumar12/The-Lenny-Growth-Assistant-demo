"""
Agent Tool Specifications and Implementations
Defines tools following standard Tool-Use schemas compatible with Anthropic Claude SDK,
OpenAI tool calling, and local model router execution.
"""

from typing import Dict, Any, List, Optional
from app.core.logging import logger, log_event
from app.rag.retriever import retrieve_context
from app.models.schemas import SourceCitation

# Tool Schemas (Anthropic / JSON Schema Standard)
PODCAST_SEARCH_TOOL = {
    "name": "search_podcast_transcripts",
    "description": "Searches Lenny's Podcast transcripts for product management, growth, PMF, retention, and startup advice.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query, topic, or guest name to retrieve transcript excerpts for."
            },
            "top_k": {
                "type": "integer",
                "description": "Number of chunks to retrieve (default: 4)",
                "default": 4
            }
        },
        "required": ["query"]
    }
}

SHIP30_ESSAY_TOOL = {
    "name": "generate_ship30_essay",
    "description": "Generates a high-retention, ~1,250-word Ship 30 for 30 atomic essay grounded in podcast knowledge.",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "Topic or core thesis of the essay."
            },
            "target_words": {
                "type": "integer",
                "description": "Target word count (around 1,250 words)",
                "default": 1250
            }
        },
        "required": ["topic"]
    }
}

ARTIFACT_GENERATION_TOOL = {
    "name": "generate_web_artifact",
    "description": "Generates an interactive HTML/CSS webpage component or a standalone Markdown document.",
    "input_schema": {
        "type": "object",
        "properties": {
            "artifact_type": {
                "type": "string",
                "enum": ["html", "markdown"],
                "description": "Type of artifact to generate: 'html' for interactive components or 'markdown' for specs."
            },
            "title": {
                "type": "string",
                "description": "Title of the artifact."
            },
            "specification": {
                "type": "string",
                "description": "Detailed description or requirements for the artifact."
            }
        },
        "required": ["artifact_type", "title", "specification"]
    }
}

ALL_AGENT_TOOLS = [PODCAST_SEARCH_TOOL, SHIP30_ESSAY_TOOL, ARTIFACT_GENERATION_TOOL]


# Execution functions
async def execute_podcast_search(query: str, top_k: int = 4) -> Dict[str, Any]:
    """Executes semantic search against podcast transcripts."""
    citations, context_text = retrieve_context(query=query, top_k=top_k)
    return {
        "citations": [c.model_dump() for c in citations],
        "context_text": context_text,
        "count": len(citations)
    }
