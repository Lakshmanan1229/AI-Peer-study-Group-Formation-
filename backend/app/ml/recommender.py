"""Content-based resource recommender and collaborative mentor filter."""
from __future__ import annotations

from typing import Any, Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# Resource catalog (30+ entries)
# ──────────────────────────────────────────────────────────────────────────────

_RESOURCES: List[Dict[str, Any]] = [
    # DSA
    {"id": "r001", "title": "Introduction to Algorithms (CLRS)", "url": "https://mitpress.mit.edu/9780262046305/",
     "type": "book", "subject": "DSA", "difficulty": "advanced",
     "tags": ["algorithms", "data structures", "complexity"]},
    {"id": "r002", "title": "NeetCode 150 – DSA Interview Prep", "url": "https://neetcode.io/",
     "type": "course", "subject": "DSA", "difficulty": "intermediate",
     "tags": ["leetcode", "interview", "graphs", "trees"]},
    {"id": "r003", "title": "Visualgo – Algorithm Visualisations", "url": "https://visualgo.net/",
     "type": "article", "subject": "DSA", "difficulty": "beginner",
     "tags": ["visualisation", "sorting", "graph"]},

    # OOP
    {"id": "r004", "title": "Design Patterns (Gang of Four)", "url": "https://www.oreilly.com/library/view/design-patterns-elements/0201633612/",
     "type": "book", "subject": "OOP", "difficulty": "advanced",
     "tags": ["design patterns", "SOLID", "architecture"]},
    {"id": "r005", "title": "Object-Oriented Programming in Python – Real Python", "url": "https://realpython.com/python3-object-oriented-programming/",
     "type": "article", "subject": "OOP", "difficulty": "beginner",
     "tags": ["python", "classes", "inheritance"]},
    {"id": "r006", "title": "Clean Code – Robert C. Martin", "url": "https://www.oreilly.com/library/view/clean-code-a/9780136083238/",
     "type": "book", "subject": "OOP", "difficulty": "intermediate",
     "tags": ["clean code", "refactoring", "best practices"]},

    # DBMS
    {"id": "r007", "title": "CMU 15-445 Database Systems (lecture videos)", "url": "https://15445.courses.cs.cmu.edu/",
     "type": "video", "subject": "DBMS", "difficulty": "advanced",
     "tags": ["SQL", "transactions", "indexing", "query optimisation"]},
    {"id": "r008", "title": "SQL Zoo – Interactive SQL Tutorials", "url": "https://sqlzoo.net/",
     "type": "course", "subject": "DBMS", "difficulty": "beginner",
     "tags": ["SQL", "queries", "joins"]},
    {"id": "r009", "title": "Use The Index, Luke!", "url": "https://use-the-index-luke.com/",
     "type": "article", "subject": "DBMS", "difficulty": "intermediate",
     "tags": ["indexing", "performance", "B-tree"]},

    # OS
    {"id": "r010", "title": "Operating Systems: Three Easy Pieces", "url": "https://pages.cs.wisc.edu/~remzi/OSTEP/",
     "type": "book", "subject": "OS", "difficulty": "intermediate",
     "tags": ["processes", "memory", "file systems", "concurrency"]},
    {"id": "r011", "title": "Neso Academy – Operating System (YouTube)", "url": "https://www.youtube.com/playlist?list=PLBlnK6fEyqRiVhbXDGLXDk_OQAeuVcp2O",
     "type": "video", "subject": "OS", "difficulty": "beginner",
     "tags": ["scheduling", "deadlock", "paging"]},
    {"id": "r012", "title": "Linux Kernel Development – Robert Love", "url": "https://www.oreilly.com/library/view/linux-kernel-development/9780768696974/",
     "type": "book", "subject": "OS", "difficulty": "advanced",
     "tags": ["linux", "kernel", "system calls"]},

    # Networks
    {"id": "r013", "title": "Computer Networking: A Top-Down Approach (Kurose & Ross)", "url": "https://gaia.cs.umass.edu/kurose_ross/",
     "type": "book", "subject": "Networks", "difficulty": "intermediate",
     "tags": ["TCP/IP", "HTTP", "routing", "sockets"]},
    {"id": "r014", "title": "Cisco Networking Basics Specialisation (Coursera)", "url": "https://www.coursera.org/specializations/networking-basics",
     "type": "course", "subject": "Networks", "difficulty": "beginner",
     "tags": ["protocols", "LAN", "WAN", "Cisco"]},
    {"id": "r015", "title": "Beej's Guide to Network Programming", "url": "https://beej.us/guide/bgnet/",
     "type": "article", "subject": "Networks", "difficulty": "intermediate",
     "tags": ["sockets", "C", "TCP", "UDP"]},

    # Math
    {"id": "r016", "title": "3Blue1Brown – Essence of Linear Algebra", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab",
     "type": "video", "subject": "Math", "difficulty": "beginner",
     "tags": ["linear algebra", "vectors", "matrices", "intuition"]},
    {"id": "r017", "title": "MIT OpenCourseWare 18.01 – Single Variable Calculus", "url": "https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/",
     "type": "course", "subject": "Math", "difficulty": "beginner",
     "tags": ["calculus", "derivatives", "integrals"]},
    {"id": "r018", "title": "Mathematics for Machine Learning (Deisenroth et al.)", "url": "https://mml-book.github.io/",
     "type": "book", "subject": "Math", "difficulty": "advanced",
     "tags": ["linear algebra", "probability", "ML foundations"]},

    # Physics
    {"id": "r019", "title": "Khan Academy – Physics", "url": "https://www.khanacademy.org/science/physics",
     "type": "course", "subject": "Physics", "difficulty": "beginner",
     "tags": ["mechanics", "waves", "thermodynamics"]},
    {"id": "r020", "title": "Feynman Lectures on Physics (free online)", "url": "https://www.feynmanlectures.caltech.edu/",
     "type": "book", "subject": "Physics", "difficulty": "advanced",
     "tags": ["classical mechanics", "electromagnetism", "quantum"]},
    {"id": "r021", "title": "MIT 8.01 – Classical Mechanics (OCW)", "url": "https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/",
     "type": "course", "subject": "Physics", "difficulty": "intermediate",
     "tags": ["mechanics", "Newton", "energy", "momentum"]},

    # English
    {"id": "r022", "title": "Grammarly Handbook – Grammar Basics", "url": "https://www.grammarly.com/blog/category/handbook/",
     "type": "article", "subject": "English", "difficulty": "beginner",
     "tags": ["grammar", "writing", "punctuation"]},
    {"id": "r023", "title": "Academic Writing in English (Coursera / UEF)", "url": "https://www.coursera.org/learn/academic-writing-english",
     "type": "course", "subject": "English", "difficulty": "intermediate",
     "tags": ["academic writing", "essays", "research papers"]},
    {"id": "r024", "title": "TED Talks – Public Speaking Tips", "url": "https://www.ted.com/playlists/574/how_to_make_a_great_presentatio",
     "type": "video", "subject": "English", "difficulty": "beginner",
     "tags": ["communication", "presentation", "public speaking"]},

    # ML
    {"id": "r025", "title": "fast.ai – Practical Deep Learning for Coders", "url": "https://course.fast.ai/",
     "type": "course", "subject": "ML", "difficulty": "intermediate",
     "tags": ["deep learning", "PyTorch", "practical", "vision", "NLP"]},
    {"id": "r026", "title": "Hands-On ML with Scikit-Learn, Keras & TensorFlow (Géron)", "url": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/",
     "type": "book", "subject": "ML", "difficulty": "intermediate",
     "tags": ["scikit-learn", "tensorflow", "supervised", "unsupervised"]},
    {"id": "r027", "title": "StatQuest – Machine Learning Fundamentals (YouTube)", "url": "https://www.youtube.com/@statquest",
     "type": "video", "subject": "ML", "difficulty": "beginner",
     "tags": ["statistics", "intuition", "algorithms", "visualisation"]},
    {"id": "r028", "title": "Deep Learning Specialisation (Coursera / Andrew Ng)", "url": "https://www.coursera.org/specializations/deep-learning",
     "type": "course", "subject": "ML", "difficulty": "advanced",
     "tags": ["neural networks", "CNN", "RNN", "regularisation"]},

    # Web
    {"id": "r029", "title": "The Odin Project – Full Stack Web Development", "url": "https://www.theodinproject.com/",
     "type": "course", "subject": "Web", "difficulty": "beginner",
     "tags": ["HTML", "CSS", "JavaScript", "Node.js", "full-stack"]},
    {"id": "r030", "title": "MDN Web Docs – JavaScript Reference", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
     "type": "article", "subject": "Web", "difficulty": "intermediate",
     "tags": ["JavaScript", "DOM", "APIs", "reference"]},
    {"id": "r031", "title": "Frontend Masters – React Complete Guide", "url": "https://frontendmasters.com/courses/complete-react-v8/",
     "type": "course", "subject": "Web", "difficulty": "intermediate",
     "tags": ["React", "hooks", "state management", "TypeScript"]},
    {"id": "r032", "title": "Fullstack Open – Helsinki University", "url": "https://fullstackopen.com/en/",
     "type": "course", "subject": "Web", "difficulty": "advanced",
     "tags": ["React", "Node.js", "GraphQL", "TypeScript", "testing"]},
]

_DIFFICULTY_ORDER: Dict[str, int] = {
    "beginner": 0, "intermediate": 1, "advanced": 2
}


def _difficulty_match_score(resource_diff: str, student_skill: float) -> float:
    """How well the resource difficulty matches student skill level (0-1)."""
    if student_skill < 0.35:
        target = "beginner"
    elif student_skill < 0.70:
        target = "intermediate"
    else:
        target = "advanced"
    r = _DIFFICULTY_ORDER.get(resource_diff, 1)
    t = _DIFFICULTY_ORDER.get(target, 1)
    gap = abs(r - t)
    return 1.0 if gap == 0 else (0.5 if gap == 1 else 0.0)


def content_based_recommend(
    weak_subjects: List[str],
    student_skills: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Return up to 10 resources relevant to the student's weak subjects.

    Args:
        weak_subjects: list of subject names where the student scores low.
        student_skills: mapping from subject name to normalised skill (0-1).

    Returns:
        Up to 10 resource dicts, each augmented with a ``score`` field,
        sorted descending by score.
    """
    weak_upper = {s.upper() for s in weak_subjects}
    candidates = [r for r in _RESOURCES if r["subject"].upper() in weak_upper]

    scored: List[Dict[str, Any]] = []
    for resource in candidates:
        subj = resource["subject"]
        skill = student_skills.get(subj, student_skills.get(subj.upper(), 0.3))
        diff_score = _difficulty_match_score(resource["difficulty"], skill)
        # Subject relevance: always 1.0 since we pre-filtered
        score = 0.6 * diff_score + 0.4
        scored.append({**resource, "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:10]


def collaborative_filter_mentors(
    target_student: Dict[str, Any],
    all_students: List[Dict[str, Any]],
    weak_subjects: List[str],
) -> List[Dict[str, Any]]:
    """Find peer mentors skilled in the target student's weak areas.

    Score formula (sum to 1.0):
      skill_match   0.50 – average self_rating in weak subjects
      year_seniority 0.30 – normalised year gap (mentor year > target year)
      peer_rating   0.20 – average peer_rating in weak subjects

    Args:
        target_student: the student needing help; dict with ``id`` and ``year``.
        all_students: all candidate students (target excluded internally).
        weak_subjects: subjects the target student struggles with.

    Returns:
        Top 5 mentor candidates, each dict containing ``id``, ``full_name``,
        ``year``, ``mentor_score``, ``strong_subjects`` and ``skills``.
    """
    target_id = str(target_student.get("id", ""))
    target_year = int(target_student.get("year", 1))
    weak_upper = {s.upper() for s in weak_subjects}

    scored: List[Dict[str, Any]] = []

    for student in all_students:
        if str(student.get("id", "")) == target_id:
            continue

        mentor_year = int(student.get("year", 1))
        skills = student.get("skills", [])

        # Gather skill values for weak subjects
        self_ratings: List[float] = []
        peer_ratings: List[float] = []
        for sk in skills:
            if str(sk.get("subject", "")).upper().strip() in weak_upper:
                self_ratings.append(float(sk.get("self_rating") or 0) / 10.0)
                peer_ratings.append(float(sk.get("peer_rating") or 0) / 10.0)

        if not self_ratings:
            continue

        avg_self = float(sum(self_ratings) / len(self_ratings))
        avg_peer = float(sum(peer_ratings) / len(peer_ratings)) if peer_ratings else avg_self

        # Only consider students with meaningful skill in weak areas
        if avg_self < 0.5:
            continue

        # Year seniority (0 if same/lower year, normalised 0-1 over range 1-4)
        year_gap = max(mentor_year - target_year, 0)
        year_score = min(year_gap / 3.0, 1.0)

        mentor_score = (
            0.50 * avg_self
            + 0.30 * year_score
            + 0.20 * avg_peer
        )

        strong = [
            str(sk.get("subject", ""))
            for sk in skills
            if float(sk.get("self_rating") or 0) >= 7.0
        ]

        scored.append({
            "id": str(student.get("id", "")),
            "full_name": student.get("full_name", ""),
            "year": mentor_year,
            "department": student.get("department", ""),
            "mentor_score": round(mentor_score, 4),
            "strong_subjects": strong,
            "skills": skills,
        })

    scored.sort(key=lambda x: x["mentor_score"], reverse=True)
    return scored[:5]
