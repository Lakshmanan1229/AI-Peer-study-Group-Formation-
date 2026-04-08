"""Centralized model loader with joblib caching.

Provides ``load_model`` / ``save_model`` helpers so backend ML modules can
load a pre-trained artifact from disk (or S3) rather than re-computing on
every startup.

Model directory structure (relative to ``ML_MODELS_DIR``):
    clustering/
        scaler.pkl
        pca.pkl
        kmeans.pkl
    recommender/
        svd_model.pkl
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Optional

import joblib

logger = logging.getLogger(__name__)

# Default path – can be overridden via the ``ML_MODELS_DIR`` env-var.
_DEFAULT_MODELS_DIR = os.getenv("ML_MODELS_DIR", "ml_training/models")

_cache: dict[str, Any] = {}


def _models_dir() -> Path:
    return Path(_DEFAULT_MODELS_DIR)


def save_model(name: str, obj: Any, subdir: str = "") -> Path:
    """Persist *obj* with joblib under ``<models_dir>/<subdir>/<name>.pkl``.

    Returns the written path.
    """
    folder = _models_dir() / subdir
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.pkl"
    joblib.dump(obj, path)
    logger.info("Saved model %s to %s", name, path)
    return path


def load_model(name: str, subdir: str = "") -> Optional[Any]:
    """Load a joblib-serialised model from disk.

    Returns ``None`` if the file is missing (caller should fall back to
    on-the-fly computation).
    """
    cache_key = f"{subdir}/{name}"
    if cache_key in _cache:
        return _cache[cache_key]

    path = _models_dir() / subdir / f"{name}.pkl"
    if not path.exists():
        logger.debug("Model file %s not found – will compute on-the-fly.", path)
        return None
    try:
        obj = joblib.load(path)
        _cache[cache_key] = obj
        logger.info("Loaded model %s from %s", name, path)
        return obj
    except Exception:
        logger.exception("Failed to load model %s from %s", name, path)
        return None


def clear_cache() -> None:
    """Flush the in-memory model cache (useful in tests)."""
    _cache.clear()
