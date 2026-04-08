"""
End-to-end clustering training script for SMVEC Peer Study Group Formation.

Usage:
    python ml_training/scripts/train_clustering.py \
        --data data_pipeline/data/students.json \
        --output ml_training/models/
"""
import argparse
import json
import os
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import euclidean_distances


def build_simple_features(students: list) -> np.ndarray:
    """Build feature matrix without heavy NLP dependencies."""
    subjects = [
        "DSA", "OOP", "DBMS", "OS", "Networks",
        "Mathematics", "Physics", "English", "Machine Learning", "Web Development",
    ]
    rows = []
    for s in students:
        row = []
        row.append(s.get("cgpa", 7.0) / 10.0)
        row.append(s.get("year", 2) / 4.0)
        pace_map = {"slow": 0.0, "moderate": 0.5, "fast": 1.0}
        row.append(pace_map.get(s.get("learning_pace", "moderate"), 0.5))
        dept_map = {"CSE": [1, 0, 0], "IT": [0, 1, 0], "ECE": [0, 0, 1]}
        row.extend(dept_map.get(s.get("department", "CSE"), [0, 0, 0]))
        skills_dict = {sk["subject"]: sk["self_rating"] / 10.0 for sk in s.get("skills", [])}
        for subj in subjects:
            row.append(skills_dict.get(subj, 0.5))
        avail_count = sum(1 for a in s.get("availability", []) if a.get("is_available", False))
        row.append(avail_count / 21.0)
        rows.append(row)
    return np.array(rows, dtype=float)


def train_clustering(data_path: str, output_dir: str) -> dict:
    print(f"Loading data from {data_path}...")
    with open(data_path) as f:
        students = json.load(f)
    print(f"Loaded {len(students)} students")

    X = build_simple_features(students)
    student_ids = [s["id"] for s in students]
    print(f"Feature matrix shape: {X.shape}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    n_components = min(20, X.shape[1], X.shape[0] - 1)
    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    print(f"PCA explained variance: {pca.explained_variance_ratio_.sum():.3f}")

    kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
    kmeans_labels = kmeans.fit_predict(X_scaled)

    dbscan = DBSCAN(eps=0.5, min_samples=3)
    dbscan_labels = dbscan.fit_predict(X_pca)
    outlier_mask = dbscan_labels == -1
    print(f"DBSCAN outliers: {outlier_mask.sum()} / {len(students)}")

    final_labels = kmeans_labels.copy()
    if outlier_mask.sum() > 0:
        distances = euclidean_distances(X_scaled[outlier_mask], kmeans.cluster_centers_)
        final_labels[outlier_mask] = distances.argmin(axis=1)

    sil_score = silhouette_score(X_scaled, final_labels)
    print(f"Silhouette Score: {sil_score:.4f}")

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(scaler, os.path.join(output_dir, "scaler.pkl"))
    joblib.dump(pca, os.path.join(output_dir, "pca.pkl"))
    joblib.dump(kmeans, os.path.join(output_dir, "kmeans_model.pkl"))
    np.save(os.path.join(output_dir, "cluster_labels.npy"), final_labels)

    label_map = {sid: int(lbl) for sid, lbl in zip(student_ids, final_labels)}
    with open(os.path.join(output_dir, "student_cluster_map.json"), "w") as f:
        json.dump(label_map, f, indent=2)

    unique, counts = np.unique(final_labels, return_counts=True)
    print(f"\n=== Training Complete ===")
    print(f"Silhouette Score: {sil_score:.4f}")
    print(f"Cluster distribution: {dict(zip(unique.tolist(), counts.tolist()))}")
    print(f"Models saved to: {output_dir}")

    return {"silhouette_score": float(sil_score), "n_clusters": 8, "n_students": len(students)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train KMeans+DBSCAN clustering model")
    parser.add_argument("--data", default="data_pipeline/data/students.json")
    parser.add_argument("--output", default="ml_training/models/")
    args = parser.parse_args()
    train_clustering(args.data, args.output)
