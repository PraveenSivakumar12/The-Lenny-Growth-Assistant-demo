"""
Vector Store and Similarity Index
Maintains an indexed catalog of podcast transcript chunks and their dense embeddings.
Supports persistent disk storage in JSON + NumPy format and fast cosine similarity search.
"""

import json
import os
import re
import math
from collections import Counter
from typing import List, Dict, Any, Tuple, Set
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.rag.embeddings import embed_query, embed_documents


class LocalVectorStore:
    def __init__(self, index_dir: str = "./data/index"):
        self.index_dir = index_dir
        self.metadata_file = os.path.join(index_dir, "metadata.json")
        self.vectors_file = os.path.join(index_dir, "vectors.npy")

        self.chunks: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = np.empty((0, 512), dtype=np.float32)
        self._token_sets: List[Set[str]] = []
        self._document_frequency: Counter[str] = Counter()

        os.makedirs(self.index_dir, exist_ok=True)
        self.load()

    def count(self) -> int:
        return len(self.chunks)

    def load(self) -> bool:
        """Loads index from disk if files exist."""
        if os.path.exists(self.metadata_file) and os.path.exists(self.vectors_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                self.vectors = np.load(self.vectors_file)
                self._rebuild_lexical_index()
                logger.info(f"Loaded {len(self.chunks)} transcript chunks from {self.index_dir}")
                return True
            except Exception as e:
                logger.error(f"Failed to load vector index: {e}")
                return False
        return False

    def save(self) -> None:
        """Persists chunks metadata and vectors to disk."""
        os.makedirs(self.index_dir, exist_ok=True)
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        np.save(self.vectors_file, self.vectors)
        logger.info(f"Saved {len(self.chunks)} chunks to {self.index_dir}")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """Embeds and indexes a list of chunk dictionaries."""
        if not chunks:
            return

        texts = [c["text"] for c in chunks]
        new_vectors = embed_documents(texts)

        if len(self.chunks) == 0:
            self.chunks = chunks
            self.vectors = new_vectors
        else:
            self.chunks.extend(chunks)
            self.vectors = np.vstack([self.vectors, new_vectors])

        self._rebuild_lexical_index()
        self.save()

    @staticmethod
    def _tokenize(text: str) -> Set[str]:
        """Tokenize transcript content while dropping common function words."""
        stop_words = {
            "a", "an", "and", "are", "as", "at", "be", "been", "being", "but",
            "by", "can", "could", "did", "do", "does", "for", "from", "had", "has",
            "have", "he", "her", "here", "hers", "him", "his", "how", "i", "if",
            "in", "into", "is", "it", "its", "may", "me", "more", "most", "my",
            "no", "not", "of", "on", "or", "our", "ours", "she", "so", "some",
            "than", "that", "the", "their", "them", "then", "there", "these", "they",
            "this", "those", "to", "too", "us", "was", "we", "were", "what", "when",
            "where", "which", "who", "why", "will", "with", "would", "you", "your",
            "yours", "podcast", "lenny", "episode", "interview",
        }
        return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in stop_words and (len(token) > 1 or token.isdigit())}

    def _rebuild_lexical_index(self) -> None:
        """Build a small TF-IDF-style lexical index for evidence-aware retrieval.

        The persisted 512-dimensional hashed vectors are retained for reproducible
        ingestion, but retrieval also verifies real token overlap to avoid hash
        collisions surfacing unrelated transcript excerpts as evidence.
        """
        self._token_sets = []
        self._document_frequency = Counter()
        for chunk in self.chunks:
            searchable = " ".join(str(chunk.get(key, "")) for key in ("title", "guest", "text"))
            tokens = self._tokenize(searchable)
            self._token_sets.append(tokens)
            self._document_frequency.update(tokens)

    def search(
        self,
        query: str,
        top_k: int = 4,
        threshold: float = 0.20
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search transcripts using IDF-weighted real-token overlap.

        This deliberately favors explainable lexical evidence over the previous
        feature-hashing cosine score, which could return unrelated text due to
        collisions in a 512-dimensional space. Scores are normalized to [0, 1].
        """
        if not self.chunks or not self._token_sets:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        n_docs = max(len(self._token_sets), 1)
        query_weights = {
            token: math.log(1.0 + (n_docs + 1.0) / (self._document_frequency.get(token, 0) + 1.0))
            for token in query_tokens
        }
        total_weight = sum(query_weights.values()) or 1.0

        scored: List[Tuple[int, float, int]] = []
        for idx, doc_tokens in enumerate(self._token_sets):
            matched = query_tokens.intersection(doc_tokens)
            if not matched:
                continue
            # Long/multi-term questions should have at least two independent
            # evidence terms in a candidate, preventing a single accidental
            # overlap (e.g. "cake") from becoming a transcript citation.
            if len(query_tokens) >= 3 and len(matched) < 2:
                continue
            # Weighted query-term coverage penalizes candidates matching only
            # a generic subset of a question's meaningful terms.
            score = sum(query_weights[token] for token in matched) / total_weight
            if score >= threshold:
                scored.append((idx, float(score), len(matched)))

        # Deterministic tie-breaking by additional term matches, then score.
        scored.sort(key=lambda item: (item[1], item[2]), reverse=True)
        return [(self.chunks[idx], score) for idx, score, _ in scored[:top_k]]


# Global Vector Store Instance
_vector_store_instance = LocalVectorStore(index_dir=settings.VECTOR_INDEX_DIR)


def get_vector_store() -> LocalVectorStore:
    return _vector_store_instance
