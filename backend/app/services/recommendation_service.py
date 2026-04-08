from __future__ import annotations

import uuid
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.student import SkillAssessment, Student

# ---------------------------------------------------------------------------
# Curated resource database
# ---------------------------------------------------------------------------
# Each entry maps to one or more subject keywords (case-insensitive prefix/suffix
# matching is applied at lookup time).

_RESOURCE_DB: List[Dict[str, Any]] = [
    # --- Data Structures & Algorithms ---
    {
        "title": "Algorithms — Khan Academy",
        "url": "https://www.khanacademy.org/computing/computer-science/algorithms",
        "type": "course",
        "subjects": ["Algorithms", "DSA", "Data Structures"],
        "base_relevance": 0.92,
    },
    {
        "title": "Algorithms Specialization — Coursera (Stanford)",
        "url": "https://www.coursera.org/specializations/algorithms",
        "type": "course",
        "subjects": ["Algorithms", "DSA", "Data Structures"],
        "base_relevance": 0.95,
    },
    {
        "title": "Introduction to Algorithms — MIT OCW (6.006)",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/",
        "type": "course",
        "subjects": ["Algorithms", "DSA", "Data Structures"],
        "base_relevance": 0.94,
    },
    {
        "title": "Data Structures — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/data-structures/",
        "type": "reference",
        "subjects": ["Data Structures", "DSA", "Algorithms"],
        "base_relevance": 0.90,
    },
    # --- Programming ---
    {
        "title": "Python for Everybody — Coursera",
        "url": "https://www.coursera.org/specializations/python",
        "type": "course",
        "subjects": ["Python", "Programming", "Software Development"],
        "base_relevance": 0.91,
    },
    {
        "title": "C Programming — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/c-programming-language/",
        "type": "reference",
        "subjects": ["C", "C++", "Programming"],
        "base_relevance": 0.88,
    },
    {
        "title": "Java Programming and Software Engineering — Coursera (Duke)",
        "url": "https://www.coursera.org/specializations/java-programming",
        "type": "course",
        "subjects": ["Java", "OOP", "Programming", "Software Engineering"],
        "base_relevance": 0.90,
    },
    # --- Mathematics ---
    {
        "title": "Linear Algebra — MIT OCW (18.06)",
        "url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
        "type": "course",
        "subjects": ["Linear Algebra", "Mathematics", "Maths"],
        "base_relevance": 0.94,
    },
    {
        "title": "Discrete Mathematics — Khan Academy",
        "url": "https://www.khanacademy.org/math/discrete-math",
        "type": "course",
        "subjects": ["Discrete Mathematics", "Discrete Maths", "Mathematics"],
        "base_relevance": 0.90,
    },
    {
        "title": "Calculus 1 — Khan Academy",
        "url": "https://www.khanacademy.org/math/calculus-1",
        "type": "course",
        "subjects": ["Calculus", "Mathematics", "Maths"],
        "base_relevance": 0.90,
    },
    # --- Computer Networks ---
    {
        "title": "The Bits and Bytes of Computer Networking — Coursera (Google)",
        "url": "https://www.coursera.org/learn/computer-networking",
        "type": "course",
        "subjects": ["Computer Networks", "Networking", "Networks"],
        "base_relevance": 0.92,
    },
    {
        "title": "Computer Networks — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/computer-network-tutorials/",
        "type": "reference",
        "subjects": ["Computer Networks", "Networking", "Networks"],
        "base_relevance": 0.88,
    },
    # --- Operating Systems ---
    {
        "title": "Operating System Engineering — MIT OCW (6.828)",
        "url": "https://ocw.mit.edu/courses/6-828-operating-system-engineering-fall-2012/",
        "type": "course",
        "subjects": ["Operating Systems", "OS"],
        "base_relevance": 0.93,
    },
    {
        "title": "Operating Systems — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/operating-systems/",
        "type": "reference",
        "subjects": ["Operating Systems", "OS"],
        "base_relevance": 0.89,
    },
    # --- DBMS ---
    {
        "title": "Intro to SQL — Khan Academy",
        "url": "https://www.khanacademy.org/computing/computer-programming/sql",
        "type": "course",
        "subjects": ["DBMS", "Database", "SQL", "Databases"],
        "base_relevance": 0.91,
    },
    {
        "title": "DBMS — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/dbms/",
        "type": "reference",
        "subjects": ["DBMS", "Database", "SQL"],
        "base_relevance": 0.88,
    },
    # --- Machine Learning / AI ---
    {
        "title": "Machine Learning Specialization — Coursera (Andrew Ng)",
        "url": "https://www.coursera.org/specializations/machine-learning-introduction",
        "type": "course",
        "subjects": ["Machine Learning", "ML", "AI", "Artificial Intelligence"],
        "base_relevance": 0.96,
    },
    {
        "title": "Deep Learning Specialization — Coursera",
        "url": "https://www.coursera.org/specializations/deep-learning",
        "type": "course",
        "subjects": ["Deep Learning", "Neural Networks", "ML", "AI"],
        "base_relevance": 0.95,
    },
    {
        "title": "Machine Learning — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/machine-learning/",
        "type": "reference",
        "subjects": ["Machine Learning", "ML"],
        "base_relevance": 0.87,
    },
    # --- Electronics / ECE ---
    {
        "title": "Circuits and Electronics — MIT OCW (6.002)",
        "url": "https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/",
        "type": "course",
        "subjects": ["Electronics", "Circuits", "ECE", "Circuit Theory"],
        "base_relevance": 0.92,
    },
    {
        "title": "Digital Electronics & Logic Design — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/digital-electronics-logic-design-tutorials/",
        "type": "reference",
        "subjects": ["Digital Electronics", "Logic Design", "ECE"],
        "base_relevance": 0.88,
    },
    # --- Software Engineering ---
    {
        "title": "Software Engineering — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/software-engineering/",
        "type": "reference",
        "subjects": ["Software Engineering", "SDLC", "Design Patterns"],
        "base_relevance": 0.87,
    },
    # --- Theory of Computation ---
    {
        "title": "Theory of Computation — MIT OCW (18.404J)",
        "url": "https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/",
        "type": "course",
        "subjects": ["Theory of Computation", "TOC", "Automata"],
        "base_relevance": 0.93,
    },
    {
        "title": "Automata Theory — GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/theory-of-computation-automata-tutorials/",
        "type": "reference",
        "subjects": ["Theory of Computation", "TOC", "Automata"],
        "base_relevance": 0.89,
    },
    # --- Computer Architecture ---
    {
        "title": "Computer Architecture — MIT OCW (6.004)",
        "url": "https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/",
        "type": "course",
        "subjects": ["Computer Architecture", "Computer Organization", "COA"],
        "base_relevance": 0.91,
    },
]


def _match_resources_for_subject(subject: str) -> List[Dict[str, Any]]:
    """Return all curated resources whose subject keywords match ``subject``."""
    subject_lower = subject.lower()
    matched: List[Dict[str, Any]] = []
    for resource in _RESOURCE_DB:
        for kw in resource["subjects"]:
            if subject_lower in kw.lower() or kw.lower() in subject_lower:
                matched.append(
                    {
                        "title": resource["title"],
                        "url": resource["url"],
                        "type": resource["type"],
                        "subject": subject,
                        "relevance_score": resource["base_relevance"],
                    }
                )
                break
    return matched


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


async def get_resource_recommendations(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[Dict[str, Any]]:
    """Return up to 10 curated study resources ranked by relevance.

    Resources are selected based on the student's weak subjects (self-rating
    < 5).  If no weak subjects exist the three lowest-rated subjects are used.
    When no skills are recorded at all, a general set of top resources is
    returned.
    """
    result = await db.execute(
        select(SkillAssessment).where(SkillAssessment.student_id == student_id)
    )
    skills: List[SkillAssessment] = list(result.scalars().all())

    if not skills:
        return [
            {
                "title": r["title"],
                "url": r["url"],
                "type": r["type"],
                "subject": r["subjects"][0],
                "relevance_score": r["base_relevance"],
            }
            for r in _RESOURCE_DB[:6]
        ]

    weak = [s for s in skills if s.self_rating < 5]
    if not weak:
        weak = sorted(skills, key=lambda x: x.self_rating)[:3]

    recommendations: List[Dict[str, Any]] = []
    seen_urls: set[str] = set()

    for skill in sorted(weak, key=lambda x: x.self_rating):
        for resource in _match_resources_for_subject(skill.subject):
            if resource["url"] in seen_urls:
                continue
            seen_urls.add(resource["url"])
            # Boost relevance score for weaker skills
            boost = (5 - skill.self_rating) / 10.0
            resource["relevance_score"] = round(
                min(1.0, resource["relevance_score"] + boost), 3
            )
            recommendations.append(resource)

    recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
    return recommendations[:10]


async def get_mentor_recommendations(
    db: AsyncSession,
    student_id: uuid.UUID,
) -> List[Dict[str, Any]]:
    """Find senior students who can mentor the current student's weak areas.

    Candidates are senior (higher year) students in the same department with
    a self-rating ≥ 7 in at least one of the student's weak subjects.  Falls
    back to same-year cross-department seniors if no department-match is found.

    Returns up to 10 candidates ranked by ``match_score``.
    """
    result = await db.execute(
        select(Student)
        .where(Student.id == student_id)
        .options(selectinload(Student.skills))
    )
    current = result.scalar_one_or_none()
    if current is None:
        return []

    # Determine weak subjects
    weak_subjects = [
        sk.subject for sk in (current.skills or []) if sk.self_rating < 5
    ]
    if not weak_subjects:
        weak_subjects = [
            sk.subject
            for sk in sorted(current.skills or [], key=lambda x: x.self_rating)[:3]
        ]
    if not weak_subjects:
        return []

    # Query senior students in same department first
    senior_result = await db.execute(
        select(Student)
        .where(
            Student.year > current.year,
            Student.department == current.department,
            Student.is_active,
            Student.id != student_id,
        )
        .options(selectinload(Student.skills))
        .limit(50)
    )
    seniors: List[Student] = list(senior_result.scalars().all())

    # Fallback: same or higher year across all departments
    if not seniors:
        fallback_result = await db.execute(
            select(Student)
            .where(
                Student.year >= current.year,
                Student.is_active,
                Student.id != student_id,
            )
            .options(selectinload(Student.skills))
            .limit(50)
        )
        seniors = list(fallback_result.scalars().all())

    candidates: List[Dict[str, Any]] = []
    for senior in seniors:
        skills_map = {sk.subject: sk.self_rating for sk in (senior.skills or [])}

        strong_in_weak: List[str] = []
        rating_sum = 0
        for subj in weak_subjects:
            rating = skills_map.get(subj, 0)
            if rating >= 7:
                strong_in_weak.append(subj)
                rating_sum += rating

        if not strong_in_weak:
            continue

        avg_skill = sum(skills_map.values()) / len(skills_map) if skills_map else 0
        match_score = round(rating_sum / (10.0 * len(weak_subjects)), 3)

        candidates.append(
            {
                "student_id": str(senior.id),
                "name": senior.full_name,
                "department": (
                    senior.department.value
                    if hasattr(senior.department, "value")
                    else str(senior.department)
                ),
                "year": senior.year,
                "strong_subjects": strong_in_weak,
                "avg_rating": round(avg_skill, 2),
                "match_score": match_score,
            }
        )

    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:10]
