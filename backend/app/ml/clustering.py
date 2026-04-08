from __future__ import annotations

from typing import Optional

import numpy as np


def cluster_students(
    feature_matrix: np.ndarray,
    n_clusters: Optional[int] = None,
) -> np.ndarray:
    """Cluster students using K-Means on the pre-built feature matrix.

    Args:
        feature_matrix: array of shape ``(n_students, n_features)`` produced
            by :func:`feature_engineering.build_feature_matrix`.
        n_clusters: target number of clusters.  If *None*, auto-determined as
            ``max(1, n_students // 4)`` to aim for groups of ~4.

    Returns:
        Integer cluster-label array of shape ``(n_students,)``.
    """
    n_students = feature_matrix.shape[0]

    if n_students == 0:
        return np.array([], dtype=np.int32)

    if n_students <= 3:
        return np.zeros(n_students, dtype=np.int32)

    if n_clusters is None:
        n_clusters = max(1, n_students // 4)

    n_clusters = min(n_clusters, n_students)

    from sklearn.cluster import KMeans  # type: ignore[import]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import]

    scaler = StandardScaler()
    normalised = scaler.fit_transform(feature_matrix)

    kmeans = KMeans(
        n_clusters=n_clusters,
        n_init=10,
        max_iter=300,
        random_state=42,
    )
    labels: np.ndarray = kmeans.fit_predict(normalised)
    return labels.astype(np.int32)
