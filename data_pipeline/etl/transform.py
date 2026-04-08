"""Data transformation functions for the AI Peer Study Group Formation pipeline."""

from datetime import datetime

import numpy as np
import pandas as pd


DEPARTMENT_ENCODING = {"CSE": 0, "IT": 1, "ECE": 2}
LEARNING_PACE_ENCODING = {"slow": 0, "moderate": 1, "fast": 2}
CRITICAL_FIELDS = ["student_id", "email", "department"]


def clean_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """Fill numeric nulls with median, categorical with mode; drop rows missing critical fields."""
    df = df.copy()

    df = df.dropna(subset=CRITICAL_FIELDS)

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    for col in categorical_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])

    return df


def normalize_grades(df: pd.DataFrame) -> pd.DataFrame:
    """Convert various grade systems to a 10-point scale."""
    df = df.copy()

    letter_to_10 = {
        "O": 10.0, "A+": 9.5, "A": 9.0, "B+": 8.5, "B": 8.0,
        "C+": 7.5, "C": 7.0, "D": 6.0, "F": 0.0,
    }

    if "cgpa" in df.columns:
        if df["cgpa"].dtype == object:
            df["cgpa"] = df["cgpa"].map(letter_to_10).fillna(df["cgpa"])
            df["cgpa"] = pd.to_numeric(df["cgpa"], errors="coerce")

        max_val = df["cgpa"].max()
        if max_val <= 4.0:
            # 4-point GPA scale -> 10-point
            df["cgpa"] = df["cgpa"] * 2.5
        elif max_val <= 10.0:
            pass  # already 10-point
        elif max_val <= 100.0:
            # Percentage -> 10-point
            df["cgpa"] = df["cgpa"] / 10.0

        df["cgpa"] = df["cgpa"].clip(0.0, 10.0)

    skill_cols = [c for c in df.columns if c.startswith("skill_")]
    for col in skill_cols:
        if df[col].dtype in [np.float64, np.int64]:
            max_val = df[col].max()
            if max_val <= 5.0:
                df[col] = df[col] * 2.0
            elif max_val <= 100.0 and max_val > 10.0:
                df[col] = df[col] / 10.0
            df[col] = df[col].clip(0.0, 10.0)

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Encode department (CSE=0, IT=1, ECE=2) and learning_pace (slow=0, moderate=1, fast=2)."""
    df = df.copy()

    if "department" in df.columns:
        df["department_encoded"] = df["department"].map(DEPARTMENT_ENCODING)

    if "learning_pace" in df.columns:
        df["learning_pace_encoded"] = df["learning_pace"].map(LEARNING_PACE_ENCODING)

    if "preferred_study_time" in df.columns:
        study_time_dummies = pd.get_dummies(
            df["preferred_study_time"], prefix="study_time"
        )
        df = pd.concat([df, study_time_dummies], axis=1)

    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate students by email, keeping the most recent record."""
    df = df.copy()

    if "email" not in df.columns:
        return df

    if "last_active" in df.columns:
        df["last_active"] = pd.to_datetime(df["last_active"], errors="coerce")
        df = df.sort_values("last_active", ascending=False)
    elif "submission_timestamp" in df.columns:
        df["submission_timestamp"] = pd.to_datetime(
            df["submission_timestamp"], errors="coerce"
        )
        df = df.sort_values("submission_timestamp", ascending=False)

    df = df.drop_duplicates(subset=["email"], keep="first")
    df = df.reset_index(drop=True)
    return df


def validate_schema(df: pd.DataFrame, required_cols: list[str]) -> bool:
    """Check that all required columns are present in the DataFrame."""
    return all(col in df.columns for col in required_cols)


def build_student_record(raw_data: dict) -> dict:
    """Transform raw survey/LMS data into a standard student record format."""
    skills = raw_data.get("skills", {})
    if not isinstance(skills, dict):
        skills = {}

    grades = raw_data.get("grades", {})
    if isinstance(grades, dict):
        for subject, grade in grades.items():
            key = f"skill_{subject.lower().replace(' ', '_')}"
            if key not in skills or skills[key] is None:
                skills[key] = grade

    record = {
        "student_id": raw_data.get("student_id", ""),
        "name": raw_data.get("name", ""),
        "email": raw_data.get("email", ""),
        "department": raw_data.get("department", ""),
        "semester": int(raw_data.get("semester", 1)),
        "cgpa": float(raw_data.get("cgpa", 0.0)),
        "learning_pace": raw_data.get("learning_pace", "moderate"),
        "preferred_study_time": raw_data.get("preferred_study_time", "evening"),
        "study_goal": raw_data.get("study_goal", "concept_learning"),
        "attendance_percentage": float(raw_data.get("attendance_percentage", 75.0)),
        "skills": skills,
        "available_slots": raw_data.get("available_slots", []),
        "source": raw_data.get("source", raw_data.get("lms_source", "unknown")),
        "created_at": datetime.utcnow().isoformat(),
    }
    return record
