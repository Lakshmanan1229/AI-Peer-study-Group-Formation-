"""General-purpose helpers for the AI Peer Study Group Formation system."""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────────────
# Group name generation
# ──────────────────────────────────────────────────────────────────────────────

ADJECTIVES: List[str] = [
    "Brilliant", "Dynamic", "Curious", "Creative", "Fearless",
    "Tenacious", "Visionary", "Agile", "Diligent", "Inventive",
    "Stellar", "Mighty", "Swift", "Nimble", "Radiant",
    "Focused", "Bold", "Clever", "Eager", "Resilient",
]

NOUNS: List[str] = [
    "Coders", "Explorers", "Thinkers", "Builders", "Innovators",
    "Scholars", "Pioneers", "Solvers", "Hackers", "Minds",
    "Wizards", "Champions", "Learners", "Creators", "Engineers",
    "Architects", "Analysts", "Devs", "Titans", "Trailblazers",
]


def generate_group_name() -> str:
    """Return a randomly generated group name, e.g. ``Brilliant_Coders``."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj}_{noun}"


# ──────────────────────────────────────────────────────────────────────────────
# Schedule overlap
# ──────────────────────────────────────────────────────────────────────────────

_SLOT_NAMES: Dict[str, str] = {
    "morning": "Morning (08:00–12:00)",
    "afternoon": "Afternoon (12:00–17:00)",
    "evening": "Evening (17:00–21:00)",
}

_DAY_NAMES: Dict[int, str] = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def compute_schedule_overlap(
    availability_lists: List[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Return slots where most members are available.

    A slot is included if at least half the members are available in it.

    Args:
        availability_lists: one inner list per member; each inner list
            contains dicts with keys ``day_of_week`` (int), ``slot`` (str),
            ``is_available`` (bool).

    Returns:
        List of dicts ``{day_of_week, slot, day_name, slot_name, available_count}``,
        sorted by (day_of_week, slot).
    """
    if not availability_lists:
        return []

    n_members = len(availability_lists)
    slot_counts: Dict[tuple, int] = {}

    for avail_list in availability_lists:
        for entry in avail_list:
            if not entry.get("is_available", False):
                continue
            day = int(entry.get("day_of_week", -1))
            slot = str(entry.get("slot", "")).lower()
            if 0 <= day <= 6 and slot in _SLOT_NAMES:
                key = (day, slot)
                slot_counts[key] = slot_counts.get(key, 0) + 1

    threshold = max(1, n_members // 2)
    result: List[Dict[str, Any]] = []
    for (day, slot), count in sorted(slot_counts.items()):
        if count >= threshold:
            result.append({
                "day_of_week": day,
                "slot": slot,
                "day_name": _DAY_NAMES.get(day, str(day)),
                "slot_name": _SLOT_NAMES.get(slot, slot),
                "available_count": count,
            })

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Numeric helpers
# ──────────────────────────────────────────────────────────────────────────────


def normalize_scores(scores: List[float]) -> List[float]:
    """Apply min-max normalisation to *scores*.

    Returns the original list unchanged when all values are equal.
    """
    if not scores:
        return []
    lo = min(scores)
    hi = max(scores)
    if hi == lo:
        return [0.0] * len(scores)
    return [(x - lo) / (hi - lo) for x in scores]


# ──────────────────────────────────────────────────────────────────────────────
# Name lookups
# ──────────────────────────────────────────────────────────────────────────────


def get_day_name(day_of_week: int) -> str:
    """Return the English name for *day_of_week* (0 = Monday … 6 = Sunday)."""
    return _DAY_NAMES.get(day_of_week, f"Day {day_of_week}")


def get_slot_name(slot: str) -> str:
    """Return a human-readable label for a slot identifier string."""
    return _SLOT_NAMES.get(slot.lower(), slot.capitalize())
