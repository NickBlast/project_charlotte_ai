# Charlotte Memory Pipeline — **Operations Manual v1.0**

## Overview

This document describes the complete memory pipeline for Charlotte AI, covering ingestion, processing, backup, and restoration workflows. The pipeline ensures deterministic operations, privacy preservation, and cross-model compatibility.

## Core Principles

- **Repo is canon; Memory is cache.** Truths live in `charlotte_core/**` (repo-first truths)
- **Deterministic operations** with UTC timestamps, SHA-256 hashing, and stable ordering
- **Privacy-first** with selective redaction only in intake candidates and reports
- **Cross-model compatibility** via restore packages that work on ChatGPT, Claude, Gemini, and local LLMs

## Pipeline Architecture (lean)

### A) Monthly Official Export → Ingest → Archive → Review

**Purpose**: Process official OpenAI exports into structured, searchable memory and a redacted `memory_candidates.md` for manual curation.

### B) Memory-at-Source (Card Scaffolding)

**Purpose**: Author atomic truths directly in-repo. Use the scaffolder to create/update Memory Cards, then (optional) paste a short “remember this” to the model.

### C) Backup & Snapshots

**Purpose**: Deterministic, hash-verified snapshots with manifest and tagging.

### D) Restore Package Generation

**Purpose**: Build ordered, chunked restore packages; run Persona Integrity Check after paste.

## Tools

- `tools/ingest_chatgpt_export.py` — Ingest official exports
- `tools/memory_card_scaffolder.py` — Create and maintain Memory Cards (author-first)
- `tools/charlotte_restore_builder.py` — Build restore packages

## Test Battery

Minimal tests to validate pipeline components:

- Ingest
- Scaffolder
- Restore
- Snapshot

## Troubleshooting (trimmed)

- Patch proposals, routing-confidence, and automated proposer troubleshooting are removed; use manual review and scaffolder-based fixes instead.

---

**Note**: The documentation removes Track B and the Diff Proposer from operational guidance; historical artifacts may remain in `_intake/` for audit purposes but do not add new self-dumps.
