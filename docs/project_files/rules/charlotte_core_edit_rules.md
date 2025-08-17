# Direct Edit Flow — Modes (Bash‑only)

**Status:** Track B retired. Manual, author‑first edits are canonical.

This guide replaces the Weekly Self‑Dump and automated patch proposer. You edit Mode cards **directly** in the repo, keep a tiny changelog in each card, and track review dates. Manual curation via the scaffolder is the recommended flow.

---

## What changes

* **Track B** (weekly self‑dump + proposer) → **Removed** from process. (You may archive related folders/scripts under `_deprecated/track_b/`.)
* When curating from `charlotte_core/_intake/memory_candidates.md`, convert candidates into Memory Cards via `tools/memory_card_scaffolder.py`; do not generate patch files.
* **Direct Edit** is the default: open the card, edit it, commit with a Mem‑Intent trailer, PR.
* **UIDs** added to every card for quick reference and tooling later.

---

## Mode Card Schema (front‑matter)

Add these fields (or confirm they exist) at the top of every Mode card.

```yaml
---
title: Mode — <Name>
uid: ABC123              # 6‑char Crockford base32 (0‑9 A‑Z minus I L O U)
type: memory_card
category: mode
scope: Active            # or Project‑scoped if applicable
status: active           # active | amended | deprecated | archived
version: 1.0             # bump on meaningful change
updated: 2025-08-16      # last content change date (UTC)
last_review: 2025-08-16  # last full review date (UTC)
tags: [mode, cues, behaviors, safety]
---
```

### Body sections (recommended)

```
## Canonical Truth
<One short paragraph that defines the mode’s identity and purpose.>

## Activation & Cues
- Activate: "<cue>"
- Deactivate: "<cue>"

## Behaviors (When Active)
- <bullet points — neutral, testable>

## Guardrails (Always)
- <bullets>

## Changelog
- 2025-08-16: Added deactivation cue "let’s focus"; updated behaviors.
- 2025-07-30: Initial card.

## Links
- Replaces: <uid> (if this supersedes an older card)
- Related: <other uids or paths>
```

---

## UID Rules (lightweight)

* **Format:** 6 characters, uppercase, Crockford base32: `0123456789ABCDEFGHJKMNPQRSTVWXYZ` (no I, L, O, U).
* **Uniqueness:** Keep a small registry file at `charlotte_core/uids.json` and add each card when created.

Example `uids.json` entry:

```json
{
  "HN9MDE": {"path": "charlotte_core/modes/hacker_noir.md", "title": "Mode — Hacker Noir", "category": "mode"}
}
```

---

## Direct Edit — Step‑by‑Step (Beginner‑safe)

### 1) Create a safety branch (DevContainer, Bash)

```bash
DATE=$(date +%F)
git fetch --all && git checkout main && git pull
git checkout -b chore/mode-edit-$DATE
```

### 2) Open the Mode card

* Via path (Explorer sidebar in VS Code), or
* Via UID: look up the `path` in `uids.json` and open that file.

### 3) Make the change

* Edit **body** sections (Cues, Behaviors, Guardrails, etc.).
* Update **front‑matter** fields:

  * `updated:` → today’s date (UTC)
  * `version:` → bump if the behavior changed materially
  * `last_review:` → set to today **only if** you did a full pass on the card
* Add a bullet to **Changelog** describing what changed.

### 4) Commit with intent

```bash
git add -A
git commit -m "Mode(<Name>): <short change> 

Mem-Intent: Direct-Edit; scope=mode; target=<UID>; reason=manual-refinement; status=Active"
```

Then push and open a PR:

```bash
git push -u origin chore/mode-edit-$DATE
```

### 5) (Optional) Sanity check structure

* If desired, run a restore dry‑run to confirm structure loads, but it’s not required for simple text edits.

### 6) Merge and move on

* After PR review/merge, the repo **is** the truth; snapshots/restores inherit it automatically.

---

## Deprecation & Archival

* **Meaningful behavior change** → create a **new card** (new `uid:`), set old card `status: deprecated`, and add a **Links → Replaced by:** reference to the new UID.
* After a deprecation cooling period, you may move deprecated cards to `charlotte_core/_archive/`.

---

## Review Cadence (light, manual)

* Every \~3 months, run a quick **modes review** day:

  * Open each mode, skim **Cues/Behaviors/Guardrails**.
  * If unchanged, set `last_review:` to today and add a **Changelog** line: “Quarterly review — no changes.”
  * If changes are needed, follow the **Direct Edit** steps above.
* Keep a simple log at `charlotte_core/reviews/modes_review_log.md`:

```
| Date       | UID    | Title                 | Action          | Notes |
|------------|--------|-----------------------|-----------------|-------|
| 2025-08-16 | HN9MDE | Mode — Hacker Noir    | No change       | Quarterly review |
| 2025-11-16 | HN9MDE | Mode — Hacker Noir    | Updated cues    | Added “let’s focus” |
```

---

## Example — Completed Mode Card (excerpt)

```md
---
title: Mode — Hacker Noir
uid: HN9MDE
type: memory_card
category: mode
scope: Active
status: active
version: 1.3
updated: 2025-08-16
last_review: 2025-08-16
tags: [mode, cues, behaviors, safety]
---

## Canonical Truth
Hacker Noir is a terse, surgical operator mindset for security/incident strategy and high‑stakes tech planning.

## Activation & Cues
- Activate: "Charlotte, switch to Hacker Noir" / "go operator"
- Deactivate: "exit Hacker Noir" / "back to normal" / "let’s focus"

## Behaviors (When Active)
- Write stepwise plans with acceptance criteria and rollback.
- Lead with threat modeling; then actions.
- Plain language; no metaphors unless asked.

## Guardrails (Always)
- No illegal guidance or glamorized harm.
- Persuasion without manipulation; disclose trade‑offs.
- Privacy‑first; exit immediately on cue.

## Changelog
- 2025-08-16: Added deactivation cue "let’s focus"; clarified behaviors.
- 2025-07-30: Initial card.

## Links
- Related: Complexity Quarantine Protocol (UID TBD)
```

---

## Cleanup Plan (to simplify the repo)

1. Move any Track B artifacts to `charlotte_core/_deprecated/track_b/` (keep history clean; nothing breaks).
2. Remove references to Track B from `README.md` and diagrams.
3. Add a short section in `README.md` called **“Direct Edit Flow (Modes)”** linking to this guide.
4. Add `uids.json` and back‑fill UIDs on existing cards (one PR; simple review).

---

## Backlog (do not action yet)

1. **Quarterly Review Script (optional)** — list all Mode cards, prompt for keep/change/archive, auto‑update `last_review`/Changelog and open a PR.
2. **Essence Vault Format** — design a compact, structured export (JSON or SQLite) that snapshots persona/modes/protocols with UIDs + hashes for deterministic restores.
3. **Run Outside ChatGPT** — evaluate local/hosted options (OpenRouter free models, small local LLMs) for offline drafting and diff‑proposals while keeping Git as the canonical store.

---

### Acceptance Criteria

* Every Mode card has a **UID**, **updated**, **last\_review**, **status**, and **version** in front‑matter.
* Edits follow the **Direct Edit** steps and include a **Mem‑Intent** commit trailer.
* Deprecated cards clearly link to their replacement (if any) and/or move to `_archive/` after a cooling period.
