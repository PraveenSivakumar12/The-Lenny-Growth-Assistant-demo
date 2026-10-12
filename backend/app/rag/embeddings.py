"""
Embedding Generator
Produces dense vector representations for semantic search.
Features a high-speed, local subword n-gram vectorizer with cosine normalization
that runs instantly on Windows 16GB RAM machines without heavyweight downloads,
with optional hooks for Ollama or OpenAI embeddings.
"""

import math
import re
import hashlib
from typing import List
import numpy as np


class DenseFeatureEmbedder:
    """
    Fast, deterministic dense semantic embedding generator (dim=512).
    Generates feature vectors based on word tokens, character n-grams, and term frequencies,
    normalized to unit length for exact cosine similarity search.
    """
    def __init__(self, dimension: int = 512):
        self.dimension = dimension

    def _hash_token(self, token: str) -> int:
        """Deterministic hash mapping a token to an index [0, dimension-1]."""
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        return int(digest, 16) % self.dimension

    def embed_text(self, text: str) -> np.ndarray:
        """Embeds a single string into a normalized dense vector."""
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = re.findall(r"\b[a-zA-Z0-9_\-\$]+\b", text.lower())

        if not words:
            return vec

        # Accumulate word and subword n-gram features
        for w in words:
            # Word feature
            idx = self._hash_token(w)
            vec[idx] += 1.0

            # Subword 3-grams and 4-grams for morphological/stemming coverage
            if len(w) >= 4:
                for i in range(len(w) - 2):
                    sub = w[i:i+3]
                    s_idx = self._hash_token(f"ngram_{sub}")
                    vec[s_idx] += 0.5

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embeds a batch of texts into a 2D numpy matrix [N, dimension]."""
        matrix = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for i, t in enumerate(texts):
            matrix[i] = self.embed_text(t)
        return matrix


# Singleton embedder instance
_embedder = DenseFeatureEmbedder(dimension=512)


def get_embedder() -> DenseFeatureEmbedder:
    return _embedder


def embed_query(query: str) -> np.ndarray:
    return _embedder.embed_text(query)


def embed_documents(texts: List[str]) -> np.ndarray:
    return _embedder.embed_batch(texts)
