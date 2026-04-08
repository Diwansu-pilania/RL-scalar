import sys
import math
from env import create_env
from agent import SmartEmailAgent
from models import EmailAction

def run_task(task_name: str, num_episodes: int = 1):
    """Run the agent on a specific task and print structured output."""
    
    env = create_env(task=task_name)
    agent = SmartEmailAgent()

    total_score = 0.0

    for episode in range(num_episodes):
        result = env.reset()
        obs = result.observation

        print(f"[START] task={task_name}", flush=True)

        steps_count = 0
        total_reward = 0.0
        done = False

        while not done:
            action_val = agent.predict(obs)
            action = EmailAction(action=action_val)

            result = env.step(action)
            obs = result.observation
            reward = result.reward
            done = result.done

            steps_count += 1
            total_reward += reward

            print(f"[STEP] step={steps_count} reward={round(reward, 4)}", flush=True)

        # Normalize score to 0.0 - 1.0 range using tanh
        score = round((math.tanh(total_reward / 20) + 1) / 2, 4)

        print(f"[END] task={task_name} score={score} steps={steps_count}", flush=True)

        total_score += score

    return total_score / num_episodes


def main():
    tasks = ["easy", "medium", "hard"]
    for task in tasks:
        run_task(task_name=task, num_episodes=1)


if __name__ == "__main__":
    main()
