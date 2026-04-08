import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from fastapi import FastAPI
from models import EmailAction
from env import create_env

app = FastAPI()

envs = {
    "easy": create_env(task="easy"),
    "medium": create_env(task="medium"),
    "hard": create_env(task="hard"),
}
current_task = "easy"

@app.get("/")
def root():
    return {"status": "ok", "message": "Email Triage RL Environment"}

@app.post("/reset")
def reset(task: str = "easy"):
    global current_task
    current_task = task
    if task not in envs:
        envs[task] = create_env(task=task)
    result = envs[task].reset()
    return result

@app.post("/step")
def step(action: EmailAction):
    result = envs[current_task].step(action)
    return result

@app.get("/state")
def state():
    env = envs[current_task]
    obs = env._get_obs()
    return {"observation": obs}

def main():
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()