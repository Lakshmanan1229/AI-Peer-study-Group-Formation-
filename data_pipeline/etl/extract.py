"""Data extraction functions for the AI Peer Study Group Formation pipeline."""

import csv
import json
import random
import string
from datetime import datetime, timedelta

import pandas as pd


REQUIRED_COLUMNS = ["student_id", "name", "email", "department", "cgpa"]
VALID_DEPARTMENTS = ["CSE", "IT", "ECE"]


def extract_from_csv(file_path: str) -> pd.DataFrame:
    """Read CSV file containing student data and return as DataFrame."""
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def extract_from_json(file_path: str) -> list[dict]:
    """Read JSON file containing student records and return as list of dicts."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        # Handle both {"students": [...]} and direct list formats
        return data.get("students", list(data.values())[0] if data else [])
    return data


def extract_from_mock_lms_api(num_students: int = 100) -> list[dict]:
    """Generate mock LMS data including grades, attendance, and course enrollments."""
    departments = VALID_DEPARTMENTS
    courses = [
        "DSA", "OOP", "DBMS", "OS", "Networks",
        "Mathematics", "Physics", "English", "Machine Learning", "Web Development",
    ]
    learning_paces = ["slow", "moderate", "fast"]
    study_times = ["morning", "afternoon", "evening", "night"]
    goals = ["exam_prep", "project_work", "concept_learning", "skill_building"]

    students = []
    for i in range(1, num_students + 1):
        dept = random.choice(departments)
        cgpa = round(random.uniform(4.0, 10.0), 2)
        num_courses = random.randint(3, 7)
        enrolled_courses = random.sample(courses, num_courses)

        grades = {}
        for course in enrolled_courses:
            grades[course] = round(random.uniform(4.0, 10.0), 1)

        attendance = round(random.uniform(50.0, 100.0), 1)
        last_active = datetime.now() - timedelta(days=random.randint(0, 30))

        student = {
            "student_id": f"LMS{dept}{i:04d}",
            "name": f"Student {i}",
            "email": f"student{i}@college.edu",
            "department": dept,
            "semester": random.randint(1, 8),
            "cgpa": cgpa,
            "attendance_percentage": attendance,
            "enrolled_courses": enrolled_courses,
            "grades": grades,
            "learning_pace": random.choice(learning_paces),
            "preferred_study_time": random.choice(study_times),
            "study_goal": random.choice(goals),
            "last_active": last_active.isoformat(),
            "lms_source": "mock_lms",
        }
        students.append(student)
    return students


def extract_from_google_forms(responses: list[dict]) -> list[dict]:
    """Parse Google Forms survey responses containing skill self-assessments."""
    field_mapping = {
        "Timestamp": "submission_timestamp",
        "Email Address": "email",
        "Full Name": "name",
        "Student ID": "student_id",
        "Department": "department",
        "Semester": "semester",
        "CGPA": "cgpa",
        "Preferred Study Time": "preferred_study_time",
        "Learning Pace": "learning_pace",
        "Study Goal": "study_goal",
    }

    skill_keywords = [
        "dsa", "oop", "dbms", "os", "networks",
        "mathematics", "physics", "english", "machine learning", "web development",
    ]

    parsed = []
    for response in responses:
        record: dict = {}
        skills: dict = {}

        for raw_key, value in response.items():
            normalized_key = raw_key.strip()
            mapped_key = field_mapping.get(normalized_key)
            if mapped_key:
                record[mapped_key] = value
            else:
                lower_key = normalized_key.lower()
                for skill in skill_keywords:
                    if skill in lower_key:
                        try:
                            skills[skill.replace(" ", "_")] = float(value)
                        except (ValueError, TypeError):
                            skills[skill.replace(" ", "_")] = None
                        break

        record["skills"] = skills
        record["source"] = "google_forms"
        parsed.append(record)
    return parsed


def validate_extraction(data: pd.DataFrame) -> tuple[bool, list[str]]:
    """Validate extracted DataFrame for required columns, null IDs, and department values."""
    errors: list[str] = []

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    if "student_id" in data.columns:
        null_ids = data["student_id"].isnull().sum()
        if null_ids > 0:
            errors.append(f"Found {null_ids} rows with null student_id")

    if "department" in data.columns:
        invalid_depts = data[~data["department"].isin(VALID_DEPARTMENTS)]["department"].unique()
        if len(invalid_depts) > 0:
            errors.append(f"Invalid department values: {list(invalid_depts)}")

    if "cgpa" in data.columns:
        out_of_range = data[(data["cgpa"] < 0) | (data["cgpa"] > 10)].shape[0]
        if out_of_range > 0:
            errors.append(f"Found {out_of_range} rows with CGPA out of range [0, 10]")

    is_valid = len(errors) == 0
    return is_valid, errors
