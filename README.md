---
title: Email Triage
emoji: 📊
colorFrom: gray
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
short_description: 'RL-based email triage environment '
---

# Email Triage RL Environment

# Overview

This project presents a **Reinforcement Learning (RL) environment** designed to simulate real-world email management.

The system models an intelligent assistant responsible for:

* Prioritizing emails
* Organizing inbox efficiently
* Responding based on urgency and deadlines

The primary objective is to maximize efficiency by making correct and timely decisions under constrained conditions.



# Performance

 **Average Efficiency Score:** ~0.88

# Evaluation Metrics Used

 **Accuracy:** 30%
 **Deadline Management:** 25%
 **Decision Quality:** 25%
 **Reward Efficiency:** 20%

The agent demonstrates stable and consistent performance across multiple difficulty levels.


# Environment Design

# Observation Space

At each step, the agent receives a list of active emails. Each email contains:

**Type**

    0 → Spam
    1 → Newsletter
    2 → Important / Urgent

**Deadline** → Remaining time to act

**Status**

    0 → Unhandled
    1 → Handled



# Action Space

| Action | Description |
| ------ | ----------- |
| 0      | Delete      |
| 1      | Reply       |
| 2      | Archive     |
| 3      | Mark Urgent |
| 4      | Skip        |



# Reward Function

 +5.0 → Correct reply before deadline
 +2.0 → Correct classification (spam/newsletter)
 -10.0 → Missed deadline for important email
 -2.0 → Incorrect action

This reward structure encourages both correctness and timely decision-making.



# Agent Strategy

The agent follows a structured policy:

  Prioritizes **unhandled emails**
  Uses **deadline-based urgency estimation**
  Applies **rule-based classification** for reliability
  Minimizes penalties by avoiding incorrect actions

This approach ensures:

  High efficiency
  Stable performance
  Robust decision-making


# Technical Stack

  Language: Python 3.10
  Framework: FastAPI
  Environment: Custom RL Environment (OpenEnv-compatible)
  Deployment: Docker, Hugging Face Spaces
  Validation: Pydantic models



# Project Structure


├── env.py            # Environment logic
├── agent.py          # Agent decision logic
├── models.py         # Data schemas (Pydantic)
├── inference.py      # Execution entry point
├── grader.py         # Evaluation script
├── openenv.yaml      # OpenEnv configuration
└── requirements.txt  # Dependencies


# API Endpoints (Deployment)

* POST /reset → Initialize environment
* POST /step → Execute action
* GET /test → Retrieve evaluation score



# Evaluation Setup

The environment supports three difficulty levels:

  Easy → Lower complexity, relaxed deadlines
  Medium → Balanced workload
  Hard → High complexity with strict deadlines

The agent dynamically adapts across all scenarios.


# Key Highlights

* Real-world inspired RL environment
* Balanced reward system
* Scalable difficulty levels
* Docker-ready deployment
* OpenEnv compatible



# Future Improvements

* Trainable RL agent (beyond rule-based)
* Integration with real email datasets
* Advanced NLP-based classification
* User personalization
---
