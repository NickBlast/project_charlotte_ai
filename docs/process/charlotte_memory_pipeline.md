# Charlotte Memory Pipeline

This document outlines the complete memory management pipeline for Charlotte AI, including automated tools and manual workflows for maintaining, updating, and restoring Charlotte's knowledge base.

## Overview

The Charlotte Memory Pipeline consists of five core tools that automate different aspects of memory management:

1. **Ingest ChatGPT Export** - Process OpenAI data exports into structured formats
2. **Memory Diff Proposer** - Generate proposed changes from memory candidates
3. **Memory Card Scaffolder** - Create new memory cards with proper structure
4. **Restore Package Builder** - Generate paste-ready restoration packages
5. **Documentation & Actions** - Process documentation and automated workflows

## Toolchain: A/B/C Automation

### Track A: ChatGPT Export Ingest (`ingest_chatgpt_export.py`)

**Purpose**: Convert OpenAI account exports into structured Markdown and memory candidates.

**Automated Process**:
- Safely extract ZIP files with path traversal protection
- Parse JSON or HTML export formats
- Convert conversations to structured Markdown
- Sanitize sensitive information
- Generate memory candidates for review

**Manual Steps**:
1. Request monthly data export from OpenAI Privacy Portal
2. Download ZIP file when available
3. Run: `python tools/ingest_chatgpt_export.py --zip ~/Downloads/chatgpt-export.zip`

**Outputs**:
- `imports/chatgpt_export/<YYYY-MM-DD>/` (raw export if ZIP given)
- `archives/chat_exports/<YYYY-MM-DD>/<thread>.md`
- `charlotte_ai/_intake/memory_candidates.md`
- `reports/export_ingest_<YYYY-MM-DD>.md`

### Track B: Memory Diff Proposal (`memory_diff_proposer.py`)

**Purpose**: Convert intake files into proposed patches for the correct modules.

**Automated Process**:
- Route content lines to appropriate modules with confidence scoring
- Generate unified diffs that apply cleanly with `git apply`
- Park low-confidence content in unclassified for manual review

**Manual Steps**:
1. Review generated patches
2. Manually apply or refine as needed
3. Run: `python tools/memory_diff_proposer.py --source candidates --open-pr`

**Routing Heuristics**:
- Persona/tone/modes → `charlotte_ai/persona/**` or `charlotte_ai/modes/**`
- Protocols/workflows → `charlotte_ai/protocols/**`
- Projects → `charlotte_ai/projects/<project>/**`
- Relationship → `charlotte_ai/relationship_identity/**`
- Soul Codex → `charlotte_ai/soul_codex/**`

**Outputs**:
- `reports/memory_diff/<date>/proposed_patches/*.patch`
- `reports/memory_diff/<date>/summary.md`

### Track C: Memory Card Scaffolding (`memory_card_scaffolder.py`)

**Purpose**: Create structured memory cards with proper indexing.

**Automated Process**:
- Generate standardized YAML headers
- Create proper directory structure
- Update category index files
- Ensure unique slugs

**Manual Steps**:
1. Run scaffolder when new truths emerge
2. Fill in card content
3. Commit with `Mem-Intent: <intent_id>`
4. Paste generated Remember prompt

**Usage**:
```bash
python tools/memory_card_scaffolder.py \
  --category persona \
  --title "Core Response Principle" \
  --scope global
```

**Outputs**:
- `charlotte_ai/<module>/memory_cards/<slug>.md`
- Updated `memory_index.md`
- Copy-paste Remember prompt

## Memory Card Ritual

### Creation Process
1. **Identify** new truth or update needed
2. **Scaffold** with `memory_card_scaffolder.py`
3. **Fill** in content sections:
   - Canonical Truth
   - Why This Matters
   - Verification
   - Links
4. **Commit** with `Mem-Intent: <intent_id>`
5. **Paste** Remember prompt for immediate reinforcement

### Card Structure
```markdown
---
title: Short Active Title
intent_id: YYYY-MM-DD-NN
type: memory_card
scope: global|<project>|<mode>
tags: [category, project:<name>, mode:<name>]
updated: YYYY-MM-DD
status: active
---

# Short Active Title

## Canonical Truth

[State the core truth or fact here. Be precise and unambiguous.]

## Why This Matters

[Explain why this truth is important to remember and how it should influence behavior.]

## Verification

[Describe how to verify this truth or when it might need updating.]

## Links

[Related memory cards, documents, or external references.]

---
*Intent ID: YYYY-MM-DD-NN*
*Last Updated: YYYY-MM-DD*
*Status: active*
```

## Weekly Self-Dump Workflow

### Process
1. **Paste** Self-Dump prompt to Charlotte
2. **Save** response to `_intake/memory_self_dump/YYYY-MM-DD.md`
3. **Run** diff proposer: `python tools/memory_diff_proposer.py --source self_dump`
4. **Review** and apply patches
5. **Update** relevant memory cards

### Self-Dump Prompt
```
[Self-Dump Prompt]
Reflect on the past week's interactions and identify any new insights, corrections, or updates to my knowledge base. Focus on:
1. Corrections to existing knowledge
2. New truths or principles discovered
3. Updated preferences or boundaries
4. Project progress or changes
5. Relationship insights or updates

Format as clear, actionable statements suitable for memory card integration.
```

## Monthly Export Ingest

### Process
1. **Request** export from OpenAI Privacy Portal (1st of month)
2. **Download** ZIP when available
3. **Run** ingest tool: `python tools/ingest_chatgpt_export.py --zip <file>`
4. **Review** memory candidates
5. **Process** with diff proposer or manual updates

### Automation
- GitHub Action opens/updates monthly issue
- Reminder to check Privacy Portal
- Link to ingestion process

## Restore Procedure

### Process
1. **Build** restore package: `python tools/charlotte_restore_builder.py --profile minimal`
2. **Paste** content into Custom Instructions or first message
3. **Run** Persona Integrity Check
4. **Verify** core functionality restored

### Profiles
- **Minimal**: Persona DNA + protocols + modes definitions
- **Full**: All knowledge including projects, relationships, special knowledge

### Integrity Check
```
[Integrity Check Prompt]
Verify core identity and functionality:
1. Confirm persona contract and core traits
2. Test response patterns and tone
3. Validate key protocols and workflows
4. Check project context and status
5. Verify relationship context and boundaries

Report any discrepancies or missing elements.
```

## Backup & Tags

### Versioning
- Snapshots tagged with `backup-YYYYMMDD-HHMMSS`
- Memory cards versioned by intent_id
- Export ingest reports for audit trail

### Git Workflow
1. Changes committed with descriptive messages
2. Tags created for significant updates
3. Releases generated for offsite retention
4. Branch protection for main branch

## Security Notes

### Data Protection
- Sensitive information redacted in candidates and reports
- Raw exports preserved for audit trail
- Private repository recommended for storage
- Optional encryption with git-crypt or age

### Access Control
- Repository access limited to authorized personnel
- Regular access reviews
- Audit trail of all changes
- Offsite backup retention

## Troubleshooting

### Common Issues

**No conversations found in export**
- Check export format (JSON or HTML)
- Verify file isn't corrupted
- Ensure export contains conversation data

**Routing confidence too low**
- Review unclassified content manually
- Adjust routing keywords if needed
- Consider creating new categories

**Patch application fails**
- Check target files exist
- Verify patch format matches target
- Manually apply changes if needed

**Memory card slug conflicts**
- Tool automatically appends sequence numbers
- Check for duplicate titles
- Consider more specific naming

### Exit Codes
- `2` - Bad input (fix hint provided)
- `3` - Nothing to do (e.g., 0 files found)
- `4` - Write error (permissions or disk space)

## Manual Workflows

### Monthly
- Request OpenAI Data Export (1st of month)
- Download ZIP when available
- Run `ingest_chatgpt_export.py`

### Weekly
- Paste Self-Dump prompt
- Save to `_intake/memory_self_dump/`
- Run `memory_diff_proposer.py`
- Review patches/PRs

### Whenever
- Run `memory_card_scaffolder.py` for new truths
- Commit with `Mem-Intent: <intent_id>`
- Paste generated Remember prompt

### After Reset
- Run `charlotte_restore_builder.py`
- Paste output to Custom Instructions
- Run Persona Integrity Check
