"""KMeans + DBSCAN hybrid clustering for student grouping.

Pipeline:
  1. StandardScaler – normalise features
  2. PCA – reduce to 20 components (speeds up DBSCAN)
  3. KMeans (k=8) – find archetypal clusters
  4. DBSCAN (eps=0.5, min_samples=3) – detect outliers on PCA features
  5. Outliers (label=-1) re-assigned to nearest KMeans centroid
"""
from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np


def cluster_students(
    feature_matrix: np.ndarray,
    n_clusters: int = 8,
) -> np.ndarray:
    """Cluster students using a KMeans + DBSCAN hybrid.

    Args:
        feature_matrix: ``(n_students, n_features)`` float array.
        n_clusters: number of KMeans clusters (default 8).

    Returns:
        Integer cluster-label array of shape ``(n_students,)``.
        Every student receives a non-negative label.
    """
    n_students = feature_matrix.shape[0]

    if n_students == 0:
        return np.array([], dtype=np.int32)

    if n_students <= 3:
        return np.zeros(n_students, dtype=np.int32)

    from sklearn.cluster import DBSCAN, KMeans  # type: ignore[import]
    from sklearn.decomposition import PCA  # type: ignore[import]
    from sklearn.preprocessing import StandardScaler  # type: ignore[import]

    # 1. Normalise
    scaler = StandardScaler()
    scaled = scaler.fit_transform(feature_matrix)

    # 2. PCA (cap components to available rank)
    n_components = min(20, n_students - 1, scaled.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    pca_features = pca.fit_transform(scaled)

    # 3. KMeans
    k = min(n_clusters, n_students)
    kmeans = KMeans(n_clusters=k, n_init=10, max_iter=300, random_state=42)
    kmeans_labels: np.ndarray = kmeans.fit_predict(scaled)

    # 4. DBSCAN on PCA features to find outliers
    dbscan = DBSCAN(eps=0.5, min_samples=3, n_jobs=-1)
    dbscan_labels: np.ndarray = dbscan.fit_predict(pca_features)

    # 5. Reassign outliers to nearest KMeans centroid
    final_labels = kmeans_labels.copy()
    outlier_mask = dbscan_labels == -1
    if outlier_mask.any():
        # Transform outlier rows to the same scaled space used by KMeans
        centroids_pca = pca.transform(kmeans.cluster_centers_)
        outlier_pca = pca_features[outlier_mask]
        # Euclidean distance from each outlier to each centroid
        diffs = outlier_pca[:, np.newaxis, :] - centroids_pca[np.newaxis, :, :]  # (O, k, d)
        distances = np.linalg.norm(diffs, axis=2)  # (O, k)
        nearest = np.argmin(distances, axis=1)
        final_labels[outlier_mask] = nearest

    return final_labels.astype(np.int32)


def get_silhouette_score(
    feature_matrix: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Return the silhouette coefficient for the given clustering.

    Returns ``0.0`` when the score cannot be computed (e.g. all one cluster).
    """
    unique = np.unique(labels)
    if len(unique) < 2 or feature_matrix.shape[0] < 2:
        return 0.0
    try:
        from sklearn.metrics import silhouette_score  # type: ignore[import]
        from sklearn.preprocessing import StandardScaler  # type: ignore[import]

        scaled = StandardScaler().fit_transform(feature_matrix)
        return float(silhouette_score(scaled, labels))
    except Exception:
        return 0.0


def get_cluster_summary(
    feature_matrix: np.ndarray,
    labels: np.ndarray,
    student_ids: List[str],
) -> Dict[int, Dict]:
    """Return a summary dict keyed by cluster label.

    Each value contains:
    * ``student_ids`` – list of ids in this cluster
    * ``size`` – number of students
    * ``centroid_mean`` – mean of all feature means within the cluster
    * ``centroid_std`` – mean of all feature stds within the cluster
    """
    summary: Dict[int, Dict] = {}
    for label in np.unique(labels):
        mask = labels == label
        ids = [student_ids[i] for i, m in enumerate(mask) if m]
        sub_matrix = feature_matrix[mask]
        summary[int(label)] = {
            "student_ids": ids,
            "size": len(ids),
            "centroid_mean": float(sub_matrix.mean()),
            "centroid_std": float(sub_matrix.std()),
        }
    return summary
