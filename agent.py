import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["API_BASE_URL"],
    api_key=os.environ["API_KEY"],
)

class SmartEmailAgent:
    def predict(self, obs):
        emails = obs if isinstance(obs, list) else obs.emails

        prompt = f"""You are an email triage agent. Given these emails, decide action for the most urgent unhandled one.

Each email is [type, deadline, length, handled]:
- type: 0=spam, 1=normal, 2=important  
- deadline: lower = more urgent
- length: 0=short, 1=long
- handled: 0=not handled

Emails: {emails}

Actions: 0=delete, 1=reply, 2=read, 3=prioritize, 4=ignore

Reply with ONLY a single digit (0-4). Nothing else."""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0,
            )
            action = int(response.choices[0].message.content.strip()[0])
            if action not in [0, 1, 2, 3, 4]:
                action = 2
            return action
        except Exception:
            unhandled = [(i, e) for i, e in enumerate(emails) if e[3] == 0]
            if not unhandled:
                return 4
            idx, email = min(unhandled, key=lambda x: x[1][1])
            e_type = email[0]
            if e_type == 0:
                return 0
            elif e_type == 2:
                return 1
            else:
                return 2