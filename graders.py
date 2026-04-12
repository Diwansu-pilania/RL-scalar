"""
graders.py — Platform-facing grader functions for Email Triage OpenEnv.

The hackathon platform resolves graders via "graders:task_1_grader" format,
where "graders" is this module and "task_1_grader" is the function name.

Each grader receives (action, observation) and returns a float strictly in (0, 1).
The platform REJECTS scores of exactly 0.0 or 1.0.
"""

import sys
import os

# Ensure repo root is on sys.path so imports work inside Docker (/app)
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from models import EmailAction, EmailObservation

# ---------------------------------------------------------------------------
# Email dataset — mirrors environment.py (needed for standalone grader lookup)
# ---------------------------------------------------------------------------
EMAILS_EASY = [
    {"id": "e001", "expected_priority": "urgent",  "expected_category": "billing",          "expected_route": "billing_team",  "expected_human": True},
    {"id": "e002", "expected_priority": "high",    "expected_category": "technical_support", "expected_route": "tech_support",  "expected_human": False},
    {"id": "e003", "expected_priority": "low",     "expected_category": "spam",             "expected_route": "spam_filter",   "expected_human": False},
    {"id": "e004", "expected_priority": "high",    "expected_category": "sales",            "expected_route": "sales_team",    "expected_human": False},
    {"id": "e005", "expected_priority": "normal",  "expected_category": "hr",               "expected_route": "hr_team",       "expected_human": False},
]
EMAILS_MEDIUM = [
    {"id": "m001", "expected_priority": "urgent",  "expected_category": "legal",            "expected_route": "legal_team",    "expected_human": True},
    {"id": "m002", "expected_priority": "urgent",  "expected_category": "technical_support", "expected_route": "tech_support",  "expected_human": True},
    {"id": "m003", "expected_priority": "normal",  "expected_category": "sales",            "expected_route": "sales_team",    "expected_human": False},
    {"id": "m004", "expected_priority": "urgent",  "expected_category": "hr",               "expected_route": "hr_team",       "expected_human": True},
    {"id": "m005", "expected_priority": "high",    "expected_category": "billing",          "expected_route": "billing_team",  "expected_human": False},
]
EMAILS_HARD = [
    {"id": "h001", "expected_priority": "urgent",  "expected_category": "billing",          "expected_route": "billing_team",  "expected_human": True},
    {"id": "h002", "expected_priority": "urgent",  "expected_category": "legal",            "expected_route": "legal_team",    "expected_human": True},
    {"id": "h003", "expected_priority": "high",    "expected_category": "hr",               "expected_route": "hr_team",       "expected_human": True},
    {"id": "h004", "expected_priority": "urgent",  "expected_category": "billing",          "expected_route": "billing_team",  "expected_human": True},
    {"id": "h005", "expected_priority": "urgent",  "expected_category": "legal",            "expected_route": "legal_team",    "expected_human": True},
]

PRIORITY_ORDER = ["low", "normal", "high", "urgent"]
CATEGORY_MAP = {
    "billing": "billing_team",
    "technical_support": "tech_support",
    "sales": "sales_team",
    "hr": "hr_team",
    "legal": "legal_team",
    "spam": "spam_filter",
    "general": "general_inbox",
}


def _find_email(email_id: str, dataset: list) -> dict | None:
    for e in dataset:
        if e["id"] == email_id:
            return e
    return None


def _grade(action: EmailAction, email: dict, task_id: int) -> float:
    """Grade action against expected email values. Returns float in (0.01, 0.99)."""
    total = 0.0

    # Priority — 30 pts
    exp_pri = email["expected_priority"]
    agent_pri = action.priority.lower().strip()
    if agent_pri == exp_pri:
        total += 0.30
    elif abs(PRIORITY_ORDER.index(agent_pri) - PRIORITY_ORDER.index(exp_pri)) == 1:
        total += 0.15

    # Category — 30 pts
    if action.category.lower().strip() == email["expected_category"]:
        total += 0.30

    # Routing — 20 pts
    agent_route = action.route_to.lower().strip()
    canonical = CATEGORY_MAP.get(action.category.lower().strip(), "")
    if agent_route == email["expected_route"] or agent_route == canonical:
        total += 0.20

    # Escalation — 10 pts
    if action.requires_human == email["expected_human"]:
        total += 0.10

    # Summary — 10 pts (task 3 only), else normalize to 1.0 scale
    if task_id == 3:
        summary = action.summary or ""
        if len(summary.strip()) >= 20:
            total += 0.10
        elif len(summary.strip()) > 0:
            total += 0.05
    else:
        # Normalize 90-point max to 1.0
        total = min(total / 0.90, 1.0)

    # Clamp strictly to (0, 1) — platform rejects exactly 0.0 or 1.0
    return max(0.01, min(0.99, float(total)))


# ---------------------------------------------------------------------------
# Public grader functions — referenced in openenv.yaml as graders:task_X_grader
# ---------------------------------------------------------------------------

def task_1_grader(action: EmailAction, observation: EmailObservation) -> float:
    """Grader for Task 1: Basic Email Classification (easy emails)."""
    email = _find_email(observation.email_id, EMAILS_EASY)
    if not email:
        return 0.1  # Unknown email — give small non-zero score
    return _grade(action, email, 1)


def task_2_grader(action: EmailAction, observation: EmailObservation) -> float:
    """Grader for Task 2: Priority Triage with Escalation (medium emails)."""
    email = _find_email(observation.email_id, EMAILS_MEDIUM)
    if not email:
        return 0.1
    return _grade(action, email, 2)


def task_3_grader(action: EmailAction, observation: EmailObservation) -> float:
    """Grader for Task 3: Complex Routing with Summarization (hard emails)."""
    email = _find_email(observation.email_id, EMAILS_HARD)
    if not email:
        return 0.1
    return _grade(action, email, 3)
