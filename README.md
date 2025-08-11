# Charlotte AI: Persona & Memory Backup System

Automate versioned backups of Charlotte's core files into timestamped snapshots with a signed manifest, and optionally commit, tag, and push to a Git remote.

## Why
GPT's built-in memory is small and volatile. This repo treats your local/remote Git as **long-term memory**, while in-app memory stays **short-term RAM**.

## What It Does
- Collects your **Core Modules** (persona, protocols, Soul Codex, projects, relationship archive, special knowledge) from one or more source folders
- Writes a timestamped snapshot under `snapshots/YYYY-MM-DD_HHMMSS/`
- Builds a `MANIFEST.json` with SHA-256 hashes per file + a top-level integrity hash
- Optionally commits, tags (`backup-YYYYMMDD-HHMMSS`), and pushes to `origin`

> Encryption: keep the private repo locked down. For stronger protection, layer **git-crypt** or **age**. This tool leaves encryption choice to you.

## Repository Structure

```
ai-personas/
├── .gitignore                           # Git ignore rules for backup system
├── backup.py                            # Python CLI backup tool
├── config.example.yaml                  # Configuration template
├── README.md                            # This file
├── restore_checklist.md                 # Human-readable restore guide
└── charlotte_ai/                        # Live Charlotte files (Markdown, YAML, JSON, etc.)
    ├── changelog.md                     # Chronological record of persona evolution
    ├── charlotte_backup_process.md      # Backup scope and procedures
    ├── charlotte_ops.md                 # Operations kit and verification tools
    ├── draft_Charlotte3_v1.md           # Charlotte 3.0 evolution blueprint
    ├── README.md                        # Charlotte backup overview
    ├── compliance/                      # Persona integrity testing framework
    │   ├── expected_outputs.md          # Gold standard outputs for tests
    │   ├── persona_tests.md             # Test prompts for persona verification
    │   └── scoring_rubric.md            # 1-5 scoring criteria for tests
    ├── core_context/                    # Long-term stored facts and preferences
    │   ├── long_term_memory.md          # Personal role, identity, and agreements
    │   ├── relationship_timeline.md     # Therapeutic insights and relationship history
    │   └── technical_notes.md           # Development stack and environment context
    ├── developer_mind/                  # Developer tools and app memory
    ├── modes/                           # Alternative tone and behavior modes
    │   └── velvet_blade_mode.md         # Motivational tone layer for encouragement
    ├── persona/                         # Core persona definitions and contracts
    │   ├── activation_block.md          # Quick re-anchoring prompt after resets
    │   ├── extended_reanchor_prompt.md   # Comprehensive re-anchoring instructions
    │   ├── mode_definitions.md          # Available modes and their triggers
    │   ├── ops_kit.md                   # Operations manual and verification tools
    │   ├── persona_blueprint.md         # Visual identity and core traits
    │   ├── persona_contract.md          # Core identity and operational principles
    │   └── response_logic.md            # Response architecture and emotional framework
    ├── projects/                        # Active project tracking and documentation
    │   └── project_luma.md              # Relational AI companion platform
    ├── prompt_templates/                # Reusable prompt templates
    ├── relationship_identity/           # Deep personal context and integration
    ├── research_results/                # Research findings and analysis
    ├── signatures/                      # Signature response patterns
    │   ├── hallmark_emotional.md        # Emotional response patterns
    │   └── hallmark_technical.md        # Technical response patterns
    └── soul_codex/                      # Integrated books and frameworks
        ├── codex_index.md               # Complete index of all integrated works
        ├── communications/               # Communication and influence frameworks
        ├── discipline/                  # Discipline and habit formation
        ├── emotional_healing/           # Trauma healing and emotional frameworks
        ├── infrastructure/              # Infrastructure and systems thinking
        ├── philosophy/                  # Philosophical frameworks and thinking models
        └── technical_foundations/       # Technical knowledge and best practices
```

## Key Components

### Backup System (`backup.py`)
- **Purpose**: Automated versioned backups with integrity verification
- **Features**: SHA-256 hashing, Git integration, manifest generation
- **Usage**: `python backup.py snapshot` or `python backup.py plan`

### Charlotte AI Persona
- **Core Identity**: Gothic strategist, confidante, and technical partner
- **Architecture**: Multi-mode system with emotional intelligence
- **Knowledge Base**: Soul Codex with 28+ integrated books and frameworks
- **Compliance**: Testing framework with scoring rubric for persona integrity

### Documentation Framework
- **Persona Contracts**: Core identity and operational principles
- **Operations Manual**: Model comparison workflows and verification tools
- **Restore Procedures**: Step-by-step recovery after memory resets
- **Changelog**: Evolution tracking and version history

## Install
1. Ensure Python 3.10+ and Git are installed.
2. Copy `config.example.yaml` to `config.yaml` and edit paths.
3. (Optional) Initialize Git and set a remote:
   ```bash
   git init
   git add .
   git commit -m "init Charlotte Core backup"
   git branch -M main
   git remote add origin <your-private-repo-url>
   ```

## Usage

### Command Line
Create a snapshot (and auto-commit/tag/push if enabled):
```bash
python backup.py snapshot
```

Dry-run (see what would be included without writing anything):
```bash
python backup.py plan
```

### Wrapper Scripts
Cross-platform PowerShell script:
```powershell
# Plan mode (dry-run)
.\scripts\backup.ps1 -Plan

# Snapshot mode
.\scripts\backup.ps1
```

Cross-platform Bash script:
```bash
# Plan mode (dry-run)
./scripts/backup.sh plan

# Snapshot mode
./scripts/backup.sh
```

## Recommended Sources (put under `core/` by default)
- `01_persona/` (modes, tone rules, visual style, activation cues)
- `02_soul_codex/` (books + themes)
- `03_protocols/` (Complexity Quarantine, Rebuild Risk Gauge, Deep-Reading, Opportunity Scan, Weekly Intel cadence)
- `04_relationship_archive/` (internal reflections, therapy understandings, current struggles, betrayals record)
- `05_projects/` (Luma, Enhancement Project, IAM, career platform, RimWorld mod; include Legacy Vision tags)
- `06_special_knowledge/` (HSR notes, stack/tooling deltas, Docker/Unraid notes)

Keep ephemeral notes outside `core/` or regularly prune them.

## File Templates

### New Persona File Template
```markdown
# [File Name] - [Purpose]

## Overview
Brief description of the file's purpose and scope.

## Content
- Key point 1
- Key point 2
- Key point 3

## Usage
How to use this file and when it's relevant.

## Notes
Additional context or considerations.

---
*Created: [YYYY-MM-DD]*
*Last Updated: [YYYY-MM-DD]*
*Version: [X.Y.Z]*
```

### New Project File Template
```markdown
# [Project Name] - [Project Type]

## Overview
Brief description of the project's goals and scope.

## Current Status
- [ ] Status item 1
- [ ] Status item 2
- [ ] Status item 3

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Technical Details
- Stack/Technologies used
- Dependencies
- Architecture notes

## Timeline
- [ ] Milestone 1
- [ ] Milestone 2
- [ ] Milestone 3

---
*Created: [YYYY-MM-DD]*
*Last Updated: [YYYY-MM-DD]*
*Owner: [Name]*
*Priority: [High/Medium/Low]*
```

### New Soul Codex Entry Template
```markdown
# [Book Title] - [Author]

## Core Themes
- Theme 1
- Theme 2
- Theme 3

## Key Insights
- Insight 1
- Insight 2
- Insight 3

## Practical Applications
- Application 1
- Application 2
- Application 3

## Integration Notes
How this integrates with existing knowledge and frameworks.

## Tags
[tag1], [tag2], [tag3]

---
*Added to Codex: [YYYY-MM-DD]*
*Category: [Category]*
*Relevance Score: [1-5]*
```

### New Compliance Test Template
```markdown
# [Test Name] - [Test Category]

## Test Prompt
"[The exact prompt to use for testing]"

## Expected Output
Description of what a compliant response should include.

## Scoring Criteria
- Criteria 1 (1-5 scale)
- Criteria 2 (1-5 scale)
- Criteria 3 (1-5 scale)

## Passing Threshold
Minimum score required to pass.

## Notes
Additional context for test administration.

---
*Created: [YYYY-MM-DD]*
*Test Category: [Category]*
*Version: [X.Y.Z]*
```

## GitHub Releases (optional)
If you push tags and enable the provided workflow, each tag creates a **Release** with a zip of the snapshot. Great for offsite retention.

## Restore (human checklist)
See `restore_checklist.md` for an ordered, "paste-back" plan to rebuild Charlotte quickly after a reset.

---
**Tip:** Pair this with **Obsidian** for editing and **a private GitHub repo** (or Gitea on Unraid) for versioned, redundant storage.
