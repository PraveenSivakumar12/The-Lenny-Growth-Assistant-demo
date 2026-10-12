"""
Semantic Context Retriever
Queries the vector store, formats retrieved chunks with provenance metadata,
and constructs grounding context blocks for prompt injection.
"""

from typing import List, Tuple
from app.core.config import settings
from app.core.logging import logger, log_event
from app.models.schemas import SourceCitation
from app.rag.vector_store import get_vector_store


def retrieve_context(
    query: str,
    top_k: int = 4,
    threshold: float = 0.20
) -> Tuple[List[SourceCitation], str]:
    """
    Retrieves the most semantically relevant transcript chunks for a query.
    Returns:
        citations: List of SourceCitation objects with verifiable metadata.
        context_str: Formatted context block for the LLM system prompt.
    """
    store = get_vector_store()
    results = store.search(query=query, top_k=top_k, threshold=threshold)

    if not results:
        log_event("retrieval_empty", query=query)
        return [], ""

    citations: List[SourceCitation] = []
    context_blocks: List[str] = []

    for chunk, score in results:
        title = chunk.get("title", "Lenny's Podcast")
        guest = chunk.get("guest", "Podcast Guest")
        date = chunk.get("date", "")
        url = chunk.get("url", "")
        text = chunk.get("text", "")

        citations.append(
            SourceCitation(
                title=title,
                guest=guest,
                date=date,
                url=url,
                excerpt=text[:320] + "..." if len(text) > 320 else text,
                score=round(score, 4),
            )
        )

        block = (
            f"--- SOURCE: {title} (Guest: {guest}, Date: {date}) ---\n"
            f"URL: {url}\n"
            f"EXCERPT:\n{text}\n"
        )
        context_blocks.append(block)

    formatted_context = "\n\n".join(context_blocks)
    log_event("retrieval_success", query=query, retrieved_chunks=len(citations), top_score=citations[0].score)

    return citations, formatted_context
