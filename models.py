from pydantic import BaseModel
from typing import List, Optional


class EmailObservation(BaseModel):
    emails: List[List[float]]


class EmailAction(BaseModel):
    action: int


class StepResult(BaseModel):
    observation: EmailObservation
    reward: float
    done: bool
    info: Optional[dict] = {}