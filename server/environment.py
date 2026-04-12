"""
Email Triage Environment — Server Logic
Three tasks with increasing difficulty, graders, and reward logic.
"""
import random
from uuid import uuid4
from typing import List, Dict, Optional, Tuple
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import EmailAction, EmailObservation

# ---------------------------------------------------------------------------
# Email dataset — 30 emails across 3 difficulty tiers
# ---------------------------------------------------------------------------

EMAILS: Dict[str, List[dict]] = {
    "easy": [
        {
            "id": "e001",
            "subject": "Invoice #4521 overdue",
            "body": "Hi, my invoice #4521 has been pending for 45 days. I need this resolved immediately or I'll have to escalate to my legal team. Please respond today.",
            "sender": "john.smith@bigcorp.com",
            "expected_priority": "urgent",
            "expected_category": "billing",
            "expected_route": "billing_team",
            "expected_human": True,
        },
        {
            "id": "e002",
            "subject": "Can't login to my account",
            "body": "Hello, I've been unable to login for 2 days. I tried resetting my password but the reset email never arrives. Please help.",
            "sender": "user123@gmail.com",
            "expected_priority": "high",
            "expected_category": "technical_support",
            "expected_route": "tech_support",
            "expected_human": False,
        },
        {
            "id": "e003",
            "subject": "Congratulations! You've won $5,000,000",
            "body": "Dear Winner, You have been selected to receive five million dollars. Click here to claim your prize. Provide your bank details.",
            "sender": "prizes@win-now.xyz",
            "expected_priority": "low",
            "expected_category": "spam",
            "expected_route": "spam_filter",
            "expected_human": False,
        },
        {
            "id": "e004",
            "subject": "Request for product demo",
            "body": "Hi team, I'm the VP of Procurement at MegaRetail Inc. We're evaluating enterprise solutions and would love a product demo for 500 seats.",
            "sender": "vp.procurement@megaretail.com",
            "expected_priority": "high",
            "expected_category": "sales",
            "expected_route": "sales_team",
            "expected_human": False,
        },
        {
            "id": "e005",
            "subject": "Annual leave request",
            "body": "Dear HR, I would like to request annual leave from July 14 to July 21. Please confirm availability. Best regards, Sarah.",
            "sender": "sarah.jones@company-internal.com",
            "expected_priority": "normal",
            "expected_category": "hr",
            "expected_route": "hr_team",
            "expected_human": False,
        },
    ],
    "medium": [
        {
            "id": "m001",
            "subject": "Re: Re: Fwd: Contract amendment",
            "body": "As discussed in our last three meetings, the liability clause in section 4.2 needs amendment before we can proceed. Our legal counsel has flagged this as a potential risk. The deadline for signature is end of month.",
            "sender": "contracts@enterprise-partner.com",
            "expected_priority": "urgent",
            "expected_category": "legal",
            "expected_route": "legal_team",
            "expected_human": True,
        },
        {
            "id": "m002",
            "subject": "Server down - production impacted",
            "body": "URGENT: Our production API has been returning 503s for the last 15 minutes. We're losing approximately $10,000/minute. Transaction IDs: TXN-88291, TXN-88292. Need immediate escalation.",
            "sender": "oncall@client-startup.io",
            "expected_priority": "urgent",
            "expected_category": "technical_support",
            "expected_route": "tech_support",
            "expected_human": True,
        },
        {
            "id": "m003",
            "subject": "Feedback on recent purchase",
            "body": "I recently bought your premium plan and I'm mostly happy, but the reporting feature is a bit confusing. Would love a tutorial. Also, is there a discount for adding 3 more team members?",
            "sender": "customer@smb.co",
            "expected_priority": "normal",
            "expected_category": "sales",
            "expected_route": "sales_team",
            "expected_human": False,
        },
        {
            "id": "m004",
            "subject": "Harassment complaint - confidential",
            "body": "I am writing to report an incident of workplace harassment that occurred on Friday June 7th. I would prefer to discuss this over the phone. Please treat this as strictly confidential.",
            "sender": "employee.anonymous@company.com",
            "expected_priority": "urgent",
            "expected_category": "hr",
            "expected_route": "hr_team",
            "expected_human": True,
        },
        {
            "id": "m005",
            "subject": "Double charge on my card",
            "body": "Hello, I noticed two identical charges of $299 on my credit card on June 3rd and June 4th. Transaction refs: REF-7812, REF-7813. Please refund the duplicate immediately.",
            "sender": "angry.customer@hotmail.com",
            "expected_priority": "high",
            "expected_category": "billing",
            "expected_route": "billing_team",
            "expected_human": False,
        },
    ],
    "hard": [
        {
            "id": "h001",
            "subject": "Partnership opportunity + urgent billing issue",
            "body": "Hi, I'm reaching out with two things: first, we have a major invoice dispute (invoice #9921, $50K) that's been unresolved for 60 days and our CFO is threatening legal action. Second, separately, our CTO wants to discuss a potential OEM partnership worth $2M annually. Who should I speak to for each?",
            "sender": "bd.director@bigfish.com",
            "expected_priority": "urgent",
            "expected_category": "billing",  # primary issue
            "expected_route": "billing_team",  # primary routing
            "expected_human": True,
        },
        {
            "id": "h002",
            "subject": "Data breach notification - immediate action required",
            "body": "Our security team has detected what appears to be unauthorized access to user data in your system between May 1-15. We have evidence suggesting customer PII was accessed. Under GDPR Article 33 you have 72 hours to notify the supervisory authority. This email serves as formal notice.",
            "sender": "security@regulatory-partner.eu",
            "expected_priority": "urgent",
            "expected_category": "legal",
            "expected_route": "legal_team",
            "expected_human": True,
        },
        {
            "id": "h003",
            "subject": "Re: Onboarding - day 1 questions",
            "body": "Hey, starting today as the new Senior Engineer. A few things: (1) my laptop hasn't arrived, (2) I can't access Jira or Confluence, (3) nobody seems to know my start date was today. Also is the benefits enrollment deadline this week? HR said something about it.",
            "sender": "new.hire.alex@company.com",
            "expected_priority": "high",
            "expected_category": "hr",
            "expected_route": "hr_team",
            "expected_human": True,
        },
        {
            "id": "h004",
            "subject": "Account termination threat",
            "body": "I'm writing to inform you that unless my outstanding refund of $1,200 is processed within 24 hours, I will be filing a complaint with the FTC, leaving reviews on every major platform, and consulting my attorney about consumer protection violations. My account: ACC-44821.",
            "sender": "very.angry.customer@yahoo.com",
            "expected_priority": "urgent",
            "expected_category": "billing",
            "expected_route": "billing_team",
            "expected_human": True,
        },
        {
            "id": "h005",
            "subject": "Strategic acquisition inquiry - NDA required",
            "body": "On behalf of [REDACTED Fortune 500], I am exploring acquisition targets in your space. Our M&A team has identified your company as a potential target. Before we can share details, we'd need a mutual NDA. This is time-sensitive as our board meeting is in 3 weeks. Please respond directly to me only.",
            "sender": "ma.advisor@confidential-advisory.com",
            "expected_priority": "urgent",
            "expected_category": "legal",
            "expected_route": "legal_team",
            "expected_human": True,
        },
    ],
}

TASKS = {
    1: {
        "name": "Basic Email Classification",
        "description": (
            "Classify emails by priority (urgent/high/normal/low) and category "
            "(billing/technical_support/sales/hr/legal/spam/general). "
            "Route each email to the correct team. Emails are straightforward with clear signals."
        ),
        "emails": EMAILS["easy"],
        "max_steps": 5,
    },
    2: {
        "name": "Priority Triage with Escalation",
        "description": (
            "Handle ambiguous, multi-faceted emails. Correctly identify priority, "
            "category, and whether the email requires immediate human escalation. "
            "Emails contain subtle cues and require contextual understanding."
        ),
        "emails": EMAILS["medium"],
        "max_steps": 5,
    },
    3: {
        "name": "Complex Routing with Summarization",
        "description": (
            "Triage complex, multi-issue emails. Identify primary issue, correct routing, "
            "escalation need, AND provide a concise 1-2 sentence summary. "
            "Emails may involve multiple departments, legal risks, and ambiguous signals."
        ),
        "emails": EMAILS["hard"],
        "max_steps": 5,
    },
}

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


# ---------------------------------------------------------------------------
# Grader
# ---------------------------------------------------------------------------

def grade_action(action: EmailAction, email: dict, task_id: int) -> Tuple[float, dict]:
    """
    Grade the agent's action against expected answers.
    Returns (reward: float 0.0-1.0, breakdown: dict)
    """
    breakdown = {}
    total = 0.0

    # 1. Priority (30 points)
    expected_pri = email["expected_priority"]
    agent_pri = action.priority.lower().strip()
    if agent_pri == expected_pri:
        breakdown["priority"] = 1.0
        total += 0.30
    elif abs(PRIORITY_ORDER.index(agent_pri) - PRIORITY_ORDER.index(expected_pri)) == 1:
        breakdown["priority"] = 0.5
        total += 0.15
    else:
        breakdown["priority"] = 0.0

    # 2. Category (30 points)
    expected_cat = email["expected_category"]
    agent_cat = action.category.lower().strip()
    if agent_cat == expected_cat:
        breakdown["category"] = 1.0
        total += 0.30
    else:
        breakdown["category"] = 0.0

    # 3. Routing (20 points)
    expected_route = email["expected_route"]
    agent_route = action.route_to.lower().strip()
    # Accept if route matches directly or if it's the canonical route for correct category
    canonical = CATEGORY_MAP.get(agent_cat, "")
    if agent_route == expected_route or agent_route == canonical:
        breakdown["routing"] = 1.0
        total += 0.20
    else:
        breakdown["routing"] = 0.0

    # 4. Escalation (10 points)
    expected_human = email["expected_human"]
    if action.requires_human == expected_human:
        breakdown["escalation"] = 1.0
        total += 0.10
    else:
        breakdown["escalation"] = 0.0

    # 5. Summary (10 points — only for task 3)
    if task_id == 3:
        summary = action.summary or ""
        # Award points if summary is non-empty and reasonably long (>20 chars)
        if len(summary.strip()) >= 20:
            breakdown["summary"] = 1.0
            total += 0.10
        elif len(summary.strip()) > 0:
            breakdown["summary"] = 0.5
            total += 0.05
        else:
            breakdown["summary"] = 0.0
    else:
        breakdown["summary"] = None
        # Redistribute summary weight to routing for tasks 1 & 2
        # (already handled above by keeping routing at 0.20 and total at 0.90)
        # Normalize to 1.0 scale for non-task-3
        if total > 0:
            total = min(total / 0.90, 1.0)

    breakdown["total_reward"] = round(total, 4)

    # Clamp to strictly (0, 1) — platform rejects exactly 0.0 or 1.0
    total = max(0.01, min(0.99, total))

    # Build feedback string
    lines = [f"Score: {round(total, 2)}/1.0"]
    lines.append(f"  priority: {'✓' if breakdown['priority'] == 1.0 else ('~' if breakdown['priority'] == 0.5 else '✗')} (got '{action.priority}', expected '{email['expected_priority']}')")
    lines.append(f"  category: {'✓' if breakdown['category'] == 1.0 else '✗'} (got '{action.category}', expected '{email['expected_category']}')")
    lines.append(f"  routing:  {'✓' if breakdown['routing'] == 1.0 else '✗'} (got '{action.route_to}', expected '{email['expected_route']}')")
    lines.append(f"  escalation: {'✓' if breakdown['escalation'] == 1.0 else '✗'} (got requires_human={action.requires_human}, expected {email['expected_human']})")
    if task_id == 3:
        lines.append(f"  summary: {'✓' if breakdown.get('summary', 0) >= 1.0 else '~' if breakdown.get('summary', 0) > 0 else '✗'}")

    feedback = "\n".join(lines)
    return total, breakdown, feedback


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class EmailTriageEnvironment(Environment):
    """
    A real-world email triage RL environment.
    Three tasks of increasing difficulty.
    """

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task_id: int = 1
        self._current_email_idx: int = 0
        self._emails: List[dict] = []
        self._task_rewards: List[float] = []
        self._done: bool = False

    # ------------------------------------------------------------------
    def reset(self) -> EmailObservation:
        """Start a new episode from task 1."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task_id = 1
        self._current_email_idx = 0
        self._emails = list(TASKS[1]["emails"])
        self._task_rewards = []
        self._done = False
        return self._make_observation()

    # ------------------------------------------------------------------
    def step(self, action: EmailAction) -> EmailObservation:
        """Process one email, grade it, advance the cursor."""
        if self._done:
            obs = self._make_observation()
            obs.done = True
            obs.grader_feedback = "Episode already finished. Call reset()."
            return obs

        current_email = self._emails[self._current_email_idx]
        reward, breakdown, feedback = grade_action(action, current_email, self._current_task_id)

        self._task_rewards.append(reward)
        self._state.step_count += 1

        # Advance
        self._current_email_idx += 1
        done = False

        if self._current_email_idx >= len(self._emails):
            # Finished current task
            if self._current_task_id < 3:
                self._current_task_id += 1
                self._current_email_idx = 0
                self._emails = list(TASKS[self._current_task_id]["emails"])
            else:
                done = True
                self._done = True

        obs = self._make_observation()
        obs.done = done
        obs.reward = reward
        obs.grader_feedback = feedback
        obs.score_breakdown = breakdown
        return obs

    # ------------------------------------------------------------------
    @property
    def state(self) -> State:
        return self._state

    # ------------------------------------------------------------------
    def _make_observation(self) -> EmailObservation:
        if self._done or self._current_email_idx >= len(self._emails):
            # Episode over — return a terminal observation
            return EmailObservation(
                email_id="DONE",
                email_subject="Episode Complete",
                email_body=(
                    f"All tasks completed! "
                    f"Total steps: {self._state.step_count}. "
                    f"Average reward: {sum(self._task_rewards) / max(len(self._task_rewards), 1):.3f}"
                ),
                email_sender="system",
                task_id=self._current_task_id,
                task_name="Complete",
                task_description="Episode finished.",
                done=True,
                reward=0.0,
            )

        task = TASKS[self._current_task_id]
        email = self._emails[self._current_email_idx]
        return EmailObservation(
            email_id=email["id"],
            email_subject=email["subject"],
            email_body=email["body"],
            email_sender=email["sender"],
            email_metadata={
                "email_index": self._current_email_idx + 1,
                "emails_in_task": len(self._emails),
            },
            task_id=self._current_task_id,
            task_name=task["name"],
            task_description=task["description"],
            done=False,
            reward=0.0,
        )

# ---------------------------------------------------------------------------
# Platform-Compliant Grader Wrappers
# ---------------------------------------------------------------------------
def _find_email_data(email_id: str, diff: str) -> Optional[dict]:
    for e in EMAILS.get(diff, []):
        if e["id"] == email_id:
            return e
    return None

def task_1_grader(action: EmailAction, observation: EmailObservation) -> float:
    email_data = _find_email_data(observation.email_id, "easy")
    if not email_data:
        return 0.01  # strictly > 0
    reward, _, _ = grade_action(action, email_data, 1)
    # Platform requires strictly (0, 1) — never exactly 0.0 or 1.0
    return max(0.01, min(0.99, float(reward)))

def task_2_grader(action: EmailAction, observation: EmailObservation) -> float:
    email_data = _find_email_data(observation.email_id, "medium")
    if not email_data:
        return 0.01
    reward, _, _ = grade_action(action, email_data, 2)
    return max(0.01, min(0.99, float(reward)))

def task_3_grader(action: EmailAction, observation: EmailObservation) -> float:
    email_data = _find_email_data(observation.email_id, "hard")
    if not email_data:
        return 0.01
    reward, _, _ = grade_action(action, email_data, 3)
    return max(0.01, min(0.99, float(reward)))


