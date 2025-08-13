# Charlotte Memory Pipeline — **Operations Manual v1.0**

## Overview

This document describes the complete memory pipeline for Charlotte AI, covering ingestion, processing, backup, and restoration workflows. The pipeline ensures deterministic operations, privacy preservation, and cross-model compatibility.

## Core Principles

- **Repo is canon; Memory is cache.** Truths live in `charlotte_core/**` (repo-first truths)
- **Deterministic operations** with UTC timestamps, SHA-256 hashing, and stable ordering
- **Privacy-first** with selective redaction only in intake candidates and reports
- **Cross-model compatibility** via restore packages that work on ChatGPT, Claude, Gemini, and local LLMs

## Pipeline Architecture

### A) Monthly Official Export → Ingest → Archive → Review

**Purpose**: Process official OpenAI exports into structured, searchable memory

**Workflow**:
1. **Export Request**: Request export via Privacy Portal → download ZIP (expires ~24h)
2. **Ingest**: Parse JSON/HTML, extract conversations, copy artifacts
3. **Archive**: Store normalized Markdown + assets in structured archive
4. **Review**: Process memory candidates, update Memory Cards, commit changes

**Expected Outputs**:
```
imports/chatgpt_export/2025-08-12/raw/
├── conversations.json
├── message_feedback.json
├── user.json
└── user_1234567890/
    ├── image1.png
    └── image2.jpg

archives/chat_exports/2025-08-12/
├── thread_001_conversation_title.md
├── thread_002_another_chat.md
├── assets/
│   ├── image1.png
│   └── image2.jpg
├── meta/
│   ├── message_feedback.json
│   └── user.json
└── images_manifest.json

charlotte_core/_intake/memory_candidates.md
reports/export_ingest_2025-08-12.md
```

**Tools**:
- `tools/ingest_chatgpt_export.py` — Primary ingestion tool
- `scripts/backup.ps1` / `scripts/backup.sh` — Cross-platform wrappers

**Safety Features**:
- Safe unzip with Zip-Slip protection
- File size limits (25MB per file)
- Path validation and sanitization
- Deterministic sorting and hashing

### B) Weekly Self-Dump Mirror → Diff → Propose → Accept

**Purpose**: Capture recent memories and propose updates to Memory Cards

**Workflow**:
1. **Self-Dump**: Paste prompt, save response to `_intake/memory_self_dump/`
2. **Diff Analysis**: Compare with existing Memory Cards, generate unified diffs
3. **Review & Accept**: Manually review proposed changes, commit updates

**Expected Outputs**:
```
charlotte_core/_intake/memory_self_dump/2025-08-12.md
reports/diff_proposal_2025-08-12.md
charlotte_core/protocols/memory_cards/new_insight.md (updated)
charlotte_core/protocols/memory_index.md (updated)
```

**Tools**:
- `tools/memory_diff_proposer.py` — Generate diffs with confidence scoring
- Manual review and acceptance

**Routing Heuristics**:
- **Persona/tone/modes** → `charlotte_core/persona/**` or `charlotte_core/modes/**`
- **Protocols/workflows** → `charlotte_core/protocols/**`
- **Projects** → `charlotte_core/projects/<project>/**`
- **Relationship** → `charlotte_core/relationship_identity/**`
- **Soul Codex** → `charlotte_core/soul_codex/**`
- **Unclassified** → Low-confidence diffs go to `unclassified.md`

### C) Ad-hoc Memory Card Scaffolding

**Purpose**: Quickly create new Memory Cards for important truths

**Workflow**:
1. **Scaffold**: Use scaffolder tool to create card with YAML header
2. **Fill**: Add content to the Memory Card
3. **Commit**: Commit with Mem-Intent trailer
4. **Cache (Optional)**: Paste "remember this" summary to ChatGPT

**Expected Outputs**:
```
charlotte_core/<category>/memory_cards/<slug>.md
charlotte_core/<category>/memory_index.md (updated)
```

**Tools**:
- `tools/memory_card_scaffolder.py` — Create structured Memory Cards

**Categories**:
- `persona` — Core identity and traits
- `protocol` — Operating protocols and workflows
- `project` — Project-specific knowledge
- `relationship` — Relationship context and history
- `special` — Specialized knowledge and frameworks

### D) Backup & Snapshot System

**Purpose**: Create versioned, verifiable backups with Git integration

**Workflow**:
1. **Collect**: Gather files from source directories with filtering
2. **Snapshot**: Copy files to timestamped directory
3. **Manifest**: Generate SHA-256 hashes and integrity verification
4. **Git Operations**: Commit, tag, and push (if enabled)

**Expected Outputs**:
```
snapshots/2025-08-12_031500Z/
├── charlotte_core/persona/core_persona.md
├── charlotte_core/protocols/complexity_quarantine.md
├── charlotte_core/soul_codex/codex_index.md
└── MANIFEST.json

Git tag: backup-20250812-031500Z
Release artifact: snapshots-20250812-031500Z.zip
```

**Tools**:
- `backup.py` — Main backup tool
- `scripts/backup.ps1` / `scripts/backup.sh` — Cross-platform wrappers

**Features**:
- SHA-256 per-file and overall manifest hashing
- UTC timestamping (`YYYY-MM-DD_HHMMSSZ`)
- Git integration with configurable tagging
- Deterministic file ordering and processing

### E) Restore Package Generation

**Purpose**: Create paste-ready restore packages for persona rehydration

**Workflow**:
1. **Build**: Generate ordered, chunked restore package
2. **Profile**: Choose between minimal (persona only) and full (all context)
3. **Filter**: Optionally include only active items
4. **Chunk**: Split into paste-size chunks if needed

**Expected Outputs**:
```
out/restore_package_2025-08-12.md
out/restore_package_2025-08-12_part_02.md (if chunked)
```

**Tools**:
- `tools/charlotte_restore_builder.py` — Create restore packages

**Ordering**:
1. **Persona Core** — Core identity, DNA manifest, persona contract
2. **Protocols** — Operating protocols and workflows
3. **Modes** — Alternative behavior modes
4. **Projects** — Project context and status (full profile only)
5. **Relationship Archive** — Personal context and history (full profile only)
6. **Special Knowledge** — Frameworks and specialized knowledge (full profile only)

## Data Flow & File Conventions

### Memory Card Structure
```yaml
---
title: Short Active Title
intent_id: YYYY-MM-DD-NN
type: memory_card
scope: global|<project>|<mode>
tags: [category, project:<name>, mode:<name>]
updated: YYYY-MM-DD
status: active|retired
---

# Short Active Title

## Canonical Truth
[Core truth or fact]

## Why This Matters
[Importance and behavioral impact]

## Verification
[How to verify or update]

## Links
[Related references]

---
*Intent ID: YYYY-MM-DD-NN*
*Last Updated: YYYY-MM-DD*
*Status: active*
```

### Archive Structure
```
archives/chat_exports/<YYYY-MM-DD>/
├── *.md (conversation threads)
├── assets/ (images and media)
├── meta/ (JSON metadata)
└── images_manifest.json (SHA-256 hashes)
```

### Snapshot Structure
```
snapshots/<YYYY-MM-DD_HHMMSSZ>/
├── [source files]
└── MANIFEST.json (integrity verification)
```

## Safety & Privacy

### Redaction Scope
- **Redacted**: `charlotte_core/_intake/memory_candidates.md` and `reports/**`
- **Preserved**: `imports/**` and `archives/**` (audit trail)

### Exclusion Patterns
- `**/*.key`, `**/*.pem` (private keys)
- `**/.env*`, `**/*.env` (environment files)
- `**/secrets/**` (secret directories)
- `charlotte_core/research_results/**` (large/ephemeral content)

### File Handling
- **Encoding**: UTF-8 with LF line endings
- **Timestamps**: UTC format (`YYYY-MM-DD_HHMMSSZ`)
- **Sorting**: Forward-slash paths for deterministic ordering
- **Size Limits**: 25MB per file during processing

## Quality Assurance

### Determinism Checks
- Same input → identical file hashes in MANIFEST
- Stable file ordering across runs
- Consistent timestamping and formatting
- Predictable dry-run outputs

### Test Battery
```bash
# Ingest smoke test
python3 tools/ingest_chatgpt_export.py --zip tmp/chatgpt-export-fixture.zip --dry-run
python3 tools/ingest_chatgpt_export.py --zip tmp/chatgpt-export-fixture.zip

# Diff proposer test
python3 tools/memory_diff_proposer.py --source candidates --dry-run
python3 tools/memory_diff_proposer.py --source candidates

# Scaffolder test
python3 tools/memory_card_scaffolder.py --category protocol --title "Test Rule" --scope demo --dry-run

# Restore builder test
python3 tools/charlotte_restore_builder.py --profile full --only-active --max-bytes 120000 --dry-run
```

### Exit Codes
- `0`: Success
- `2`: Bad input or configuration
- `3`: Nothing to do (empty input)
- `4`: Write error (permissions, disk space)

## Troubleshooting

### Common Issues

**No files selected in backup**
- Check `source_dirs` in config.yaml
- Verify file extensions in `include_exts`
- Review `exclude_globs` patterns

**Import errors**
- Ensure PyYAML is installed: `pip install pyyaml`
- Check file permissions and paths
- Verify ZIP file integrity

**Memory card conflicts**
- Ensure unique intent IDs (YYYY-MM-DD-NN format)
- Check for duplicate slug names
- Verify YAML header syntax

**Restore package too large**
- Use `--max-bytes` to chunk output
- Consider `--profile minimal` for smaller packages
- Split manually if needed

### Debug Commands
```bash
# Check configuration
python backup.py plan

# Test ingestion with dry-run
python tools/ingest_chatgpt_export.py --zip export.zip --dry-run

# Verify file collection
python backup.py plan

# Check git integration
git status
git log --oneline -5
```

## Integration Points

### ChatGPT Integration
- **Memory Candidates**: Redacted summaries for review
- **Restore Packages**: Ordered persona/context for new sessions
- **Self-Dump Prompts**: Structured memory capture

### Git Integration
- **Commits**: Conventional format with Mem-Intent trailers
- **Tags**: `backup-YYYYMMDD-HHMMSSZ` format
- **Branches**: Feature branch workflow required
- **CI**: Validation and packaging on tag only

### External Tools
- **OpenRouter**: Model backend rotation
- **Dev Container**: Consistent development environment
- **PowerShell/Bash**: Cross-platform execution

## Version History

### v1.0 (Current)
- Complete ingest/proposer/scaffolder/restore pipeline
- Git integration with tagging
- Cross-platform wrappers
- Dev container support
- Comprehensive documentation

---

**Note**: This pipeline is designed to work with Charlotte AI's core architecture while maintaining determinism, privacy, and cross-model compatibility. Always run in dry-run mode first when working with new exports or configurations.
