"""Initial tables

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension for goal_embedding column
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ------------------------------------------------------------------
    # students
    # ------------------------------------------------------------------
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(1024), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "department",
            sa.Enum("CSE", "IT", "ECE", name="department_enum"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("cgpa", sa.Float, nullable=False),
        sa.Column(
            "learning_pace",
            sa.Enum("slow", "moderate", "fast", name="learning_pace_enum"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("student", "admin", "faculty", name="role_enum"),
            nullable=False,
            server_default="student",
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("goals", sa.String(2000), nullable=True),
        # pgvector column — raw DDL because SQLAlchemy core has no native Vector type
        sa.Column(
            "goal_embedding",
            sa.Text,  # placeholder; overwritten by raw ALTER below
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    # Replace placeholder TEXT column with actual vector(384) type
    op.execute("ALTER TABLE students ALTER COLUMN goal_embedding TYPE vector(384) USING NULL")

    op.create_index("ix_students_id", "students", ["id"])
    op.create_index("ix_students_email", "students", ["email"], unique=True)

    # ------------------------------------------------------------------
    # skill_assessments
    # ------------------------------------------------------------------
    op.create_table(
        "skill_assessments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("self_rating", sa.Integer, nullable=False),
        sa.Column("peer_rating", sa.Float, nullable=True),
        sa.Column("grade_points", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_skill_assessments_student_id", "skill_assessments", ["student_id"])

    # ------------------------------------------------------------------
    # availability_slots
    # ------------------------------------------------------------------
    op.create_table(
        "availability_slots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column(
            "slot",
            sa.Enum("morning", "afternoon", "evening", name="slot_enum"),
            nullable=False,
        ),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_index("ix_availability_slots_student_id", "availability_slots", ["student_id"])

    # ------------------------------------------------------------------
    # study_groups
    # ------------------------------------------------------------------
    op.create_table(
        "study_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("department", sa.String(10), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "inactive", "disbanded", name="group_status_enum"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("max_size", sa.Integer, nullable=False, server_default="6"),
        sa.Column("complementary_score", sa.Float, nullable=True),
        sa.Column("schedule_overlap_count", sa.Integer, nullable=True),
        sa.Column("goal_similarity_score", sa.Float, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_study_groups_id", "study_groups", ["id"])

    # ------------------------------------------------------------------
    # group_memberships
    # ------------------------------------------------------------------
    op.create_table(
        "group_memberships",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("study_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("member", "leader", name="member_role_enum"),
            nullable=False,
            server_default="member",
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_group_memberships_group_id", "group_memberships", ["group_id"])
    op.create_index("ix_group_memberships_student_id", "group_memberships", ["student_id"])

    # ------------------------------------------------------------------
    # group_sessions
    # ------------------------------------------------------------------
    op.create_table(
        "group_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("study_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column(
            "session_type",
            sa.Enum("online", "offline", name="session_type_enum"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("attendance", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_group_sessions_id", "group_sessions", ["id"])
    op.create_index("ix_group_sessions_group_id", "group_sessions", ["group_id"])

    # ------------------------------------------------------------------
    # peer_feedbacks
    # ------------------------------------------------------------------
    op.create_table(
        "peer_feedbacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "reviewer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "reviewee_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("students.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("study_groups.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("group_sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("helpfulness_score", sa.Integer, nullable=False),
        sa.Column("comment", sa.Text, nullable=True),
        sa.Column("is_anonymous", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_peer_feedbacks_id", "peer_feedbacks", ["id"])
    op.create_index("ix_peer_feedbacks_reviewer_id", "peer_feedbacks", ["reviewer_id"])
    op.create_index("ix_peer_feedbacks_reviewee_id", "peer_feedbacks", ["reviewee_id"])
    op.create_index("ix_peer_feedbacks_group_id", "peer_feedbacks", ["group_id"])
    op.create_index("ix_peer_feedbacks_session_id", "peer_feedbacks", ["session_id"])


def downgrade() -> None:
    op.drop_table("peer_feedbacks")
    op.drop_table("group_sessions")
    op.drop_table("group_memberships")
    op.drop_table("study_groups")
    op.drop_table("availability_slots")
    op.drop_table("skill_assessments")
    op.drop_table("students")

    op.execute("DROP TYPE IF EXISTS session_type_enum")
    op.execute("DROP TYPE IF EXISTS member_role_enum")
    op.execute("DROP TYPE IF EXISTS group_status_enum")
    op.execute("DROP TYPE IF EXISTS slot_enum")
    op.execute("DROP TYPE IF EXISTS role_enum")
    op.execute("DROP TYPE IF EXISTS learning_pace_enum")
    op.execute("DROP TYPE IF EXISTS department_enum")
