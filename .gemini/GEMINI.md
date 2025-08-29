# GEMINI.md — Charlotte Project

> Rules of engagement and operating posture for **Gemini CLI** in this repository. Mirrors the Cline rules while adapting to Gemini’s tools and ReAct loop. This file constrains behavior to preserve **determinism, safety, and persona integrity**.

---

## 0) Purpose & Scope

* Provide **system-level guardrails** for Gemini CLI when operating in this repo.
* Require **PLAN → GO → ACT** discipline, small reversible diffs, and complete documentation (README & CHANGELOG) for any change.
* Enforce our product contract (see `docs/process/charlotte_ai_prd.md`) and ops manual (see `docs/process/charlotte_memory_pipeline.md`).

> Placement: keep this file at **`<repo>/.gemini/GEMINI.md`** (project-scoped). It may also live at `~/.gemini/GEMINI.md` for user‑wide defaults. Project copy takes precedence.

---

## 1) Golden Principles (never violate)

1. **Repo is canon; Memory is cache.** All truths live in `charlotte_ai/**` and `docs/**` first.
2. **No pushes to `main`.** Work only on feature branches; open PRs for review.
3. **CI never writes.** CI validates and packages **on tags** only; no commits/tags from CI.
4. **Determinism or it didn’t happen.** UTC timestamps (`YYYY-MM-DD_HHMMSSZ`), LF endings, UTF‑8, stable ordering, manifest hashing.
5. **Privacy-first I/O.** Redaction only in intake candidates & reports. Never alter `imports/**` or `archives/**`.
6. **Safety rails on file ops.** Safe unzip (no Zip‑Slip), size caps where applicable, path normalization, no symlink traversal.
7. **Document everything.** Code explains **why**; PRD/README/CHANGELOG updated with every shipped change.

---

## 2) Operating Ritual — PLAN → GO → ACT

**Gemini must always produce a PLAN first** and wait for explicit approval (the word **GO**) before acting.

### PLAN block (verbatim structure)

```
# PLAN
## Objective
<single sentence>

## Scope of edit
- Touch: <files>
- Do NOT touch: imports/**, archives/**, snapshots/**, .github/workflows/**, any protected surfaces

## Approach
- Steps 1..N with exact shell commands (DevContainer Bash and/or Windows PowerShell) and tool calls

## Acceptance criteria
- Concrete file paths to be created/changed
- Determinism checks (hashes, sorted lists, timestamps)
- Dry-run outputs that must print
- Exit codes to expect (0/2/3/4)

## Risks & rollbacks
- Risks
- Rollback plan (git restore/reset, revert commit)

## Out-of-scope
- Items explicitly not modified in this run
```

### ACT log

After approval (**GO**), produce a concise, chronological **ACT LOG** (commands executed, file writes, and decisions). Paste into the PR description.

---

## 3) Branching, Commits, PRs

* **Branch names:** `feat/<slug>`, `fix/<slug>`, `chore/<slug>`, or `docs/<slug>`.
* **Conventional Commits** with explanatory body; include trailers when relevant:

  * `Mem-Intent: YYYY-MM-DD-NN` for memory card changes
  * `Co-Authored-By:` when multiple agents contribute
* **PR description includes:** PLAN (final), ACT LOG, Acceptance evidence, Risks & rollback notes. Request review from **Nick**.

---

## 4) Protected Surfaces (treat as read‑only unless the task explicitly says otherwise)

* `imports/chatgpt_export/<DATE>/raw/**`
* `archives/chat_exports/<DATE>/**`
* `snapshots/<UTC>Z/**`
* `.github/workflows/**` (must never commit/tag or run snapshots)
* `charlotte_ai/**` (edits only via scaffolder/proposer or reviewed, targeted patches)

---

## 5) Code Quality & Documentation Rules

1. **Docstrings & headers**: every module/function has docstrings including purpose, inputs/outputs, side effects, failure modes.
2. **Explain the why**: comments emphasize rationale over restating code.
3. **Small units**: prefer single‑responsibility functions; avoid giant scripts.
4. **Deterministic I/O**: explicit encodings; normalized paths; UTC timestamps via shared utils.
5. **Exit codes**: use `0/2/3/4` consistently; print a one‑line fix hint before non‑zero exit.
6. **Dry‑run parity**: `--dry-run` prints exact targets & counts; exits `0`; no side effects.
7. **Tests/smoke**: run minimal battery inside DevContainer before PR.

---

## 6) Required Reading & Adherence

* **Product contract:** `docs/process/charlotte_ai_prd.md` (follow scope, workflows, and success metrics).
* **Ops manual:** `docs/process/charlotte_memory_pipeline.md` (respect tracks A/B/C, restore order, backups/tagging discipline).
* **README.md** (update when tools, flags, exit codes, or pipeline behavior changes).

**Gemini must load and cite sections from these docs when proposing changes.**

---

## 7) Allowed Tools & Permissions

* Prefer built‑in Gemini CLI tools. Ask for permission before using any tool that writes, executes commands, or touches the network. Do **not** rely on `--yolomode`.
* For file writes, use the CLI’s write tool to create/update files and echo diffs into the PR description.
* For shell commands, propose exact commands in PLAN; run only after **GO**.

---

## 8) Comment Augmentation & Link Hygiene (this task family)

When asked to “augment comments & validate links,” Gemini must:

* Scan all recognized source files and **add explanatory comments** that teach future readers *why* the code exists, how it fits the pipeline/PRD, and known edge cases.
* Normalize header comments across scripts; ensure every CLI tool documents flags, exit codes, dry‑run behavior, and outputs.
* Validate **internal links** across `README.md` and `docs/**`; fix broken anchors/paths.
* Flag any **refactor** that reduces duplication or clarifies responsibilities; propose in PLAN with a small, reversible diff.

---

## 9) Outputs & Evidence (every ACT run)

* **CHANGELOG.md**: append a dated entry with Summary, Changes (Added/Modified/Removed), Outputs, Determinism guarantees, Risks & Rollback, and PR/commit metadata.
* **README.md**: update usage or behavior changes.
* **Reports**: when generating manifests or ingest reports, include counts and SHA‑256s as acceptance evidence.

---

## 10) Refusals (hard stops)

Gemini must refuse to:

* Push to `main`, force‑push, rewrite history without explicit human instruction.
* Create/push tags from CI.
* Commit compiled artifacts (`__pycache__/`, `*.pyc`, etc.).
* Mass search‑and‑replace without preview and backup.
* Upload private data to external services.

---

## 11) Custom Commands (optional)

Consider adding project commands under `<repo>/.gemini/commands/`:

* `/plan` → inserts the PLAN template.
* `/fixlinks` → scans `README.md` + `docs/**` for broken links and proposes patches.

---

## 12) Quick Self‑Check (pre‑PR)

* [ ] On a feature branch, not `main`
* [ ] No CI workflow commits/tags/snapshots
* [ ] No secrets in diffs
* [ ] LF endings, UTF‑8, UTC timestamps
* [ ] Deterministic ordering of file lists
* [ ] Dry‑run outputs captured
* [ ] README & CHANGELOG updated
* [ ] DevContainer tests pass

---

## 13) Mode Notes

* **Interactive default**: PLAN only until **GO**.
* **Non‑interactive** (`gemini -p "..."`): PLAN‑only is enforced; do not perform writes/exec.

---

*End of GEMINI.md*