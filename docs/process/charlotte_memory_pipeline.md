title: Short Active Title
intent_id: YYYY-MM-DD-NN
type: memory_card
scope: global|<project>|<mode>
tags: [category, project:<name>, mode:<name>]
updated: YYYY-MM-DD
status: active
# Charlotte Memory Pipeline

This document describes the Charlotte Memory Pipeline with a lean, author-first workflow. Deprecated: Track B (Weekly Self-Dump) and the Diff Proposer — manual curation into Memory Cards is the canonical flow.

## Overview

Core tools

1. ingest (tools/ingest_chatgpt_export.py)
2. scaffolder (tools/memory_card_scaffolder.py)
3. restore builder (tools/charlotte_restore_builder.py)

Use the scaffolder to author and maintain Memory Cards; do not rely on automated patch proposers.

## Pipeline Architecture (lean)

### A) Monthly Official Export → Ingest → Archive → Review
Purpose: Process official OpenAI exports into searchable archives and a redacted `memory_candidates.md` for manual curation.

### B) Memory-at-Source (Card Scaffolding)
Purpose: Author atomic truths directly in-repo. Use the scaffolder to create/update Memory Cards, then (optional) paste a short “remember this” to the model.

### C) Backup & Snapshots
Purpose: Deterministic, hash-verified snapshots; tag to publish a release artifact.

### D) Restore Package Generation
Purpose: Build ordered, chunked restore packages; run Persona Integrity Check post-paste.

## Tooling

- `tools/ingest_chatgpt_export.py` — Import and normalize official exports
- `tools/memory_card_scaffolder.py` — Create and update Memory Cards (author-first)
- `tools/charlotte_restore_builder.py` — Build paste-ready restore packages

## Test Battery

Minimal tests to validate pipeline components:

- Ingest
- Scaffolder
- Restore
- Snapshot

## Manual Workflows

- Monthly: request OpenAI export → run ingest → curate `charlotte_core/_intake/memory_candidates.md` → convert candidates into Memory Cards via scaffolder
- Ad-hoc: author Memory Cards directly with scaffolder

## Restore Procedure (summary)

1. Build restore package: `python tools/charlotte_restore_builder.py --profile minimal`
2. Paste content into the model
3. Run Persona Integrity Check prompts

## Backup & Tags (summary)

- Snapshots are timestamped under `snapshots/` with a `MANIFEST.json` for integrity
- Tags follow `backup-YYYYMMDD-HHMMSS` when packaging releases

## Troubleshooting (trimmed)

- Patch/routing-confidence topics and automated proposer troubleshooting are removed from this doc. Manual review and scaffolder-based card creation are the recommended remediation steps.

## Notes

- This document intentionally removes Track B automation and the Diff Proposer from operational guidance; historical artifacts may remain in `_intake/` for audit purposes, but do not add new self-dumps.
**Manual Steps**:
