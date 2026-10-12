#!/usr/bin/env python3
"""Fetch permitted transcript inputs if needed and build the local RAG index."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault("TRANSCRIPTS_DATA_DIR", str(PROJECT_ROOT / "data" / "transcripts"))
os.environ.setdefault("VECTOR_INDEX_DIR", str(PROJECT_ROOT / "data" / "index"))

from fetch_lenny_data import fetch_transcripts  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Re-download source data and rebuild the index.")
    args = parser.parse_args()

    fetch_transcripts(PROJECT_ROOT, force=args.force)

    index_dir = Path(os.environ["VECTOR_INDEX_DIR"])
    metadata_path = index_dir / "metadata.json"
    vectors_path = index_dir / "vectors.npy"
    if not args.force and metadata_path.is_file() and vectors_path.is_file():
        print(f"Using existing transcript index in {index_dir}")
        return

    # Import only after transcript data is present so the vector-store singleton
    # sees the configured directories before ingestion populates it.
    from app.rag.ingestion import run_ingestion  # noqa: E402

    chunk_count = run_ingestion()
    if chunk_count <= 0:
        raise SystemExit("Transcript ingestion created no chunks; check the source archive and logs.")
    print(f"Knowledge base ready: {chunk_count} chunks indexed.")


if __name__ == "__main__":
    main()
