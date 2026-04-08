from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

_MAX_GROUP_SIZE = 6
_MIN_GROUP_SIZE = 2


def form_groups(
    students_data: List[Dict[str, Any]],
    cluster_labels: np.ndarray,
    feature_matrix: np.ndarray,
) -> List[List[str]]:
    """Form balanced study groups from K-Means cluster assignments.

    Within each cluster the students are shuffled (with a fixed seed for
    reproducibility) and split into chunks of up to ``_MAX_GROUP_SIZE``.
    Any trailing chunk smaller than ``_MIN_GROUP_SIZE`` is merged into the
    previous group.

    Args:
        students_data: list of student dicts, each containing ``student_id``.
        cluster_labels: integer array of shape ``(n_students,)`` from
            :func:`clustering.cluster_students`.
        feature_matrix: feature array (unused here but kept in signature for
            future diversity-aware optimisation).

    Returns:
        List of groups; each group is a list of ``student_id`` strings.
    """
    if not students_data or len(cluster_labels) == 0:
        return []

    # Group student indices by cluster label
    clusters: Dict[int, List[int]] = {}
    for idx, label in enumerate(cluster_labels):
        clusters.setdefault(int(label), []).append(idx)

    rng = np.random.default_rng(seed=42)
    groups: List[List[str]] = []

    for student_indices in clusters.values():
        n = len(student_indices)
        order = rng.permutation(n)

        start = 0
        while start < n:
            end = min(start + _MAX_GROUP_SIZE, n)
            chunk_indices = [student_indices[order[j]] for j in range(start, end)]
            chunk_ids = [str(students_data[ci]["student_id"]) for ci in chunk_indices]

            if len(chunk_ids) >= _MIN_GROUP_SIZE:
                groups.append(chunk_ids)
            elif groups:
                # Merge undersized trailing chunk into the last group
                groups[-1].extend(chunk_ids)
            else:
                groups.append(chunk_ids)

            start = end

    return groups
