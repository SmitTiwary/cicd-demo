# Git Basics Playbook — How Changes Are Tracked and Published

Run this **before** `PLAYBOOK.md`. It uses only Git (no CI/CD) on a throwaway branch, so it never touches `dev`/`staging`/`main`. Repo: `SmitTiwary/cicd-demo`.

---

## 0. The one picture to draw on the board

```
  Working directory  --git add-->  Staging area  --git commit-->  Local repo  --git push-->  GitHub (origin)
  (files you edit)                 (next snapshot)                (history on      (shared history)
                                                                    your laptop)
        <------------------------------- git pull / git fetch ---------------------------------
```

Say it out loud:
- **Editing a file** changes only the working directory. Git notices the change but hasn't saved it.
- **`git add`** puts the change in the next snapshot.
- **`git commit`** saves that snapshot permanently in your **local** history, with a unique ID (hash).
- **`git push`** sends your commits to GitHub so other people can see them.

Every step below moves a change one box to the right. Run `git status` after each step to show where it is now.

---

## Step 1 — Where am I?

```bash
cd /Users/smit.tiwary/Documents/cicd
git status
git branch
git log --oneline --graph --decorate -10
```

**What it means:** `git status` is your "you are here" map. `git branch` shows the branch you're on (marked `*`). `git log` shows the history. Each line is a commit with a short hash like `7a76f95`.
**What to see:** `nothing to commit, working tree clean`. Nothing has changed since the last commit.

---

## Step 2 — Make a branch for the lesson

```bash
git switch -c lesson/git-basics
git branch
```

**What it means:** a branch is a movable label that points at a commit. A new branch costs almost nothing and keeps experiments away from `main`.
**What to see:** `* lesson/git-basics`.

---

## Step 3 — Change a tracked file → "modified"

```bash
echo "Edited live in class on $(date +%F)." >> README.md
git status
git diff
```

**What it means:** Git compares your file with the last commit and sees that it changed. The change is **not staged yet**, so it won't go into a commit.
**What to see:**
- `git status` → red `modified: README.md` under *Changes not staged for commit*.
- `git diff` → the new line in green with a `+`. That `+` line is all Git stores for this change.

---

## Step 4 — Create a new file → "untracked"

```bash
echo "Git tracks content, not just files." > notes.txt
git status
```

**What it means:** Git has never seen this file before. It stays **untracked**, and Git ignores its contents until you `add` it.
**What to see:** `notes.txt` under *Untracked files*.

---

## Step 5 — Ignored files → invisible on purpose

```bash
cat .gitignore
python train.py        # regenerates model.pkl
git status
```

**What it means:** `model.pkl`, `.venv/`, and `__pycache__/` are listed in `.gitignore`. Git **pretends they don't exist**. Build outputs and secrets belong here, not in history.
**What to see:** `model.pkl` changed on disk, but `git status` doesn't mention it.

---

## Step 6 — Stage the changes (`git add`)

```bash
git add README.md
git status             # README is green (staged), notes.txt is still untracked
git diff               # empty: nothing left unstaged in README
git diff --staged      # shows what WILL go into the commit
git add notes.txt
git status
```

**What it means:** the staging area lets you **choose** what goes into the next commit. You don't have to commit everything you changed.
**What to see:** both files in green under *Changes to be committed*.

---

## Step 7 — Commit (save a snapshot locally)

```bash
git commit -m "lesson: add class note and notes.txt"
git status
git log --oneline --graph --decorate -5
git show HEAD
```

**What it means:** the snapshot is now saved permanently, with its own hash, your name, the date, and the message. **It exists only on this laptop**, and GitHub doesn't have it yet.
**What to see:**
- `git status` → `working tree clean` again.
- `git log` → a new commit at the top, with `HEAD -> lesson/git-basics` pointing at it.
- `git show HEAD` → the author, date, message, and the exact diff.

---

## Step 8 — A second commit → history grows

```bash
echo "Second line." >> notes.txt
git add notes.txt
git commit -m "lesson: second note"
git log --oneline -3
git diff HEAD~1 HEAD   # what changed between the last two commits
```

**What it means:** each commit points to its parent, and those links form the history. `HEAD~1` means "one commit before the current one". You can compare any two points in time.

---

## Step 9 — Publish (`git push`)

Before pushing, show that GitHub doesn't know about these commits:

```bash
git log --oneline --all --graph --decorate -6
```

**What to see:** `lesson/git-basics` exists, but there's **no** `origin/lesson/git-basics` label yet.

```bash
git push -u origin lesson/git-basics
git log --oneline --all --graph --decorate -6
git status
```

**What it means:** `push` uploads your commits to `origin` (GitHub). `-u` links your local branch to the remote one, so later you can just type `git push`/`git pull`.
**What to see:**
- `origin/lesson/git-basics` now sits on the same commit as your branch.
- `git status` → `Your branch is up to date with 'origin/lesson/git-basics'`.
- On GitHub: `https://github.com/SmitTiwary/cicd-demo/commits/lesson/git-basics`. Open it and click a commit. It's the same hash and the same diff as `git show`.
- **Bonus link to CI/CD:** the Actions tab shows **no** new run, because `ci.yml` only triggers on `dev`/`staging`/`main`.

---

## Step 10 — Ahead / behind (local vs remote)

Make a commit **without pushing**:

```bash
echo "Third line." >> notes.txt
git commit -am "lesson: third note"
git status             # "ahead of 'origin/lesson/git-basics' by 1 commit"
```

Now go the other way. On GitHub, open `notes.txt` on the `lesson/git-basics` branch → ✏️ Edit → add a line → Commit. Then:

```bash
git push               # REJECTED: remote has a commit you don't have
git fetch
git status             # "have diverged, 1 and 1 different commits each"
git log --oneline --all --graph --decorate -6
```

**What it means:** your laptop and GitHub now each have a commit the other doesn't. `fetch` downloads remote commits but **doesn't change your files**.

```bash
git pull --no-rebase   # merge GitHub's commit into yours
git push
git log --oneline --graph --decorate -6
```

**What to see:** a merge commit that joins the two lines, then local and `origin` point at the same commit again. If both edits touched the same line, Git stops with a **merge conflict**. That's worth showing, because it happens often in teams.

---

## Step 11 — Undo cheat-sheet (show each one live)

| Situation | Command | Effect |
|---|---|---|
| Edited a file, want the old version back | `git restore notes.txt` | Throws away unstaged edits |
| Staged by mistake | `git restore --staged notes.txt` | Moves it back out of staging, keeps the edit |
| Already committed **and pushed** a bad change | `git revert HEAD` then `git push` | Adds a **new** commit that undoes it. History stays honest |
| See any old version of a file | `git show HEAD~2:notes.txt` | Prints the file as it was 2 commits ago |

**Key lesson:** once a commit is pushed, you don't erase it. You add a new commit that undoes it (`revert`).

---

## Step 12 — Clean up after class

```bash
git switch demo/new-run
git branch -D lesson/git-basics
git push origin --delete lesson/git-basics
```

---

## TL;DR teaching arc

1. `git status` after every step. **Lesson: always know which box your change is in.**
2. Edit → *modified*. New file → *untracked*. `.gitignore` → *invisible*.
3. `git add` → *staged*. **Lesson: you choose what goes in a snapshot.**
4. `git commit` → saved **locally** with a hash. **Lesson: commit ≠ publish.**
5. `git push` → on GitHub, same hash. **Lesson: publishing is a separate, explicit step.**
6. Ahead/behind, `fetch`/`pull`. **Lesson: there are two copies of history, and you keep them in sync.**
7. `revert`, not delete. **Lesson: shared history only moves forward.**
8. Then switch to `PLAYBOOK.md`: "now let's make GitHub *react* to a push."
