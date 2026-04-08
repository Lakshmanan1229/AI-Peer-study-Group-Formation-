"""NLP utilities for student goal embeddings.

Uses sentence-transformers (all-MiniLM-L6-v2).
The model is lazy-loaded on first call to avoid import-time overhead.
"""
from __future__ import annotations

import logging
from typing import List

import numpy as np

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]

        from app.config import settings

        model_name = settings.SENTENCE_TRANSFORMER_MODEL
        _model = SentenceTransformer(model_name)
        logger.info("Loaded sentence-transformer model: %s", model_name)
    return _model


def generate_goal_embedding(goal_text: str) -> List[float]:
    """Return a 384-dim L2-normalised embedding for *goal_text*.

    Args:
        goal_text: free-form student goals / interests string.

    Returns:
        List of 384 floats representing the normalised embedding.
    """
    model = _get_model()
    embedding: np.ndarray = model.encode(goal_text, normalize_embeddings=True)
    return embedding.tolist()


def compute_goal_similarity(
    embedding1: List[float],
    embedding2: List[float],
) -> float:
    """Cosine similarity between two pre-computed goal embeddings.

    Args:
        embedding1: list of floats (384 dimensions).
        embedding2: list of floats (384 dimensions).

    Returns:
        Cosine similarity in [-1, 1].  Returns 0.0 when either vector is zero.
    """
    a = np.array(embedding1, dtype=np.float32)
    b = np.array(embedding2, dtype=np.float32)
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def batch_generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate L2-normalised embeddings for a batch of goal texts.

    Args:
        texts: list of goal strings.

    Returns:
        List of 384-dim float lists, one per input text.
    """
    if not texts:
        return []
    model = _get_model()
    embeddings: np.ndarray = model.encode(
        texts, normalize_embeddings=True, batch_size=64, show_progress_bar=False
    )
    return [emb.tolist() for emb in embeddings]
