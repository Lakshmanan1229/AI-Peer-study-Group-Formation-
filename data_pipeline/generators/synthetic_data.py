"""
Synthetic data generator for SMVEC AI Peer Study Group Formation System.
Generates 500 realistic student profiles across 5 archetypes.

Usage: python data_pipeline/generators/synthetic_data.py
"""
import json
import random
import os
from datetime import datetime

ARCHETYPES = {
    "strong_consistent": {"cgpa_range": (8.5, 10.0), "skill_mean": 8.0, "skill_std": 1.0, "count": 100},
    "strong_uneven": {"cgpa_range": (7.5, 9.0), "skill_mean": 7.0, "skill_std": 2.5, "count": 100},
    "average_improving": {"cgpa_range": (6.5, 7.5), "skill_mean": 6.0, "skill_std": 1.5, "count": 100},
    "struggling_active": {"cgpa_range": (5.0, 6.5), "skill_mean": 4.5, "skill_std": 1.5, "count": 100},
    "struggling_passive": {"cgpa_range": (4.0, 6.0), "skill_mean": 3.5, "skill_std": 1.0, "count": 100},
}

SUBJECTS = [
    "DSA", "OOP", "DBMS", "OS", "Networks",
    "Mathematics", "Physics", "English", "Machine Learning", "Web Development"
]
DEPARTMENTS = ["CSE", "IT", "ECE"]
LEARNING_PACES = ["slow", "moderate", "fast"]

FIRST_NAMES = [
    "Aarav", "Aditi", "Aditya", "Akash", "Amara", "Ananya", "Arun", "Bharath", "Deepa", "Dhruv",
    "Divya", "Gayatri", "Harish", "Ishaan", "Janani", "Karan", "Kavya", "Kishore", "Lakshmi", "Madhav",
    "Meera", "Naveen", "Nithya", "Pooja", "Pradeep", "Priya", "Rahul", "Ravi", "Rohit", "Sanjay",
    "Santosh", "Saranya", "Shivani", "Shreya", "Siddharth", "Suresh", "Tamil", "Uday", "Vasanth", "Vikram",
]

LAST_NAMES = [
    "Krishnan", "Murugan", "Rajendran", "Selvam", "Subramaniam", "Venkatesh", "Annamalai",
    "Balasubramaniam", "Chandrasekaran", "Durai", "Govindan", "Iyengar", "Jayaraman",
    "Karthikeyan", "Manikandan", "Natarajan", "Ponnusamy", "Ramaswamy", "Shanmugam", "Thirumalai",
]

GOAL_TEMPLATES = [
    "I want to master {subject1} and {subject2} to get a good placement in top MNC companies.",
    "My goal is to understand {subject1} deeply and use it to build real projects.",
    "I need help with {subject1} and want to improve my {subject2} skills for campus recruitment.",
    "Aiming for 9+ CGPA by improving my {subject1} fundamentals with peer study.",
    "Want to crack GATE exam focusing on {subject1} and {subject2}.",
    "Building a strong foundation in {subject1} and aiming for a software development role.",
    "Preparing for product-based company interviews by mastering {subject1} and {subject2}.",
    "I struggle with {subject1} and need consistent peer support to improve my understanding.",
]


def generate_student(archetype_name: str, student_id: int, index: int) -> dict:
    archetype = ARCHETYPES[archetype_name]
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    department = random.choice(DEPARTMENTS)
    year = random.randint(1, 4)

    cgpa_min, cgpa_max = archetype["cgpa_range"]
    cgpa = round(random.uniform(cgpa_min, cgpa_max), 2)

    if archetype_name == "struggling_passive":
        pace = random.choices(LEARNING_PACES, weights=[0.5, 0.4, 0.1])[0]
    elif archetype_name == "strong_consistent":
        pace = random.choices(LEARNING_PACES, weights=[0.1, 0.3, 0.6])[0]
    else:
        pace = random.choices(LEARNING_PACES, weights=[0.2, 0.5, 0.3])[0]

    skills = []
    for subject in SUBJECTS:
        base_rating = random.gauss(archetype["skill_mean"], archetype["skill_std"])
        if archetype_name == "strong_uneven" and random.random() < 0.3:
            base_rating = random.uniform(3.0, 6.0)
        self_rating = max(1.0, min(10.0, base_rating))
        peer_rating = max(1.0, min(10.0, self_rating + random.gauss(0, 0.8)))
        grade_points = max(0.0, min(10.0, self_rating * 0.9 + random.gauss(0, 0.5)))
        skills.append({
            "subject": subject,
            "self_rating": round(self_rating, 1),
            "peer_rating": round(peer_rating, 1),
            "grade_points": round(grade_points, 1),
        })

    availability = []
    avail_prob = {"struggling_passive": 0.3, "strong_consistent": 0.6}.get(archetype_name, 0.45)
    for day in range(7):
        for slot in ["morning", "afternoon", "evening"]:
            availability.append({
                "day_of_week": day,
                "slot": slot,
                "is_available": random.random() < avail_prob,
            })

    s1, s2 = random.sample(SUBJECTS[:6], 2)
    goals = random.choice(GOAL_TEMPLATES).format(subject1=s1, subject2=s2)

    batch_year = 2024 - (year - 1)
    roll_number = f"SMVEC{batch_year}{department}{str(index).zfill(3)}"

    return {
        "id": f"student_{student_id:04d}",
        "email": f"{first_name.lower()}.{last_name.lower()}{student_id}@smvec.ac.in",
        "full_name": f"{first_name} {last_name}",
        "department": department,
        "year": year,
        "cgpa": cgpa,
        "learning_pace": pace,
        "roll_number": roll_number,
        "archetype": archetype_name,
        "role": "student",
        "goals": goals,
        "skills": skills,
        "availability": availability,
        "created_at": datetime.now().isoformat(),
    }


def generate_dataset(output_file: str = "data_pipeline/data/students.json") -> list:
    random.seed(42)
    students = []
    student_id = 1

    for archetype_name, config in ARCHETYPES.items():
        for i in range(config["count"]):
            student = generate_student(archetype_name, student_id, i + 1)
            students.append(student)
            student_id += 1

    random.shuffle(students)

    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(students, f, indent=2)

    dept_counts: dict = {}
    archetype_counts: dict = {}
    for s in students:
        dept_counts[s["department"]] = dept_counts.get(s["department"], 0) + 1
        archetype_counts[s["archetype"]] = archetype_counts.get(s["archetype"], 0) + 1

    print(f"Generated {len(students)} students")
    print(f"Department distribution: {dept_counts}")
    print(f"Archetype distribution: {archetype_counts}")
    print(f"Saved to: {output_file}")

    return students


if __name__ == "__main__":
    generate_dataset()
