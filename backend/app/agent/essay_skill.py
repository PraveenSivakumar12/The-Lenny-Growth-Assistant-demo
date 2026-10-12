"""
Ship 30 for 30 Essay Skill Engine
Transforms podcast transcript knowledge into structured, high-retention ~1,250-word essays
following the Ship 30 for 30 principles (1-3-1 hook cadence, skimmable subheadings,
bold emphasis, tactical lists, golden takeaway).
"""

from typing import List, Dict, Any, Optional, Tuple
from app.core.logging import logger, log_event
from app.rag.retriever import retrieve_context
from app.models.schemas import SourceCitation
from app.providers.base import BaseLLMProvider
from app.agent.prompts import SHIP30_ESSAY_PROMPT


async def generate_ship30_essay(
    topic: str,
    provider: BaseLLMProvider,
    target_words: int = 1250,
    conversation_context: Optional[str] = None,
    model: Optional[str] = None
) -> Tuple[str, str, List[SourceCitation], Dict[str, Any]]:
    """
    Generates a full Ship 30 for 30 essay grounded in podcast knowledge.

    Returns:
        title: Extracted or generated title
        essay_content: Full Markdown text
        citations: List of SourceCitation objects used
        metadata: Word count, model used, sections count
    """
    # 1. Retrieve supporting transcript material
    citations, context_text = retrieve_context(query=topic, top_k=6, threshold=0.18)

    # Refuse to invent an essay when the knowledge base has no supporting evidence.
    if not citations or not context_text:
        raise ValueError(
            "The transcript archive did not return sufficient supporting evidence for this essay topic."
        )

    # 2. Build system and user prompts
    system_prompt = SHIP30_ESSAY_PROMPT + f"\n\nCONTEXT FROM LENNY'S PODCAST TRANSCRIPTS:\n{context_text}"

    user_instructions = (
        f"Write a comprehensive Ship 30 for 30 essay on the following topic:\n\n"
        f"TOPIC: {topic}\n\n"
        f"TARGET WORD COUNT: Exactly approximately {target_words} words (minimum 1,000 words).\n"
        f"Remember to include:\n"
        f"- Clear, curiosity-inducing Headline\n"
        f"- 1-3-1 Hook & Lead\n"
        f"- 3-5 Subsections with skimmable H2 headings\n"
        f"- Selective bolding for the first 2-3 words of key lines\n"
        f"- Actionable bullet lists\n"
        f"- Specific guest attribution (from provided context)\n"
        f"- Golden Takeaway at the end."
    )

    if conversation_context:
        user_instructions += f"\n\nADDITIONAL CONVERSATION BACKGROUND:\n{conversation_context}"

    messages = [{"role": "user", "content": user_instructions}]

    # 3. Call Model Provider
    try:
        response = await provider.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            temperature=0.7,
            max_tokens=3500
        )
        raw_text = response.content
    except Exception as e:
        logger.error(f"Error generating essay from provider {provider.provider_name}: {e}")
        # Never substitute generic, unsupported claims for a grounded essay.
        raise RuntimeError(
            "Essay generation failed because the selected model provider is unavailable. "
            "Please retry when the provider is available."
        ) from e

    # Extract title
    title = f"The Product Growth Playbook: {topic.title()}"
    lines = raw_text.strip().splitlines()
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break

    words = raw_text.split()
    word_count = len(words)

    metadata = {
        "word_count": word_count,
        "target_words": target_words,
        "model_used": model or provider.default_model,
        "provider": provider.provider_name,
        "source_count": len(citations),
    }

    log_event("essay_generated", topic=topic, word_count=word_count, citations=len(citations))
    return title, raw_text, citations, metadata
