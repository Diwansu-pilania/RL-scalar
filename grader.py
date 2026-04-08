import numpy as np
from env import EmailAction

def evaluate_agent(env, agent, episodes=50):
    total_score = 0

    for _ in range(episodes):
        result = env.reset()

        obs = result.observation.emails

        correct_classification = 0
        total_classification = 0

        deadlines_met = 0
        urgent_total = 0

        good_decisions = 0
        total_decisions = 0

        total_reward = 0
        done = False

        while not done:
            obs_before = np.copy(obs)

            action_val = agent.predict(obs)
            action = EmailAction(action=action_val)

            result = env.step(action)

            obs = result.observation.emails
            reward = result.reward
            done = result.done
            info = result.info

            total_reward += reward

            idx = info.get("email_idx", None)
            if idx is None:
                continue

            email = env.emails[idx]
            prev_deadline = obs_before[idx][1]

           
            if action_val in [0, 1]:
                total_classification += 1
                if (action_val == 0 and email["type"] == 0) or \
                   (action_val == 1 and email["type"] == 2):
                    correct_classification += 1

           
            if email["type"] == 2:
                urgent_total += 1
                if prev_deadline > 0:
                    deadlines_met += 1

            
            if (email["type"] == 2 and action_val in [1, 3]) or \
               (email["type"] == 1 and action_val == 2) or \
               (email["type"] == 0 and action_val == 0):
                good_decisions += 1

            total_decisions += 1

        acc = correct_classification / max(total_classification, 1)
        deadline_score = deadlines_met / max(urgent_total, 1)
        decision_score = good_decisions / max(total_decisions, 1)
        efficiency_score = np.tanh(total_reward / 20)

        final = (
            0.30 * acc +
            0.25 * deadline_score +
            0.25 * decision_score +
            0.20 * efficiency_score
        )

        total_score += final

    return total_score / episodes