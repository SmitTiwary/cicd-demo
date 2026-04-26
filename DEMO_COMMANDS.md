# CI/CD Demo — Command Walkthrough

A copy-paste-able sequence of every command needed to run the demo, starting from activating the virtual environment all the way through the dev → staging → prod promotion flow.

> Replace `SmitTiwary/cicd-demo` with your own `<user>/<repo>` everywhere.

---

## 1. Activate the virtual environment

```bash
cd /Users/smit.tiwary/Documents/cicd
source .venv/bin/activate
```

(If `.venv` doesn't exist yet:)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Run things locally (sanity check before pushing)

```bash
python train.py          # trains model, writes model.pkl
pytest -v                # runs tests/test_model.py + tests/test_api.py
uvicorn app:app --reload # optional: serve API on http://127.0.0.1:8000
```

Quick API check (in another terminal):

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

---

## 3. One-time GitHub setup (skip if already done)

Create the repo + push:

```bash
gh repo create cicd-demo --public --source=. --remote=origin
git push -u origin main
```

Create the long-lived branches that the workflows trigger on:

```bash
git checkout -b dev      && git push -u origin dev
git checkout -b staging  && git push -u origin staging
git checkout main
```

Create the GitHub Environments (UI step):
1. `gh repo view --web`
2. Settings → Environments → **New environment** → create `dev`, `staging`, `prod`.
3. On `prod`, enable **Required reviewers** and add yourself. This is the manual approval gate.

---

## 4. Inspect status (any time)

```bash
git fetch --all
git log --oneline --all --graph --decorate -10   # branch state
gh run list --limit 10                            # recent CI/CD runs
gh run list --branch dev --limit 5                # runs on a specific branch
gh run list --branch staging --limit 5
```

Deployment history (which SHA is on which environment):

```bash
gh api repos/SmitTiwary/cicd-demo/deployments \
  --jq '.[] | {env: .environment, sha: .sha[0:7], created: .created_at}'
```

---

## 5. Demo A — Feature branch + passing PR

```bash
git checkout -b feature/demo-pass
# (make a small change, e.g. edit README.md)
git add -A
git commit -m "demo: small docs tweak"
git push -u origin feature/demo-pass

gh pr create --base dev --head feature/demo-pass \
  --title "Demo: passing PR" --body "Should pass CI"

gh pr checks                # watch CI go green
gh pr merge --squash         # merging to dev triggers Deploy → dev env
```

---

## 6. Demo B — Failing CI (the quality gate in action)

```bash
git checkout branch1                 # or any feature branch
# Edit tests/test_model.py: change threshold from 0.9 → 0.999
git add tests/test_model.py
git commit -m "demo: raise accuracy threshold to force CI failure"
git push origin branch1

gh pr create --base dev --head branch1 \
  --title "Demo: failing accuracy gate" --body "Should fail CI"

gh pr checks                  # watch the red ❌
```

Then revert and show it goes green:

```bash
# Edit tests/test_model.py: change 0.999 back to 0.9
git add tests/test_model.py
git commit -m "demo: restore accuracy threshold"
git push origin branch1

gh pr checks                  # ✅
gh pr merge --squash
```

---

## 7. Demo C — Promotion flow: dev → staging → prod

After your change is merged into `dev` and deployed to the dev environment:

**Promote dev → staging**

```bash
gh pr create --base staging --head dev \
  --title "Promote: dev → staging" --body "Promotion"
gh pr merge --merge          # push to staging triggers Deploy → staging env
```

**Promote staging → prod**

```bash
gh pr create --base main --head staging \
  --title "Promote: staging → prod" --body "Production release"
gh pr merge --merge          # push to main triggers Deploy → prod env
```

The prod deploy will **pause for approval** because of the Required reviewers rule.
Approve it in the GitHub UI (Actions tab → the running Deploy job → "Review deployments" → Approve).

Verify it landed:

```bash
gh api repos/SmitTiwary/cicd-demo/deployments \
  --jq '.[] | {env: .environment, sha: .sha[0:7], created: .created_at}'
```

All three environments should now be on the same SHA.

---

## 8. Useful cleanup / reset commands

```bash
gh run list --limit 20                         # find a run id
gh run view <run-id>                           # inspect a run
gh run view <run-id> --log-failed              # only failed step logs

gh pr list                                     # open PRs
gh pr close <number>                           # close without merging

git branch -d feature/demo-pass                # delete local branch after merge
git push origin --delete feature/demo-pass     # delete remote branch
```

---

## TL;DR teaching arc

1. `source .venv/bin/activate` → `pytest -v` (local).
2. Push to `branch1` → nothing happens (wrong trigger). **Lesson: triggers matter.**
3. Open PR `branch1 → dev` → CI runs. **Lesson: PRs are the gate.**
4. Force a failure (threshold = 0.999) → CI blocks merge. **Lesson: tests protect the branch.**
5. Fix + merge → Deploy fires to `dev`. **Lesson: CI vs CD.**
6. Promote `dev → staging → main` → prod waits for approval. **Lesson: environments + manual gates.**
