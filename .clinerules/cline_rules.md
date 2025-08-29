mm, yes—Task 5. I'll make this crisp and executable for Cline. Drop the doc below into your repo at `docs/process/cline_rules.md`.
# Cline Rules of Engagement — Charlotte Project

**Scope:** These rules govern how Cline plans, edits, tests, commits, and ships within this repository. The aim is to preserve **determinism, safety, and persona integrity** while moving fast.

**Environments**

* **Dev Container (Linux/Bash)** is the *authoritative* execution surface for builds/tests.
* **Native Windows (PowerShell 7)** wrappers are provided for local ergonomics.
* All examples below show both where relevant. Follow the lane used in the task.

---

## 1) Golden Principles (never violate)

1. **Repo is canon; Memory is cache.** Truths live in `charlotte_core/**` first; ChatGPT "Memory" is optional convenience.
2. **No pushes to `main`.** Ever. All changes occur on feature branches with PRs.

   * Refuse to act if `git rev-parse --abbrev-ref HEAD` is `main`.
3. **CI never writes.** CI **validates** and **packages on tag** only. CI must not commit, tag, or run `backup.py snapshot`.
4. **Determinism or it didn't happen.** UTC `YYYY-MM-DD_HHMMSSZ`, LF endings, UTF-8, stable ordering, manifests.
5. **Privacy first.** Redaction only in intake candidates & reports. Never alter `imports/**` or `archives/**`.
6. **Safety rails on file I/O.** Safe unzip (no Zip-Slip), explicit size caps where applicable, path normalization, no symlink traversal unless allowed.
7. **Everything documented.** Code is commented (why > what). README & CHANGELOG updated with every shipped change.

---

## 2) Work Order Ritual (Plan → Act)

### 2.1 PLAN Block (Cline must produce before writing files)

Include this *verbatim* structure:

<markdown>
# PLAN
## Objective
<one sentence of the user goal>

## Scope of edit
- Files to touch (list)
- Files NOT to touch (list protected files)

## Approach
- Steps 1..N with exact commands (DevContainer Bash and/or Windows PowerShell)

## Acceptance criteria
- Concrete file paths that must exist/change
- Determinism checks (hashes, sorted lists, timestamps)
- Dry-run outputs that must print
- Exit codes to expect (0/2/3/4)

## Risks & rollbacks
- Risks (format drift, size, path issues)
- Rollback plan (git restore/reset, revert commit)

## Out-of-scope
- Anything explicitly not to modify in this run
</markdown>

Only after Nick (or Charlotte) says **GO**, begin **ACT**.

### 2.2 ACT Block (execution log)

Cline must produce a short, chronological log (commands & results) and paste it in the PR description under **ACT LOG**.

---

## 3) Branching, Commits, PRs

### 3.1 Branch naming

Use one of:

* `feat/<short-slug>`
* `fix/<short-slug>`
* `chore/<short-slug>`
* `docs/<short-slug>`

Example: `feat/devcontainer-ingest-tests`

### 3.2 Commits (Conventional Commits + trailers)

* Format: `type(scope): summary`
* Include a body explaining *why* and notable decisions.
* Add trailers when relevant:

  * `Mem-Intent: YYYY-MM-DD-NN` (when a Memory Card is added/updated)
  * `Co-Authored-By:` (if multi-agent)

### 3.3 Pull Requests

* Title mirrors the branch (e.g., `feat: devcontainer + full export ingest tests`)
* Description includes:

  * The **PLAN** (final)
  * The **ACT LOG**
  * **Acceptance evidence** (paths, counts, sample diffs)
  * Risks & rollback notes
* Request review from **Nick**.
* Labels: `feat|fix|docs|chore`, plus `safe-merge` when passing all acceptance.

---

## 4) Protected Surfaces (treat as read-only unless the task explicitly says otherwise)

* `imports/chatgpt_export/<DATE>/raw/**` — verbatim export (audit trail).
* `archives/chat_exports/<DATE>/**` — derived archive; do **not** redact after creation.
* `snapshots/<UTC>Z/**` — never hand-edit; produced only by `backup.py snapshot`.
* `.github/workflows/**` — must not include jobs that commit/tag or run snapshots.
* `charlotte_core/**` — edits must be either:

  * Memory Card additions/edits via scaffolder/proposer, or
  * Structured, reviewed patches (never mass search-and-replace without a plan).

---

## 5) Code Quality Rules

1. **Docstrings & headers:** Every module/function has docstrings with purpose, inputs/outputs, side effects, failure modes.
2. **Comments explain "why", not "what".** Link to decisions (PRD section, pipeline step).
3. **Small units:** Prefer small functions with single responsibilities over long scripts.
4. **Deterministic I/O:** Explicit encodings; `Path.as_posix()` for sorting; UTC timestamps via a shared `utils.utc_ts()`.
5. **Exit codes:** Use `0/2/3/4` consistently; print a one-line fix hint before non-zero exits.
6. **Dry-run parity:** `--dry-run` prints **exact** targets & counts and exits `0`, with no side effects.
7. **Tests before PR:** Run smoke tests in the **DevContainer**.

---

## 6) README & CHANGELOG Duties

### 6.1 README.md (must update when ANY of these change)

* New tool, script, or workflow
* New environment requirement
* Changes to inputs/outputs, flags, or exit codes
* Changes to the memory pipeline or restore order

**Add sections or amend usage examples**. Include both **Bash (DevContainer)** and **PowerShell (Windows)** variants.

### 6.2 CHANGELOG.md (update after every ACT run)

Append to the top under `## [Unreleased]` or a new version block:

```
## [YYYY-MM-DD] <short title>
### Summary
- <1–3 bullets on what changed and why>

### Changes
- Added: <files/commands/flags>
- Modified: <files>
- Removed: <files>

### Outputs
- New/changed paths (with examples)
- Determinism guarantees (any new)
- Exit codes / dry-run outputs confirmed

### Risks & Rollback
- <notes>

PR: #<id>  Commit: <sha>
```

If the run created a snapshot/tag, note the tag (e.g., `backup-20250812-031500Z`) and link to the Release.

---

## 7) Always-on Safety Checklist (Cline must self-check before opening PR)

* [ ] On a feature branch (not `main`)
* [ ] No workflow runs `backup.py snapshot` in CI
* [ ] No secrets or private data in diffs (search patterns: `sk-`, `API_KEY=`, `BEGIN PRIVATE KEY`)
* [ ] Redaction appears **only** in `charlotte_core/_intake/memory_candidates.md` and `reports/**`
* [ ] File endings LF; encoding UTF-8; timestamps UTC `...Z`
* [ ] Deterministic sorting of file lists (forward-slash paths)
* [ ] Dry-run outputs pasted into PR description
* [ ] README & CHANGELOG updated
* [ ] Tests pass in **DevContainer**

---

## 8) Minimal Test Battery (run inside DevContainer)

<bash>
# Ingest smoke (fixture or real export)
python3 tools/ingest_chatgpt_export.py --zip tmp/chatgpt-export-fixture.zip --dry-run
python3 tools/ingest_chatgpt_export.py --zip tmp/chatgpt-export-fixture.zip

# Diff proposer (dry-run then real)
python3 tools/memory_diff_proposer.py --source candidates --dry-run
python3 tools/memory_diff_proposer.py --source candidates

# Scaffolder (dry-run ok)
python3 tools/memory_card_scaffolder.py --category protocol --title "Test Rule" --scope demo --dry-run

# Restore builder
python3 tools/charlotte_restore_builder.py --profile full --only-active --max-bytes 120000 --dry-run
</bash>

Expected artifacts must match the **Memory Pipeline** doc's "Expected Outputs" sections.

---

## 9) What Cline must refuse to do

* Push to `main`, force-push any branch, or rewrite history without explicit instruction.
* Create or push tags from CI.
* Commit compiled/bytecode artifacts (`__pycache__/`, `*.pyc`, `*.pyo`, etc.).
* Redact or transform files under `imports/**` or `archives/**`.
* Run destructive global search/replace without a preview and backup.
* Upload or mirror private data to external services.

---

## 10) Work Order Templates (copy-ready)

### 10.1 Feature Work Order (PLAN)

<markdown>
Title: <feat>: <short slug>

Objective:
<one sentence>

Scope:
- Touch: <files>
- Do NOT touch: imports/**, archives/**, snapshots/**, .github/workflows/** (except <file>)

Approach:
1) <command (Bash)>
   <command (PowerShell)>
2) ...

Acceptance:
- Outputs: <paths>
- Dry-run must print: <lines>
- Exit codes: success=0; empty=3; bad input=2; write error=4

Risks/Rollback:
- <risk> → git restore <file> / revert <sha>

Out-of-scope:
- <items>
</markdown>

### 10.2 Release Work Order (tag/ship)

<markdown>
Title: release: backup-<UTC>Z

Steps:
1) Local: python backup.py snapshot
2) Tag: git tag -a "backup-<UTC>Z" -m "Charlotte snapshot"
3) Push: git push --follow-tags

Acceptance:
- Release artifact contains exactly snapshots/<UTC>Z/**
- MANIFEST overall_sha256 present

Risks:
- None (local-only snapshot, CI packages on tag)
</markdown>

---

## 11) Enforcement Hints (optional but encouraged)

* **Pre-PR check script** Cline can run:

  * Verify not on `main`
  * Grep for secrets in diff
  * Confirm `.gitattributes`/`.editorconfig` enforce LF, UTF-8
  * Run minimal test battery
* **Branch protection** (configured in GitHub) to require PR review + passing checks.

---

## 12) Final reminder to Cline

When in doubt:

* Ask for **PLAN approval** before editing.
* Prefer **small, reversible** diffs.
* **Demonstrate** acceptance with concrete paths and counts.
* Update **README** & **CHANGELOG** every time you alter behavior.
* If any safety rail conflicts with the request, **pause and ask**.

---
