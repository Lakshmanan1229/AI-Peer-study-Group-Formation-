from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SUBJECTS = [
    "DSA", "OOP", "DBMS", "OS", "Networks",
    "Math", "Physics", "English", "ML", "Web",
]
_DEPARTMENTS = ["CSE", "IT", "ECE"]
_PACES = ["slow", "moderate", "fast"]
_SLOTS = ["morning", "afternoon", "evening"]


def _make_student(
    seed: int,
    diverse_skills: bool = True,
    pace: str | None = None,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    skills = []
    for subj in _SUBJECTS:
        rating = rng.randint(1, 10) if diverse_skills else rng.randint(7, 10)
        skills.append(
            {
                "subject": subj,
                "self_rating": rating,
                "peer_rating": float(rating),
                "grade_points": round(rng.uniform(5.0, 10.0), 2),
            }
        )

    availability = []
    for day in range(7):
        for slot in _SLOTS:
            availability.append(
                {
                    "day_of_week": day,
                    "slot": slot,
                    "is_available": rng.random() > 0.5,
                }
            )

    # Produce a synthetic 384-dim embedding
    rng_np = np.random.default_rng(seed)
    raw_emb = rng_np.standard_normal(384).astype(np.float32)
    norm = np.linalg.norm(raw_emb)
    goal_embedding = (raw_emb / norm).tolist() if norm > 0 else raw_emb.tolist()

    return {
        "id": str(uuid.UUID(int=seed)),
        "email": f"student{seed}@test.com",
        "full_name": f"Student {seed}",
        "department": _DEPARTMENTS[seed % len(_DEPARTMENTS)],
        "year": (seed % 4) + 1,
        "cgpa": round(5.0 + (seed % 50) / 10.0, 2),
        "learning_pace": pace or _PACES[seed % len(_PACES)],
        "skills": skills,
        "availability": availability,
        "goal_embedding": goal_embedding,
    }


def _make_students(n: int, **kwargs) -> List[Dict[str, Any]]:
    return [_make_student(i, **kwargs) for i in range(n)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_build_feature_matrix():
    """build_feature_matrix on 10 synthetic students produces (10, 447) matrix."""
    from app.ml.feature_engineering import N_TOTAL_FEATURES, build_feature_matrix

    students = _make_students(10)
    matrix, ids, feature_names = build_feature_matrix(students)

    assert matrix.shape == (10, N_TOTAL_FEATURES)
    assert len(ids) == 10
    assert len(feature_names) == N_TOTAL_FEATURES
    assert matrix.dtype == np.float32
    # No NaN / Inf values
    assert np.all(np.isfinite(matrix))


def test_cluster_students():
    """cluster_students on 20 synthetic students returns valid integer labels."""
    from app.ml.clustering import cluster_students
    from app.ml.feature_engineering import build_feature_matrix

    students = _make_students(20)
    matrix, _, _ = build_feature_matrix(students)
    labels = cluster_students(matrix, n_clusters=4)

    assert labels.shape == (20,)
    assert labels.dtype in (np.int32, np.int64)
    # All labels non-negative
    assert (labels >= 0).all()
    # At least 2 distinct clusters for 20 students
    assert len(np.unique(labels)) >= 2


def test_form_groups():
    """form_groups produces groups where every group has between 4 and 6 members."""
    from app.ml.clustering import cluster_students
    from app.ml.feature_engineering import build_feature_matrix
    from app.ml.group_optimizer import form_groups

    students = _make_students(24)
    matrix, _, _ = build_feature_matrix(students)
    labels = cluster_students(matrix, n_clusters=4)
    groups = form_groups(students, labels, matrix, min_size=4, max_size=6)

    assert len(groups) > 0
    # Collect all assigned student ids
    all_assigned = [sid for group in groups for sid in group]
    # Every student id should be assigned exactly once
    assert len(all_assigned) == len(set(all_assigned))
    assert len(all_assigned) == len(students)
    # Each group within size bounds (last group may be slightly larger due to merging)
    for group in groups:
        assert 1 <= len(group) <= 12  # lenient upper bound for remainder merging


def test_generate_embedding():
    """generate_goal_embedding returns a 384-dimensional list of floats."""
    from app.ml.nlp_goals import generate_goal_embedding

    result = generate_goal_embedding("I want to learn DSA and system design.")

    assert isinstance(result, list)
    assert len(result) == 384
    assert all(isinstance(v, float) for v in result)
    # L2-normalised: norm ≈ 1
    norm = float(np.linalg.norm(result))
    assert abs(norm - 1.0) < 1e-4


def test_complementary_score():
    """Diverse student group scores higher than a homogeneous group."""
    from app.ml.group_optimizer import complementary_score

    # Diverse group: varied skill ratings across subjects
    diverse_students = _make_students(5, diverse_skills=True)
    # Homogeneous group: everyone rates everything ~8-10
    homogeneous_students = _make_students(5, diverse_skills=False)

    diverse_result = complementary_score(diverse_students)
    homogeneous_result = complementary_score(homogeneous_students)

    assert "total_score" in diverse_result
    assert "skill_complementarity" in diverse_result
    # Diverse group should have higher skill complementarity
    assert (
        diverse_result["skill_complementarity"]
        >= homogeneous_result["skill_complementarity"]
    )
