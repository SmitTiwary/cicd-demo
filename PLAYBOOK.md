# CI/CD Teaching Playbook

Starting branch: **`demo/new-run`** (created off `main`, all three environments synced). Repo: `SmitTiwary/cicd-demo`.

---

## 0. Two concepts to say out loud before touching the keyboard

- **CI (Continuous Integration)** = "is this change safe?" → runs tests on every push/PR. Never deploys anything. → `.github/workflows/ci.yml`
- **CD (Continuous Delivery/Deployment)** = "ship the change" → runs only after code lands on `dev`/`staging`/`main`, and actually pushes it to an environment. → `.github/workflows/deploy.yml`

Write the branch→env table on the board:

| Branch | Environment | Gate |
|---|---|---|
| `dev` | dev | none — auto |
| `staging` | staging | none — auto |
| `main` | prod | **required reviewer** — a human must click Approve |

---

## Step 1 — Local sanity check

```bash
source .venv/bin/activate
python train.py
pytest -v
```

**What it means:** this is what CI will do too, just on your laptop instead of GitHub's machine. If it's broken here, it'll be broken there.
**What to see:** terminal shows `X passed` in green.

---

## Step 2 — Prove triggers matter (nothing happens on a raw push)

```bash
git checkout demo/new-run
echo "// demo edit" >> app.py
git add app.py
git commit -m "demo: touch app.py"
git push origin demo/new-run
```

**What it means:** `ci.yml` only triggers on `push`/`pull_request` to `dev`, `staging`, or `main` (ci.yml lines 8-12). `demo/new-run` isn't one of those branches, so nothing fires.
**Where to see it:** GitHub → **Actions tab** (`https://github.com/SmitTiwary/cicd-demo/actions`) — no new run appears for this push. This is the "aha" moment: *pushing code ≠ triggering a pipeline*.

---

## Step 3 — Open a PR into `dev` → CI runs

```bash
gh pr create --base dev --head demo/new-run \
  --title "Demo: feature branch" --body "Teaching demo"
gh pr checks --watch
```

**What it means:** now the push matches `pull_request: branches: [dev]`, so CI fires: checkout → install deps → train model → run tests → upload `model.pkl` as an artifact (ci.yml lines 20-50).
**Where to see it:**
- Terminal: `gh pr checks --watch` streams pass/fail live.
- Browser: open the PR page → scroll to the checks section → click **Details** to watch the log stream in real time (Actions tab → the running job). Point out: "GitHub just spun up a brand-new Ubuntu VM for this."

---

## Step 4 — Break the quality gate on purpose

```bash
# In tests/test_model.py, change the accuracy threshold from 0.9 to 0.999
git add tests/test_model.py
git commit -m "demo: raise accuracy threshold to force CI failure"
git push
```

**What it means:** the model can't hit 99.9% accuracy on iris with logistic regression, so `pytest` fails.
**Where to see it:** PR page → the check turns **red ❌**, and GitHub blocks the merge button (if branch protection is on; otherwise just point out the red X). Click into the failed log — show students the actual `assert` failure.

Fix it:

```bash
# revert threshold back to 0.9
git add tests/test_model.py
git commit -m "demo: restore accuracy threshold"
git push
gh pr checks --watch
```

**Lesson to say out loud:** "Tests aren't decoration — they're a gate that a human (or a reviewer) can point to and say 'this literally cannot merge yet.'"

---

## Step 5 — Merge → CD fires → deploys to `dev`

```bash
gh pr merge --squash
```

**What it means:** merging pushes a commit onto `dev`. That push matches `deploy.yml`'s trigger (deploy.yml lines 10-12). Two jobs run:
1. `resolve-env` reads the branch name (`dev`) and outputs `env_name=dev` (deploy.yml lines 30-46).
2. `deploy` binds to the GitHub **Environment** called `dev`, retrains, "deploys" (echoes + uploads the model artifact tagged `model-dev-<sha>`).

**Where to see it:**
- Actions tab → a new **Deploy** run appears automatically (separate from the CI run that already finished).
- Repo → **Settings → Environments → dev** → "Deployment history" shows the new deployment with the commit SHA.

---

## Step 6 — Promote `dev → staging`

```bash
gh pr create --base staging --head dev \
  --title "Promote: dev → staging" --body "Promotion"
gh pr checks --watch
gh pr merge --merge
```

**What it means:** same CI/CD pattern, but now `resolve-env` outputs `env_name=staging`. No human gate here — staging auto-deploys just like dev.
**Where to see it:** Actions tab, and **Settings → Environments → staging** deployment history — same as Step 5, different environment.

---

## Step 7 — Promote `staging → main` → the approval gate

```bash
gh pr create --base main --head staging \
  --title "Promote: staging → prod" --body "Production release"
gh pr checks --watch
gh pr merge --merge
```

**What it means:** the push to `main` maps to `env_name=prod`. But `prod`'s Environment has a **Required reviewer** configured — this is the one thing in this whole pipeline that isn't automatic.

**Where to see it — this is the payoff moment:**
1. Actions tab → the Deploy run shows status **Waiting**.
2. Click into the run → banner says *"Review deployments"* → click it → shows your name as the required reviewer → click **Approve and deploy**.
3. Point out to students: *"Everything up to here was a robot. This click is the only human decision in the entire pipeline — and it's deliberately placed in front of production."*

Verify everything landed on the same commit:

```bash
gh api repos/SmitTiwary/cicd-demo/deployments \
  --jq '.[] | {env: .environment, sha: .sha[0:7], created: .created_at}' | head -3
```

**What to see:** dev, staging, and prod all show the same short SHA.

---

## Debrief prompts for students

- Which workflow file is CI, which is CD, and how do you tell from the trigger (`on:`) alone?
- Why did Step 2 (raw push to a feature branch) do nothing?
- What's the difference between a check failing in a PR (Step 4) vs. a deploy waiting for approval (Step 7)? (One is automated policy, one is a human gate.)
- If you wanted to *skip* staging entirely, what would you have to change in `deploy.yml`?

---

## Cleanup after class

```bash
gh pr list                                  # see any leftover open PRs
git branch -d demo/new-run                  # delete local branch
git push origin --delete demo/new-run       # delete remote branch
```
