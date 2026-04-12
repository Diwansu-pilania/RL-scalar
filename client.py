"""
Email Triage Environment — Client
Import this in training code: from email_triage_env import EmailTriageEnv, EmailAction
"""
import sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from models import EmailAction, EmailObservation


class EmailTriageEnv(EnvClient[EmailAction, EmailObservation, State]):
    """WebSocket client for the Email Triage Environment."""

    def _step_payload(self, action: EmailAction) -> dict:
        return action.model_dump()

    def _parse_result(self, payload: dict) -> StepResult[EmailObservation]:
        obs_data = payload.get("observation", {})
        obs = EmailObservation(
            email_id=obs_data.get("email_id", ""),
            email_subject=obs_data.get("email_subject", ""),
            email_body=obs_data.get("email_body", ""),
            email_sender=obs_data.get("email_sender", ""),
            email_metadata=obs_data.get("email_metadata", {}),
            grader_feedback=obs_data.get("grader_feedback"),
            score_breakdown=obs_data.get("score_breakdown"),
            task_id=obs_data.get("task_id", 1),
            task_name=obs_data.get("task_name", ""),
            task_description=obs_data.get("task_description", ""),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
        )
        return StepResult(
            observation=obs,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: dict) -> State:
        return State(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
        )
