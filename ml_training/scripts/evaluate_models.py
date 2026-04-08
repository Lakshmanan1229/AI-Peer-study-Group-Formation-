"""
Evaluate trained ML models on key performance metrics.

Metrics:
  - Silhouette Score: cluster quality (target > 0.30)
  - Complementary Index: avg skill std within groups normalized (target > 0.40)
  - Schedule Feasibility Rate: % groups with >= 2 overlapping slots (target > 0.80)

Usage:
    python ml_training/scripts/evaluate_models.py \
        --data data_pipeline/data/students.json \
        --models ml_training/models/
"""
import argparse
import json
import os
import sys
import numpy as np
import joblib
from sklearn.metrics import silhouette_score

# Allow importing train_clustering helper
sys.path.insert(0, os.path.dirname(__file__))
from train_clustering import build_simple_features


def form_simple_groups(student_ids: list, labels: np.ndarray, min_size: int = 4, max_size: int = 6) -> list:
    clusters: dict = {}
    for sid, lbl in zip(student_ids, labels):
        clusters.setdefault(int(lbl), []).append(sid)
    groups = []
    for members in clusters.values():
        for i in range(0, len(members), max_size):
            chunk = members[i : i + max_size]
            if len(chunk) >= min_size:
                groups.append(chunk)
            elif groups:
                groups[-1].extend(chunk)
    return groups


def complementary_index(groups: list, students_dict: dict) -> float:
    variances = []
    for group_ids in groups:
        group = [students_dict[sid] for sid in group_ids if sid in students_dict]
        if len(group) < 2:
            continue
        skill_matrix = [
            [sk["self_rating"] for sk in s.get("skills", [])] for s in group if s.get("skills")
        ]
        if len(skill_matrix) > 1:
            arr = np.array(skill_matrix)
            variances.append(float(np.std(arr, axis=0).mean()))
    return float(np.mean(variances) / 10.0) if variances else 0.0


def schedule_feasibility(groups: list, students_dict: dict) -> float:
    feasible = 0
    for group_ids in groups:
        group = [students_dict[sid] for sid in group_ids if sid in students_dict]
        slot_counts: dict = {}
        for s in group:
            for a in s.get("availability", []):
                if a.get("is_available", False):
                    key = (a["day_of_week"], a["slot"])
                    slot_counts[key] = slot_counts.get(key, 0) + 1
        if sum(1 for c in slot_counts.values() if c >= 2) >= 2:
            feasible += 1
    return feasible / len(groups) if groups else 0.0


def evaluate_models(data_path: str, models_dir: str) -> None:
    print(f"Loading data from {data_path}...")
    with open(data_path) as f:
        students = json.load(f)
    students_dict = {s["id"]: s for s in students}

    labels_path = os.path.join(models_dir, "cluster_labels.npy")
    scaler_path = os.path.join(models_dir, "scaler.pkl")

    if not os.path.exists(labels_path) or not os.path.exists(scaler_path):
        print("No trained models found. Run train_clustering.py first.")
        return

    labels = np.load(labels_path)
    scaler = joblib.load(scaler_path)
    X = build_simple_features(students)
    X_scaled = scaler.transform(X)

    sil = silhouette_score(X_scaled, labels)
    groups = form_simple_groups([s["id"] for s in students], labels)
    comp = complementary_index(groups, students_dict)
    feas = schedule_feasibility(groups, students_dict)

    print("\n=== Model Evaluation Report ===")
    print(f"1. Silhouette Score:        {sil:.4f}  (target > 0.30) {'✓' if sil > 0.30 else '✗'}")
    print(f"2. Complementary Index:     {comp:.4f}  (target > 0.40) {'✓' if comp > 0.40 else '✗'}")
    print(f"3. Schedule Feasibility:    {feas:.4f}  (target > 0.80) {'✓' if feas > 0.80 else '✗'}")
    print(f"\nTotal students: {len(students)}")
    print(f"Groups formed:  {len(groups)}")
    print(f"Avg group size: {np.mean([len(g) for g in groups]):.1f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate trained ML models")
    parser.add_argument("--data", default="data_pipeline/data/students.json")
    parser.add_argument("--models", default="ml_training/models/")
    args = parser.parse_args()
    evaluate_models(args.data, args.models)
