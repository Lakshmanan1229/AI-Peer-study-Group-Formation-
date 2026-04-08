"""
Train content-based and collaborative filtering recommendation models.

Usage:
    python ml_training/scripts/train_recommender.py \
        --data data_pipeline/data/students.json \
        --output ml_training/models/
"""
import argparse
import json
import os
import numpy as np
import joblib
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

SUBJECTS = [
    "DSA", "OOP", "DBMS", "OS", "Networks",
    "Mathematics", "Physics", "English", "Machine Learning", "Web Development",
]
SUBJECT_TO_IDX = {s: i for i, s in enumerate(SUBJECTS)}


def build_interaction_matrix(students: list) -> np.ndarray:
    n = len(students)
    matrix = np.zeros((n, len(SUBJECTS)))
    for i, student in enumerate(students):
        for skill in student.get("skills", []):
            j = SUBJECT_TO_IDX.get(skill["subject"])
            if j is not None:
                matrix[i, j] = skill["self_rating"]
    return matrix


def train_collaborative_filter(matrix: np.ndarray, n_factors: int = 10):
    n_factors = min(n_factors, min(matrix.shape) - 1)
    U, sigma, Vt = svds(csr_matrix(matrix), k=n_factors)
    predicted = np.dot(np.dot(U, np.diag(sigma)), Vt)
    return U, sigma, Vt, predicted


def evaluate_precision_at_k(actual: np.ndarray, predicted: np.ndarray, top_k: int = 5) -> float:
    precisions = []
    for i in range(min(200, actual.shape[0])):
        weak = np.where(actual[i] < 5)[0]
        if len(weak) == 0:
            continue
        test_idx = set(weak[: max(1, len(weak) // 5)])
        top_recs = set(np.argsort(-predicted[i])[:top_k])
        precisions.append(len(test_idx & top_recs) / top_k)
    return float(np.mean(precisions)) if precisions else 0.0


def train_recommender(data_path: str, output_dir: str) -> dict:
    print(f"Loading data from {data_path}...")
    with open(data_path) as f:
        students = json.load(f)
    print(f"Loaded {len(students)} students")

    matrix = build_interaction_matrix(students)
    print(f"Interaction matrix shape: {matrix.shape}")

    U, sigma, Vt, predicted = train_collaborative_filter(matrix, n_factors=10)
    precision = evaluate_precision_at_k(matrix, predicted, top_k=5)
    print(f"Precision@5: {precision:.4f}")

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(
        {"U": U, "sigma": sigma, "Vt": Vt, "subjects": SUBJECTS},
        os.path.join(output_dir, "recommender_model.pkl"),
    )
    with open(os.path.join(output_dir, "recommender_metadata.json"), "w") as f:
        json.dump(
            {"student_ids": [s["id"] for s in students], "subjects": SUBJECTS, "n_factors": 10},
            f,
        )

    print(f"\n=== Recommender Training Complete ===")
    print(f"Precision@5: {precision:.4f}")
    print(f"Models saved to: {output_dir}")
    return {"precision_at_5": precision, "n_students": len(students)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train recommendation models")
    parser.add_argument("--data", default="data_pipeline/data/students.json")
    parser.add_argument("--output", default="ml_training/models/")
    args = parser.parse_args()
    train_recommender(args.data, args.output)
