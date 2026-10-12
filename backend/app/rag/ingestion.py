"""
Transcript Ingestion Pipeline
Scans the transcripts directory, parses frontmatter and metadata,
generates semantic chunks, and populates the vector store index.
"""

import os
import json
import glob
from typing import Dict, Any, List, Optional
import numpy as np
from app.core.config import settings
from app.core.logging import logger, log_event
from app.rag.chunker import parse_frontmatter_and_body, chunk_transcript
from app.rag.vector_store import get_vector_store


def load_index_catalog(transcripts_dir: str) -> Dict[str, Dict[str, Any]]:
    """Loads index.json catalog if available to enrich metadata."""
    catalog_path = os.path.join(transcripts_dir, "index.json")
    catalog_map = {}
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                podcasts = data.get("podcasts", [])
                for item in podcasts:
                    fname = os.path.basename(item.get("filename", ""))
                    doc_id = os.path.splitext(fname)[0]
                    catalog_map[doc_id] = item
        except Exception as e:
            logger.warning(f"Could not load index.json catalog: {e}")
    return catalog_map


def run_ingestion(transcripts_dir: Optional[str] = None) -> int:
    """Ingests all markdown transcripts into the vector store."""
    target_dir = transcripts_dir or settings.TRANSCRIPTS_DATA_DIR
    logger.info(f"Starting transcript ingestion from {target_dir}")

    if not os.path.exists(target_dir):
        logger.error(f"Transcripts directory {target_dir} does not exist.")
        return 0

    catalog = load_index_catalog(target_dir)
    md_files = glob.glob(os.path.join(target_dir, "*.md"))

    all_chunks: List[Dict[str, Any]] = []
    processed_docs = 0

    for file_path in md_files:
        base_name = os.path.basename(file_path)
        if base_name.lower() in ["license.md", "readme.md"]:
            continue

        doc_id = os.path.splitext(base_name)[0]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            fm_meta, body = parse_frontmatter_and_body(content)

            # Merge with catalog if available
            if doc_id in catalog:
                cat_info = catalog[doc_id]
                for k, v in cat_info.items():
                    if k not in fm_meta or not fm_meta[k]:
                        fm_meta[k] = v

            chunks = chunk_transcript(
                doc_id=doc_id,
                metadata=fm_meta,
                body=body,
                chunk_word_size=400,
                overlap_words=60,
            )

            all_chunks.extend(chunks)
            processed_docs += 1

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

    logger.info(f"Processed {processed_docs} transcripts, generated {len(all_chunks)} chunks.")

    # Re-index
    store = get_vector_store()
    # Reset store if running fresh ingestion
    store.chunks = []
    store.vectors = np.empty((0, 512), dtype=np.float32)
    store.add_documents(all_chunks)

    log_event("ingestion_completed", documents=processed_docs, total_chunks=len(all_chunks))
    return len(all_chunks)


if __name__ == "__main__":
    count = run_ingestion()
    print(f"Ingestion finished successfully. Indexed {count} transcript chunks.")
