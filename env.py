import random
from typing import List
from models import EmailObservation, EmailAction, StepResult
import numpy as np
random.seed(42)
np.random.seed(42)


class EmailTriageEnv:
    def __init__(self, num_emails=5):
        self.num_emails = num_emails
        self.max_deadline = 10
        self.reset()

    def reset(self):
        self.emails = []

        for _ in range(self.num_emails):
            self.emails.append({
                "type": random.choice([0, 1, 2]),   # 0=spam,1=normal,2=important
                "deadline": random.randint(1, self.max_deadline),
                "length": random.choice([0, 1]),    # 0=short,1=long
                "handled": False
            })

        return StepResult(
            observation=self._get_obs(),
            reward=0.0,
            done=False,
            info={}
        )

    def _get_obs(self):
        return EmailObservation(
            emails=[
                [
                    e["type"],
                    max(e["deadline"], 0),
                    e["length"],
                    int(e["handled"])
                ]
                for e in self.emails
            ]
        )

    def step(self, action: EmailAction):
        reward = 0

        unhandled = [i for i, e in enumerate(self.emails) if not e["handled"]]

        if not unhandled:
            return StepResult(
                observation=self._get_obs(),
                reward=0.0,
                done=True,
                info={"email_idx": None}
            )

       
        idx = min(unhandled, key=lambda i: self.emails[i]["deadline"])
        email = self.emails[idx]

        urgency = max(0, min(1, (self.max_deadline - email["deadline"]) / self.max_deadline))
        a = action.action

       

        if a == 0:  # delete
            reward += 2 if email["type"] == 0 else -2

        elif a == 1:  # reply
            reward += (3 + 2 * urgency) if email["type"] == 2 else -2

        elif a == 2:  # read
            reward += (2 + urgency) if email["type"] == 1 else -1.5

        elif a == 3:  # prioritize
            reward += (2.5 + 2 * urgency) if email["type"] == 2 else -1

        elif a == 4:  # ignore
            reward -= (1 + 2 * urgency)   

        
        if email["length"] == 1:
            if a in [1, 3]:
                reward += 0.5
            else:
                reward -= 0.2

        
        email["handled"] = True

        
        for e in self.emails:
            if not e["handled"]:
                e["deadline"] -= 1
                if e["deadline"] <= 0:
                    penalty = 1 + abs(e["deadline"]) * 0.5
                    if e["type"] == 2:
                        reward -= 2 * penalty
                    else:
                        reward -= 0.5 * penalty

        done = all(e["handled"] for e in self.emails)

        return StepResult(
            observation=self._get_obs(),
            reward=reward,
            done=done,
            info={"email_idx": idx}
        )

def create_env(task=None):
    """
    Returns an instance of EmailTriageEnv.
    `task` can be used to customize difficulty if needed.
    """
    num_emails = 5
    if task == "medium":
        num_emails = 7
    elif task == "hard":
        num_emails = 10
    return EmailTriageEnv(num_emails=num_emails)
