from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

_DAYS = 7
_SLOTS = 3  # morning=0, afternoon=1, evening=2
_DEPARTMENTS = ["CSE", "IT", "ECE"]
_PACES = ["slow", "moderate", "fast"]


def build_feature_matrix(students_data: List[Dict[str, Any]]) -> np.ndarray:
    """Build a normalised numeric feature matrix from student data dicts.

    Each row represents one student with the following feature groups:

    * Skill self-ratings  (one column per distinct subject, normalised 0–1)
    * Availability slots  (21 binary columns: 7 days × 3 time-slots)
    * Department one-hot  (3 columns)
    * Year                (1 column, normalised 0–1 over range 1–4)
    * CGPA                (1 column, normalised 0–1 over range 0–10)
    * Learning pace one-hot (3 columns)

    Args:
        students_data: list of dicts, each containing:
            ``student_id``, ``department``, ``year``, ``cgpa``,
            ``learning_pace``, ``subjects`` (dict subject→rating),
            ``availability`` (dict (day_int, slot_str) → bool).

    Returns:
        np.ndarray of shape ``(n_students, n_features)``.
    """
    if not students_data:
        return np.empty((0, 0), dtype=np.float32)

    all_subjects: List[str] = sorted(
        {subj for s in students_data for subj in s.get("subjects", {}).keys()}
    )

    n_skill = len(all_subjects)
    n_avail = _DAYS * _SLOTS
    n_dept = len(_DEPARTMENTS)
    n_pace = len(_PACES)
    n_features = n_skill + n_avail + n_dept + 1 + 1 + n_pace

    matrix = np.zeros((len(students_data), n_features), dtype=np.float32)

    for i, student in enumerate(students_data):
        col = 0

        # --- Skill ratings (normalised 0–1, original scale 1–10) ---
        subjects: Dict[str, float] = student.get("subjects", {})
        for subj in all_subjects:
            matrix[i, col] = subjects.get(subj, 0) / 10.0
            col += 1

        # --- Availability slots (binary) ---
        availability: Dict = student.get("availability", {})
        for day in range(_DAYS):
            for slot_idx, slot_name in enumerate(["morning", "afternoon", "evening"]):
                matrix[i, col] = float(
                    availability.get((day, slot_name), False)
                )
                col += 1

        # --- Department one-hot ---
        dept = student.get("department", "")
        if dept in _DEPARTMENTS:
            matrix[i, col + _DEPARTMENTS.index(dept)] = 1.0
        col += n_dept

        # --- Year (normalised 1–4 → 0–1) ---
        matrix[i, col] = (student.get("year", 1) - 1) / 3.0
        col += 1

        # --- CGPA (normalised 0–10 → 0–1) ---
        matrix[i, col] = student.get("cgpa", 5.0) / 10.0
        col += 1

        # --- Learning pace one-hot ---
        pace = student.get("learning_pace", "moderate")
        if pace in _PACES:
            matrix[i, col + _PACES.index(pace)] = 1.0
        # col not incremented further; kept in step with other blocks for clarity

    return matrix
