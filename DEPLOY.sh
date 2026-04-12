#!/bin/bash
# ============================================================
# Email Triage OpenEnv — One-Click Deploy Script
# Run this from inside the email-triage-env/ folder
# ============================================================

set -e

echo "============================================"
echo "  Email Triage OpenEnv — Deployment Script"
echo "============================================"
echo ""

# ---- CONFIG — fill these in ----
GITHUB_USERNAME="${GITHUB_USERNAME:-Diwansu-pilania}"
HF_USERNAME="${HF_USERNAME:-Diwansu}"
REPO_NAME="email-triage-env"
# --------------------------------

# Step 1: Remove pycache
echo "[1/6] Cleaning pycache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Step 2: Git init and push to GitHub
echo "[2/6] Initializing git..."
git init
git add .
git commit -m "feat: Email Triage OpenEnv submission

- 3 tasks: Basic Classification, Priority Triage, Complex Routing
- 30 emails across easy/medium/hard difficulty tiers
- Graders with partial credit (priority/category/routing/escalation/summary)
- Reward 0.0-1.0 per step
- Full OpenEnv spec: step()/reset()/state(), typed models, openenv.yaml
- Baseline inference.py with [START]/[STEP]/[END] structured logging
- Docker + HF Spaces ready"

echo ""
echo ">>> Push to GitHub manually:"
echo "    git remote add origin https://github.com/Diwansu-pilania/RL-scalar"
echo "    git branch -M main"
echo "    git push -u origin main"
echo ""
read -p "Press Enter after you've pushed to GitHub..."

# Step 3: Install openenv CLI if needed
echo "[3/6] Checking openenv CLI..."
pip install openenv-core -q

# Step 4: Login to HF
echo "[4/6] Logging into Hugging Face..."
huggingface-cli login

# Step 5: Prepare HF Spaces README (must be at root as README.md)
echo "[5/6] Preparing HF Spaces README..."
cp SPACES_README.md /tmp/hf_readme_backup.md
# HF Spaces needs the YAML front-matter README as the root README
cat SPACES_README.md > /tmp/spaces_readme.md
cat README.md >> /tmp/spaces_readme.md

# Step 6: Push to HF Spaces
echo "[6/6] Deploying to Hugging Face Spaces..."
openenv push --repo-id "$HF_USERNAME/$REPO_NAME"

echo ""
echo "============================================"
echo "  DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo "Your submission URLs:"
echo "  GitHub:  https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  HF Space: https://huggingface.co/spaces/$HF_USERNAME/$REPO_NAME"
echo ""
echo "IMPORTANT: Set these secrets in your HF Space settings:"
echo "  API_BASE_URL = https://api.openai.com/v1"
echo "  MODEL_NAME   = gpt-4o-mini"
echo "  HF_TOKEN     = <your token>"
echo ""
echo "Test your deployment:"
echo "  python inference.py --url https://$HF_USERNAME-$REPO_NAME.hf.space"
echo ""
echo "Deadline: April 8, 11:59 PM IST — good luck!"
