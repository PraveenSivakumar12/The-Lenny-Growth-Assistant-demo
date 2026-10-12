"""
Transcript Chunker
Parses Lenny's Podcast transcripts with YAML frontmatter, cleans speaker cues,
and splits text into semantically cohesive, overlapping chunks with metadata.
"""

import re
from typing import List, Dict, Any, Tuple


def parse_frontmatter_and_body(content: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML frontmatter metadata and remaining body content."""
    metadata: Dict[str, Any] = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = parts[1]
            body = parts[2]
            for line in raw_fm.strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    metadata[key] = val

    return metadata, body.strip()


def clean_transcript_text(text: str) -> str:
    """Normalizes whitespace and removes excessive markdown artifacts while preserving speaker cues."""
    # Collapse multiple blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", text)
    return cleaned.strip()


def chunk_transcript(
    doc_id: str,
    metadata: Dict[str, Any],
    body: str,
    chunk_word_size: int = 450,
    overlap_words: int = 75,
) -> List[Dict[str, Any]]:
    """
    Splits transcript body into chunks of ~450 words with 75 words overlap.
    Preserves document title, guest, publication date, post URL, and chunk index.
    """
    # Clean text
    clean_body = clean_transcript_text(body)
    words = clean_body.split()

    if not words:
        return []

    chunks = []
    chunk_index = 0
    start = 0

    title = metadata.get("title", doc_id.replace("-", " ").title())
    guest = metadata.get("guest", "")
    date = metadata.get("date", "")
    url = metadata.get("post_url", "")

    while start < len(words):
        end = min(start + chunk_word_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunk_id = f"{doc_id}_chunk_{chunk_index}"
        chunks.append({
            "chunk_id": chunk_id,
            "doc_id": doc_id,
            "title": title,
            "guest": guest,
            "date": date,
            "url": url,
            "text": chunk_text,
            "word_count": len(chunk_words),
            "chunk_index": chunk_index,
        })

        chunk_index += 1
        if end >= len(words):
            break
        start += chunk_word_size - overlap_words

    return chunks
