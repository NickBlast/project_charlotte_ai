You are Gemini, acting as Senior Engineer. Perform a TRUE REBIRTH of the repo to a single feature spine: the Memory Cards System (MCS) with three tiny security/privacy rails. Use Plan → Act discipline, acceptance criteria, and rollback.

## Context
- Repository: https://github.com/NickBlast/project_charlotte_ai
- Direction: Keep ONLY **Track C — Memory Cards (MCS)**. Hard delete everything else (no attic).
- Privacy stance: Treat ANY repo that is NOT explicitly private as PUBLIC.

## Operating Rules
- Create branch: `feat/mcs-v0_1-rebirth`
- Never commit to `main`.
- Small, reviewable commits grouped by concern.
- Determinism: stable ordering, LF endings, UTF-8.
- Exit codes: `0` success, `1` failure.
- Python: 3.11+; CLI built with **argparse** (stdlib). Dependencies: **PyYAML** only (if needed).

## Security & Privacy Rails (must implement)
1) **Default ignores**: `**/secrets/**`, `*.key`, `*.pem`, `.env*`
   - Add to `.gitignore`.
   - Ensure exporter/build routines ignore these patterns.

2) **Public-remote tripwire**: Before any command that **writes** to the repo (new/update) or **emits artifacts** to `/dist/`, detect if the repo is public; if public, print a conspicuous RED warning and require a `--yes` flag to proceed.
   - Policy: “Any repo that is NOT private is PUBLIC.”
   - Implementation:
     - If `gh` exists: `gh repo view --json isPrivate` → boolean.
     - Else if `GITHUB_TOKEN` present: call GitHub API for `private` flag.
     - Else: **assume public** and warn.
   - Never hard-block; require explicit `--yes` when public.

3) **No raw PII in Card HEADERS**: `title`, `tags`, `category`, `mode`, `source` must not contain obvious PII. Warn (non-fatal) if detected. Card body is allowed.
   - Warn on: email (`[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}`), phones (E.164-ish `\+?\d[\d\s().-]{7,}`), SSN-like (`\b\d{3}-\d{2}-\d{4}\b`), naive street addresses (e.g., `\b\d{1,5}\s+\w+(?:\s+\w+){0,3}\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Lane|Ln)\b`, case-insensitive). Case-insensitive overall.

## Scope of Work

### A) HARD DELETE (no attic, real removal)
Remove all code/scripts/tests/docs related to:
- Track B weekly self-dump & diff proposer.
- Test batteries/validation tied to ingest/proposer/scaffolder/restore builder.
- Tag-driven releases (zip on `backup-<UTC>`).
- Cross-platform wrappers (PowerShell/Bash) for tools; keep only Python.
- Ops manual & authoring templates beyond Memory Cards (Prompt/Research/Planning/Prompt-Critic/Test Plan, etc.).
- Persona compliance scaffolding.
- Templates other than the Memory Card YAML.
- Snapshot backups, restore builder, Track A ingest (delete all code + README references).

Implementation guidance:
- Inventory with ripgrep on keywords: `ingest|export|self_dump|proposed_patches|proposer|restore|backup|release|wrappers|compliance|templates`.
- `git rm -r` hard delete; keep the repo importable/runnable after removals.

### B) BUILD: Memory Cards System (MCS)

**File layout**
- Cards: `charlotte_ai/memory/cards/<category>/<slug>.yaml`
- Index: `charlotte_ai/memory/index.json` (ACTIVE cards only; deterministic sort by `title` then `id`)
- Template: `templates/memory_card.yaml` (the only template)
- CLI: `tools/cards_cli.py` (entry: `python tools/cards_cli.py <subcommand>`)

**YAML schema (single source of truth)**
- `id` (uuid4)
- `title` (str)
- `category` (str)
- `scope` (str)
- `tags` (list[str])
- `mode` (str)
- `status` (enum: active|dormant)
- `created_utc` (ISO 8601 UTC; e.g., from `datetime.now(timezone.utc).isoformat()`)
- `updated_utc` (ISO 8601 UTC)
- `source` (str; header PII scan applies)
- `body_md` (str; markdown)
- `mem_intent` (str, 1–2 lines)
- `checksum` (sha256 of `body_md`, hex)

**Provide the canonical template** (`templates/memory_card.yaml`):
```

id: ""
title: ""
category: ""
scope: ""
tags: \[]
mode: ""
status: "active"
created\_utc: ""
updated\_utc: ""
source: ""
body\_md: |
(write the memory card details here in markdown)
mem\_intent: ""
checksum: ""

```

**CLI subcommands (argparse)**
- `cards new --title T --category C --tags "a,b,c" [--mode M] [--scope S] [--status active|dormant] [--source TEXT]`
  - Generates slug from title.
  - Creates YAML from template; fills uuid/timestamps; checksum from empty or provided `--body @file.md`.
  - Updates `index.json`.
  - Tripwire check before write; require `--yes` if repo is public.

- `cards update <card_path> [--title ... --tags ... --mode ... --scope ... --status ... --source ... --body @file.md]`
  - Edits fields; recomputes checksum from `body_md` if changed; bumps `updated_utc`.
  - Updates `index.json`.
  - Tripwire check before write; require `--yes` if repo is public.

- `cards list [--active|--all] [--tag X] [--category Y]`
  - Prints deterministic table (no body content). Defaults to `--active`.

- `cards validate`
  - Schema conformity (load all cards; ensure required fields).
  - UUID uniqueness across all cards.
  - `checksum` equals sha256(`body_md`).
  - **Header PII**: print WARN lines if detected; do NOT fail.
  - Exit `1` only if schema/uuid/checksum errors are present.

- `cards build-pack --filter "tag:foo|category:bar" --max-bytes 110000 [--yes]`
  - Select **active** cards matching OR-filters (`|`), e.g., `tag:X|tag:Y|category:projects`.
  - Deterministic order (`title`, then `id`).
  - Produce chunked, paste-ready text files into `dist/pack_<UTC>/chunk_001.txt`, `chunk_002.txt`, …
  - Chunking: append card blocks until adding the next would exceed `--max-bytes`; then start a new chunk. Include clear delimiters (e.g., `### <title> [<id>]`).
  - Tripwire: require `--yes` when repo is public.

- `cards remember-snippet <card_path>`
  - Print a one-liner: `Remember (Mem-Intent: "<mem_intent>") — <title> [<id>]`.

**Determinism details**
- Sorting: pure Unicode sort by `title` then `id`.
- Line endings: LF.
- Stable chunk boundaries: same input → same chunks/SHAs.
- `index.json`: active cards only, `{id,title,category,tags,mode,status,updated_utc}`; sorted by `title,id`.

**.gitignore**
```

**/secrets/**
\*.key
*.pem
.env*
/dist/
/artifacts/

```

**README (≤30 lines) — “Memory Cards Quickstart”**
- Show `new`, `update`, `list`, `validate`, `build-pack`, `remember-snippet` examples.
- Mention the three rails briefly and `--yes` behavior when public.

## Plan → Act

### Plan
1) Branch: `feat/mcs-v0_1-rebirth`.
2) Inventory and **hard delete** all non-MCS code & docs.
3) Add template, implement CLI with argparse, validators, tripwire.
4) Implement `index.json` builder and deterministic packer.
5) Add `.gitignore` entries.
6) Write concise README Quickstart.
7) Run smoke + determinism checks.
8) Open PR with summary and migration notes.

### Act (Checklist)
- [ ] `git checkout -b feat/mcs-v0_1-rebirth`
- [ ] Ripgrep inventory; produce deletions list; `git rm -r` those paths.
- [ ] Add `templates/memory_card.yaml` (canonical).
- [ ] Create `tools/cards_cli.py`:
      - argparse subcommands above
      - uuid4, UTC timestamps, sha256
      - header-PII regex warnings (case-insensitive)
      - public-remote tripwire (gh/API/assume-public) gating writes & `/dist` emits with `--yes`
      - deterministic `index.json` writer
      - deterministic chunked exporter with `--max-bytes`
- [ ] Update `.gitignore` with secret patterns + `/dist/`, `/artifacts/`.
- [ ] Write README Quickstart (≤30 lines).
- [ ] Smoke + determinism:
      - `python tools/cards_cli.py new --title "Test Card" --category "projects" --tags "alpha,beta" --yes`
      - `python tools/cards_cli.py list --active`
      - `python tools/cards_cli.py validate`  # expect exit 0
      - `python tools/cards_cli.py build-pack --filter "category:projects" --max-bytes 110000 --yes`
      - Repeat build-pack; compute SHA-256 of all `chunk_*.txt` → must match.

## Acceptance Criteria
- Only Memory Cards feature remains; no dead references to removed features.
- `cards new/update/list/validate/build-pack/remember-snippet` work as specified.
- Build-pack outputs are deterministic (identical SHAs across two successive runs with no changes).
- `.gitignore` and exporter ignore patterns are honored.
- Tripwire requires `--yes` when repo is not private.
- Header-PII warnings appear when applicable; schema/uuid/checksum failures return exit `1`.
- README Quickstart ≤30 lines and accurate.
- Ripgrep for removed-feature keywords returns **0** hits outside change history.

## Rollback Plan
- Revert the branch to the commit before deletions.
- If CLI determinism/validation fails, revert the CLI commit and re-apply in smaller slices.
- If tripwire is too aggressive, `--yes` override already supported—document the explicit risk acknowledgement in PR.

## Notes
- Keep the dependency surface minimal (stdlib + PyYAML).
- Do NOT implement snapshots, restore builder, or Track A ingest in this pass.