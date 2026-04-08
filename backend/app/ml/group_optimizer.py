"""Group optimizer for the AI Peer Study Group Formation system.

Composite score weights:
  skill_complementarity : 0.35
  schedule_overlap      : 0.25
  goal_similarity       : 0.25
  pace_compatibility    : 0.15
"""
from __future__ import annotations

import itertools
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_WEIGHT_SKILL = 0.35
_WEIGHT_SCHEDULE = 0.25
_WEIGHT_GOAL = 0.25
_WEIGHT_PACE = 0.15

_PACE_ORDER: Dict[str, int] = {"slow": 0, "moderate": 1, "fast": 2}
_MIN_OVERLAP_SLOTS = 2   # groups must share at least this many slots
_SLOTS_TOTAL = 21         # 7 days × 3 slots

# ──────────────────────────────────────────────────────────────────────────────
# Low-level helpers
# ──────────────────────────────────────────────────────────────────────────────


def compute_schedule_overlap(students: List[Dict[str, Any]]) -> int:
    """Return number of slots where at least 2 students are simultaneously available."""
    if len(students) < 2:
        return 0

    slot_counts = np.zeros(_SLOTS_TOTAL, dtype=np.int32)
    for s in students:
        for av in s.get("availability", []):
            if not av.get("is_available", False):
                continue
            day = int(av.get("day_of_week", -1))
            slot_name = str(av.get("slot", "")).lower()
            slot_idx_map = {"morning": 0, "afternoon": 1, "evening": 2}
            if 0 <= day < 7 and slot_name in slot_idx_map:
                slot_counts[day * 3 + slot_idx_map[slot_name]] += 1

    return int((slot_counts >= 2).sum())


def compute_skill_diversity(students: List[Dict[str, Any]]) -> float:
    """Return a 0-1 diversity score based on variance of skill self-ratings."""
    if len(students) < 2:
        return 0.0

    from app.ml.feature_engineering import SUBJECTS

    all_ratings: List[float] = []
    subj_upper = [s.upper() for s in SUBJECTS]

    # Per-subject std across group members
    per_subject_stds: List[float] = []
    for subj in subj_upper:
        ratings = []
        for student in students:
            for sk in student.get("skills", []):
                if str(sk.get("subject", "")).upper().strip() == subj:
                    ratings.append(float(sk.get("self_rating") or 0) / 10.0)
                    break
            else:
                ratings.append(0.0)
        if ratings:
            per_subject_stds.append(float(np.std(ratings)))
            all_ratings.extend(ratings)

    if not per_subject_stds:
        return 0.0

    # Normalise: max possible std ≈ 0.5 (binary 0/1 split)
    diversity = min(float(np.mean(per_subject_stds)) / 0.5, 1.0)
    return diversity


def compute_goal_alignment(students: List[Dict[str, Any]]) -> float:
    """Return average pairwise cosine similarity of goal embeddings (0-1).

    Students without embeddings are excluded.  Returns 0.5 (neutral) when
    fewer than 2 embeddings are present.
    """
    embeddings = [
        np.array(s["goal_embedding"], dtype=np.float32)
        for s in students
        if s.get("goal_embedding") and len(s["goal_embedding"]) == 384
    ]
    if len(embeddings) < 2:
        return 0.5

    sims: List[float] = []
    for a, b in itertools.combinations(embeddings, 2):
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a > 0 and norm_b > 0:
            sims.append(float(np.dot(a, b) / (norm_a * norm_b)))

    if not sims:
        return 0.5

    # Convert cosine similarity [-1,1] → [0,1]
    return (float(np.mean(sims)) + 1.0) / 2.0


def _compute_pace_compatibility(students: List[Dict[str, Any]]) -> float:
    """Return 1.0 if all paces the same, lower if divergent."""
    if len(students) < 2:
        return 1.0
    paces = {str(s.get("learning_pace", "moderate")).lower() for s in students}
    if len(paces) == 1:
        return 1.0
    if len(paces) == 2:
        return 0.6
    return 0.2  # all three paces in one group


# ──────────────────────────────────────────────────────────────────────────────
# Main scoring
# ──────────────────────────────────────────────────────────────────────────────


def complementary_score(students: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute composite group quality score.

    Args:
        students: list of student dicts, each containing ``skills``,
            ``availability``, ``goal_embedding``, ``learning_pace``.

    Returns:
        Dict with keys ``skill_complementarity``, ``schedule_overlap``,
        ``goal_similarity``, ``pace_compatibility``, ``total_score``.
    """
    skill = compute_skill_diversity(students)
    overlap_count = compute_schedule_overlap(students)
    # Normalise: diminishing returns beyond 10 shared slots
    schedule = min(overlap_count / 10.0, 1.0)
    goal = compute_goal_alignment(students)
    pace = _compute_pace_compatibility(students)

    total = (
        _WEIGHT_SKILL * skill
        + _WEIGHT_SCHEDULE * schedule
        + _WEIGHT_GOAL * goal
        + _WEIGHT_PACE * pace
    )
    return {
        "skill_complementarity": round(skill, 4),
        "schedule_overlap": round(schedule, 4),
        "goal_similarity": round(goal, 4),
        "pace_compatibility": round(pace, 4),
        "total_score": round(total, 4),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Group formation
# ──────────────────────────────────────────────────────────────────────────────


def _greedy_form_groups(
    cluster_students: List[Dict[str, Any]],
    min_size: int,
    max_size: int,
) -> List[List[str]]:
    """Greedy group formation within a single cluster.

    Start with a random seed student, then iteratively add the candidate that
    maximises the composite score.  Ensure at least ``_MIN_OVERLAP_SLOTS``
    shared availability slots exist before sealing a group.
    """
    rng = np.random.default_rng(seed=42)
    students = list(cluster_students)
    rng.shuffle(students)

    groups: List[List[str]] = []
    remaining = list(students)

    while remaining:
        if len(remaining) < min_size:
            # Merge leftovers into the last group
            if groups:
                groups[-1].extend([str(s.get("id", "")) for s in remaining])
            else:
                groups.append([str(s.get("id", "")) for s in remaining])
            break

        # Seed with the first available student
        group = [remaining.pop(0)]

        while len(group) < max_size and remaining:
            best_idx: Optional[int] = None
            best_score = -1.0

            for idx, candidate in enumerate(remaining):
                trial = group + [candidate]
                scores = complementary_score(trial)
                if scores["total_score"] > best_score:
                    best_score = scores["total_score"]
                    best_idx = idx

            if best_idx is None:
                break

            group.append(remaining.pop(best_idx))

            # Stop if group has min_size and meets schedule constraint
            if len(group) >= min_size:
                overlap = compute_schedule_overlap(group)
                if overlap >= _MIN_OVERLAP_SLOTS or len(remaining) == 0:
                    break

        groups.append([str(s.get("id", "")) for s in group])

    return groups


def form_groups(
    students_data: List[Dict[str, Any]],
    cluster_labels: np.ndarray,
    feature_matrix: np.ndarray,
    min_size: int = 4,
    max_size: int = 6,
) -> List[List[str]]:
    """Form study groups within each cluster using a greedy optimiser.

    Args:
        students_data: full list of student dicts (same order as ``cluster_labels``).
        cluster_labels: integer cluster-label array from :mod:`clustering`.
        feature_matrix: feature matrix (currently unused; reserved for future
            centroid-distance tie-breaking).
        min_size: minimum students per group (default 4).
        max_size: maximum students per group (default 6).

    Returns:
        List of groups; each group is a list of ``id`` strings.
    """
    if not students_data or len(cluster_labels) == 0:
        return []

    # Partition students by cluster
    clusters: Dict[int, List[Dict[str, Any]]] = {}
    for idx, label in enumerate(cluster_labels):
        clusters.setdefault(int(label), []).append(students_data[idx])

    groups: List[List[str]] = []
    for cluster_students in clusters.values():
        cluster_groups = _greedy_form_groups(cluster_students, min_size, max_size)
        groups.extend(cluster_groups)

    return groups
