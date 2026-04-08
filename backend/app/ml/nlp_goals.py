from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore[import]

        from app.config import settings

        _model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        logger.info(
            "Loaded sentence-transformer model: %s",
            settings.SENTENCE_TRANSFORMER_MODEL,
        )
    return _model


def generate_goal_embedding(goals_text: str) -> List[float]:
    """Return a 384-dim normalised embedding for the supplied goals text."""
    model = _get_model()
    embedding = model.encode(goals_text, normalize_embeddings=True)
    return embedding.tolist()
