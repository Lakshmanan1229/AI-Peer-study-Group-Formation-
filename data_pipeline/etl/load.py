"""Data loading functions for the AI Peer Study Group Formation pipeline."""

import json
import logging
from io import BytesIO

import pandas as pd

logger = logging.getLogger(__name__)


def load_to_postgresql(records: list[dict], db_url: str) -> dict:
    """Upsert student records into PostgreSQL using SQLAlchemy.

    Returns a dict with counts: inserted, updated, failed.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    counts = {"inserted": 0, "updated": 0, "failed": 0}
    try:
        for record in records:
            try:
                success = upsert_student(session, record)
                if success:
                    counts["inserted"] += 1
                else:
                    counts["updated"] += 1

                skills = record.get("skills", {})
                if skills and isinstance(skills, dict):
                    student_id = record.get("student_id")
                    skills_list = [
                        {"subject": k, "score": v} for k, v in skills.items()
                    ]
                    load_skills_batch(session, student_id, skills_list)
            except Exception as exc:
                logger.error("Failed to upsert record %s: %s", record.get("student_id"), exc)
                counts["failed"] += 1
                session.rollback()

        session.commit()
    finally:
        session.close()

    return counts


def save_to_s3_parquet(df: pd.DataFrame, bucket: str, key: str) -> bool:
    """Convert DataFrame to Parquet format and upload to an S3 bucket."""
    import boto3

    buffer = BytesIO()
    df.to_parquet(buffer, index=False, engine="pyarrow")
    buffer.seek(0)

    try:
        s3_client = boto3.client("s3")
        s3_client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
        logger.info("Uploaded parquet to s3://%s/%s", bucket, key)
        return True
    except Exception as exc:
        logger.error("Failed to upload to S3: %s", exc)
        return False


def upsert_student(session, student_data: dict) -> bool:
    """Insert or update a student record based on email. Returns True if inserted."""
    from sqlalchemy import text

    email = student_data.get("email")
    if not email:
        raise ValueError("student_data must contain an email field")

    check_query = text("SELECT student_id FROM students WHERE email = :email")
    result = session.execute(check_query, {"email": email}).fetchone()

    skills = student_data.get("skills", {})
    skills_json = json.dumps(skills) if isinstance(skills, dict) else "{}"

    if result is None:
        insert_query = text(
            """
            INSERT INTO students
                (student_id, name, email, department, semester, cgpa,
                 learning_pace, preferred_study_time, study_goal,
                 attendance_percentage, skills_json, created_at)
            VALUES
                (:student_id, :name, :email, :department, :semester, :cgpa,
                 :learning_pace, :preferred_study_time, :study_goal,
                 :attendance_percentage, :skills_json, NOW())
            """
        )
        session.execute(
            insert_query,
            {
                "student_id": student_data.get("student_id"),
                "name": student_data.get("name"),
                "email": email,
                "department": student_data.get("department"),
                "semester": student_data.get("semester"),
                "cgpa": student_data.get("cgpa"),
                "learning_pace": student_data.get("learning_pace"),
                "preferred_study_time": student_data.get("preferred_study_time"),
                "study_goal": student_data.get("study_goal"),
                "attendance_percentage": student_data.get("attendance_percentage"),
                "skills_json": skills_json,
            },
        )
        return True
    else:
        update_query = text(
            """
            UPDATE students SET
                name = :name,
                department = :department,
                semester = :semester,
                cgpa = :cgpa,
                learning_pace = :learning_pace,
                preferred_study_time = :preferred_study_time,
                study_goal = :study_goal,
                attendance_percentage = :attendance_percentage,
                skills_json = :skills_json,
                updated_at = NOW()
            WHERE email = :email
            """
        )
        session.execute(
            update_query,
            {
                "name": student_data.get("name"),
                "department": student_data.get("department"),
                "semester": student_data.get("semester"),
                "cgpa": student_data.get("cgpa"),
                "learning_pace": student_data.get("learning_pace"),
                "preferred_study_time": student_data.get("preferred_study_time"),
                "study_goal": student_data.get("study_goal"),
                "attendance_percentage": student_data.get("attendance_percentage"),
                "skills_json": skills_json,
                "email": email,
            },
        )
        return False


def load_skills_batch(session, student_id: str, skills: list[dict]) -> None:
    """Upsert a batch of skill records for a given student."""
    from sqlalchemy import text

    for skill in skills:
        subject = skill.get("subject", "")
        score = skill.get("score")
        if not subject or score is None:
            continue

        upsert_query = text(
            """
            INSERT INTO student_skills (student_id, subject, score, updated_at)
            VALUES (:student_id, :subject, :score, NOW())
            ON CONFLICT (student_id, subject)
            DO UPDATE SET score = EXCLUDED.score, updated_at = NOW()
            """
        )
        session.execute(
            upsert_query,
            {"student_id": student_id, "subject": subject, "score": float(score)},
        )
