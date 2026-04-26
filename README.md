# Iris CI/CD Demo

A tiny ML project to learn GitHub CI/CD with three environments: **dev**, **staging**, **prod**.

## What's in here

- `train.py` — trains a logistic regression on the iris dataset, saves `model.pkl`
- `app.py` — FastAPI app with a `/predict` endpoint
- `tests/` — pytest tests for the model and the API
- `.github/workflows/ci.yml` — runs on every PR and push: install, train, test
- `.github/workflows/deploy.yml` — on push to `dev`/`staging`/`main`, deploys to the matching environment

## Branch → environment mapping

| Branch    | Environment | Behavior                  |
| --------- | ----------- | ------------------------- |
| `dev`     | `dev`       | Auto-deploy               |
| `staging` | `staging`   | Auto-deploy               |
| `main`    | `prod`      | Requires manual approval  |

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python train.py          # creates model.pkl
pytest -v                # run tests
uvicorn app:app --reload # serve on http://127.0.0.1:8000
```

Try the API:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

## One-time GitHub setup

1. **Create a new empty repo** on github.com (no README, no .gitignore — this repo already has them).
2. **Push this code** (commands are printed below after `git init`).
3. In the repo on github.com, go to **Settings → Environments** and create three environments:
   - `dev`
   - `staging`
   - `prod` — under "Deployment protection rules", check **Required reviewers** and add yourself. This is the key CI/CD concept: prod deploys wait for a human.
4. Create the `dev` and `staging` branches from `main`:
   ```bash
   git checkout -b dev && git push -u origin dev
   git checkout -b staging && git push -u origin staging
   git checkout main
   ```

## The CI/CD flow you'll practice

1. Make a change on a feature branch, open a PR into `dev` → CI runs tests.
2. Merge → `deploy.yml` runs and deploys to the `dev` environment.
3. Open a PR from `dev` → `staging`, merge → deploys to `staging`.
4. Open a PR from `staging` → `main`, merge → **waits for your approval**, then deploys to `prod`.

The "deploy" step here just prints a message and uploads the trained model as an artifact — no cloud account needed. Once you understand the flow, you can swap the "Simulate deploy" step for a real deploy (Render, Fly.io, AWS, etc.).
# trigger demo
