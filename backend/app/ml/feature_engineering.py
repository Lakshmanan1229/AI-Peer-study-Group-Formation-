"""Feature engineering for the AI Peer Study Group Formation system.

Builds a 447-element numeric feature vector per student:
  - 30  subject-skill features  (10 subjects × 3: self_rating, peer_rating, grade_points)
  - 5   skill statistics        (mean, std, min, max, range of self-ratings)
  - 2   academic scalars        (cgpa 0-1, year 0-1)
  - 1   learning pace scalar    (slow=0, moderate=0.5, fast=1.0)
  - 3   department one-hot      (is_cse, is_it, is_ece)
  - 21  availability bitmap     (7 days × 3 slots, each 0/1)
  - 1   availability summary    (total_available_slots normalised)
  - 384 goal embedding          (sentence-transformer dimensions)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

SUBJECTS: List[str] = [
    "DSA", "OOP", "DBMS", "OS", "Networks",
    "Math", "Physics", "English", "ML", "Web",
]

_DEPARTMENTS: List[str] = ["CSE", "IT", "ECE"]
_SLOTS: List[str] = ["morning", "afternoon", "evening"]
_DAYS: int = 7
_PACE_MAP: Dict[str, float] = {"slow": 0.0, "moderate": 0.5, "fast": 1.0}

GOAL_DIM: int = 384
N_BASE_FEATURES: int = 30 + 5 + 2 + 1 + 3 + 21 + 1   # 63
N_TOTAL_FEATURES: int = N_BASE_FEATURES + GOAL_DIM      # 447


def _build_feature_names() -> List[str]:
    names: List[str] = []
    for subj in SUBJECTS:
        names.extend([f"{subj}_self_rating", f"{subj}_peer_rating", f"{subj}_grade_points"])
    names += ["mean_skill", "std_skill", "min_skill", "max_skill", "skill_range"]
    names += ["cgpa", "year", "learning_pace"]
    names += [f"is_{d.lower()}" for d in _DEPARTMENTS]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for d in range(_DAYS):
        for slot in _SLOTS:
            names.append(f"avail_{day_names[d]}_{slot}")
    names.append("total_avail_slots")
    names += [f"goal_emb_{k}" for k in range(GOAL_DIM)]
    return names


FEATURE_NAMES: List[str] = _build_feature_names()


def _extract_skill_features(skills: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
    skill_30 = np.zeros(len(SUBJECTS) * 3, dtype=np.float32)
    lookup: Dict[str, Dict[str, float]] = {}
    for sk in skills:
        key = str(sk.get("subject", "")).upper().strip()
        lookup[key] = {
            "self_rating": float(sk.get("self_rating") or 0),
            "peer_rating": float(sk.get("peer_rating") or 0),
            "grade_points": float(sk.get("grade_points") or 0),
        }

    raw_self: List[float] = []
    for idx, subj in enumerate(SUBJECTS):
        entry = lookup.get(subj.upper(), {})
        sr = min(max(entry.get("self_rating", 0) / 10.0, 0.0), 1.0)
        pr = min(max(entry.get("peer_rating", 0) / 10.0, 0.0), 1.0)
        gp = min(max(entry.get("grade_points", 0) / 10.0, 0.0), 1.0)
        base = idx * 3
        skill_30[base], skill_30[base + 1], skill_30[base + 2] = sr, pr, gp
        raw_self.append(sr)

    arr = np.array(raw_self, dtype=np.float32)
    stats_5 = np.array(
        [arr.mean(), arr.std(), arr.min(), arr.max(), arr.max() - arr.min()],
        dtype=np.float32,
    )
    return skill_30, stats_5


def _extract_availability_features(
    availability: List[Dict[str, Any]],
) -> Tuple[np.ndarray, float]:
    bitmap = np.zeros(_DAYS * len(_SLOTS), dtype=np.float32)
    for slot in availability:
        day = int(slot.get("day_of_week", -1))
        slot_name = str(slot.get("slot", "")).lower()
        if 0 <= day < _DAYS and slot_name in _SLOTS and slot.get("is_available", False):
            bitmap[day * len(_SLOTS) + _SLOTS.index(slot_name)] = 1.0
    return bitmap, float(bitmap.sum()) / (_DAYS * len(_SLOTS))


def build_feature_matrix(
    students_data: List[Dict[str, Any]],
) -> Tuple[np.ndarray, List[str], List[str]]:
    """Build the numeric feature matrix for all students.

    Args:
        students_data: list of dicts with keys:
            ``id``, ``cgpa``, ``year``, ``learning_pace``, ``department``,
            ``skills`` (list of ``{subject, self_rating, peer_rating, grade_points}``),
            ``availability`` (list of ``{day_of_week, slot, is_available}``),
            ``goal_embedding`` (list[float] 384-dim or None).

    Returns:
        Tuple of (feature_matrix, student_ids, feature_names).
        ``feature_matrix`` shape: ``(n_students, 447)``.
    """
    if not students_data:
        return np.empty((0, N_TOTAL_FEATURES), dtype=np.float32), [], FEATURE_NAMES

    n = len(students_data)
    matrix = np.zeros((n, N_TOTAL_FEATURES), dtype=np.float32)
    student_ids: List[str] = []

    for i, student in enumerate(students_data):
        student_ids.append(str(student.get("id", i)))
        col = 0

        # 30 skill features + 5 stats
        skill_30, stats_5 = _extract_skill_features(student.get("skills", []))
        matrix[i, col:col + 30] = skill_30
        col += 30
        matrix[i, col:col + 5] = stats_5
        col += 5

        # CGPA
        matrix[i, col] = min(max(float(student.get("cgpa", 5.0)) / 10.0, 0.0), 1.0)
        col += 1

        # Year (1-4 → 0-1)
        matrix[i, col] = (min(max(int(student.get("year", 1)), 1), 4) - 1) / 3.0
        col += 1

        # Learning pace
        pace = str(student.get("learning_pace", "moderate")).lower()
        matrix[i, col] = _PACE_MAP.get(pace, 0.5)
        col += 1

        # Department one-hot
        dept = str(student.get("department", "")).upper()
        if dept in _DEPARTMENTS:
            matrix[i, col + _DEPARTMENTS.index(dept)] = 1.0
        col += len(_DEPARTMENTS)

        # Availability bitmap (21) + summary (1)
        bitmap, total_norm = _extract_availability_features(student.get("availability", []))
        matrix[i, col:col + _DAYS * len(_SLOTS)] = bitmap
        col += _DAYS * len(_SLOTS)
        matrix[i, col] = total_norm
        col += 1

        # Goal embedding (384)
        goal_emb: Optional[List[float]] = student.get("goal_embedding")
        if goal_emb and len(goal_emb) == GOAL_DIM:
            matrix[i, col:col + GOAL_DIM] = np.array(goal_emb, dtype=np.float32)

    return matrix, student_ids, FEATURE_NAMES
