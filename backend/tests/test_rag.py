"""
Tests for Transcript Ingestion, Semantic Retrieval, and Source Citations
"""

import pytest
from app.rag.chunker import parse_frontmatter_and_body, chunk_transcript
from app.rag.retriever import retrieve_context
from app.rag.vector_store import get_vector_store


def test_chunker_parsing():
    sample_text = """---
title: "Testing Elena Episode"
guest: "Elena Verna"
date: "2025-10-01"
post_url: "https://lennysnewsletter.com/p/test-ep"
---
**Lenny Rachitsky**: Welcome to the show.
**Elena Verna**: Growth is about creating word-of-mouth loops rather than micro-optimization.
"""
    meta, body = parse_frontmatter_and_body(sample_text)
    assert meta["title"] == "Testing Elena Episode"
    assert meta["guest"] == "Elena Verna"
    assert "Growth is about creating" in body

    chunks = chunk_transcript(
        doc_id="test-doc",
        metadata=meta,
        body=body,
        chunk_word_size=20,
        overlap_words=5
    )
    assert len(chunks) >= 1
    assert chunks[0]["title"] == "Testing Elena Episode"
    assert chunks[0]["guest"] == "Elena Verna"
    assert chunks[0]["url"] == "https://lennysnewsletter.com/p/test-ep"


def test_retriever_grounded_citations():
    # Test real query over indexed dataset
    citations, context = retrieve_context("Elena Verna growth and Lovable", top_k=3)
    assert len(citations) > 0
    assert "Elena" in citations[0].title or "Elena" in citations[0].guest or "Lovable" in citations[0].excerpt
    assert citations[0].url.startswith("http") or citations[0].url == ""
    assert len(citations[0].excerpt) > 20
    assert "CONTEXT FROM LENNY'S PODCAST" not in context  # context is clean raw blocks


def test_empty_retrieval_handling():
    # Query with nonsensical terms
    citations, context = retrieve_context("xyz987qwp_unrelated_gibberish_12345", threshold=0.8)
    assert len(citations) == 0
    assert context == ""


def test_retriever_rejects_off_topic_question():
    # No accidental n-gram/feature-hash collision should turn an unrelated
    # question into a transcript citation.
    citations, context = retrieve_context(
        "how to bake chocolate cake in a toaster oven",
        top_k=4,
        threshold=0.20,
    )
    assert citations == []
    assert context == ""
