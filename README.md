# Charlotte AI: Persona & Memory Backup System

Automate versioned backups of Charlotte's core files into timestamped snapshots with a signed manifest, and optionally commit, tag, and push to a Git remote.

## Why

GPT's built-in memory is small and volatile. This repo treats your local/remote Git as **long-term memory**, while in-app memory stays **short-term RAM**.

## What It Does

- Collects your **Core Modules** (persona, protocols, Soul Codex, projects, relationship archive, special knowledge) from one or more source folders
- Writes a timestamped snapshot under `snapshots/YYYY-MM-DD_HHMMSSZ/`
- Builds a `MANIFEST.json` with SHA-256 hashes per file + a top-level integrity hash
- Optionally commits, tags (`backup-YYYYMMDD-HHMMSSZ`), and pushes to `origin`

> **Encryption**: Keep the private repo locked down. For stronger protection, layer **git-crypt** or **age**. This tool leaves encryption choice to you.

## Repository Structure

```
project_charlotte_ai/
├── .gitignore                           # Git ignore rules for backup system
├── backup.py                            # Python CLI backup tool
├── config.example.yaml                  # Configuration template
├── README.md                            # This file
├── restore_checklist.md                 # Human-readable restore guide
└── charlotte_core/                        # Live Charlotte files (Markdown, YAML, JSON, etc.)
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

## Installation

### Prerequisites
- Python 3.10+ and Git installed
- Private Git repository (recommended for security)

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/project_charlotte_ai.git
   cd project_charlotte_ai
   ```

2. **Configure the system**:
   ```bash
   cp config.example.yaml config.yaml
   # Edit config.yaml with your paths and preferences
   ```

3. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "init Charlotte Core backup"
   git branch -M main
   git remote add origin <your-private-repo-url>
   ```

4. **Install dependencies**:
   ```bash
   pip install pyyaml
   ```

## Usage Guide

### 1. Backup Operations

#### Create a Snapshot
```bash
# Create backup with automatic Git operations
python backup.py snapshot

# Preview what would be backed up (dry run)
python backup.py plan
```

#### Cross-Platform Wrappers
**Windows (PowerShell)**:
```powershell
# Plan mode (dry-run)
.\scripts\backup.ps1 -Plan

# Snapshot mode
.\scripts\backup.ps1
```

**Linux/macOS (Bash)**:
```bash
# Plan mode (dry-run)
./scripts/backup.sh plan

# Snapshot mode
./scripts/backup.sh
```

#### Configuration Options
Edit `config.yaml` to customize:
```yaml
repo_root: "."                    # Repository root directory
source_dirs:                      # Directories to backup
  - "charlotte_core"
include_exts:                     # File extensions to include
  - ".md"
  - ".yaml"
  - ".yml"
  - ".json"
exclude_globs:                    # Patterns to exclude
  - "**/temp/**"
  - "**/.git/**"
git:                             # Git integration settings
  enable: true
  tag: true
  push: true
  commit_message: "chore: Charlotte snapshot"
```

### 2. Memory Pipeline Operations

#### Monthly Official Export Processing
**Purpose**: Process OpenAI ChatGPT exports into structured memory

**Steps**:
1. **Request Export**: Go to OpenAI Privacy Portal → request export → download ZIP
2. **Ingest Export**:
   ```bash
   # Using Python tool directly
   python tools/ingest_chatgpt_export.py --zip chatgpt-export.zip
   
   # Or using PowerShell wrapper
   .\scripts\ingest.ps1 -ZipPath chatgpt-export.zip
   ```

3. **Review and Process**:
   - Check `charlotte_core/_intake/memory_candidates.md` for redacted summaries
   - Use `tools/memory_diff_proposer.py` to suggest Memory Card updates
   - Review and accept proposed changes
   - Commit changes with `Mem-Intent:` trailer

**Expected Outputs**:
```
archives/chat_exports/2025-08-12/
├── thread_001_conversation_title.md
├── thread_002_another_chat.md
├── assets/ (images and media)
├── meta/ (JSON metadata)
└── images_manifest.json

charlotte_core/_intake/memory_candidates.md
reports/export_ingest_2025-08-12.md
```

#### Weekly Self-Dump Mirror
**Purpose**: Capture recent memories and update Memory Cards

**Steps**:
1. **Generate Self-Dump Prompt**:
   ```bash
   python tools/charlotte_restore_builder.py --profile minimal --dry-run
   ```

2. **Execute Self-Dump**: Paste the prompt into ChatGPT, save response to:
   ```
   charlotte_core/_intake/memory_self_dump/2025-08-12.md
   ```

3. **Propose Updates**:
   ```bash
   python tools/memory_diff_proposer.py --source self_dump
   ```

4. **Review and Accept**: Manually review proposed changes, commit updates

#### Ad-hoc Memory Card Creation
**Purpose**: Quickly create Memory Cards for important truths

**Steps**:
```bash
# Create a new Memory Card
python tools/memory_card_scaffolder.py \
  --category protocol \
  --title "New Protocol Name" \
  --scope global \
  --description "Brief description"

# Scaffold with dry-run to preview
python tools/memory_card_scaffolder.py \
  --category project \
  --title "Project Name" \
  --scope demo \
  --dry-run
```

**Categories**:
- `persona` - Core identity and traits
- `protocol` - Operating protocols and workflows  
- `project` - Project-specific knowledge
- `relationship` - Relationship context and history
- `special` - Specialized knowledge and frameworks

### 3. Restore Operations

#### Build Restore Package
**Purpose**: Create paste-ready persona restoration package

**Commands**:
```bash
# Full profile (all context)
python tools/charlotte_restore_builder.py --profile full

# Minimal profile (persona only)
python tools/charlotte_restore_builder.py --profile minimal

# Only active items
python tools/charlotte_restore_builder.py --only-active

# Custom chunk size (default: 120000 bytes)
python tools/charlotte_restore_builder.py --max-bytes 60000

# Dry run to preview
python tools/charlotte_restore_builder.py --profile full --dry-run
```

**Usage**:
1. Restore package will be created in `out/restore_package_YYYY-MM-DD.md`
2. If larger than chunk size, will be split into multiple parts
3. Paste content into ChatGPT Custom Instructions or first message
4. Run Persona Integrity Check to verify restoration

#### Restore Process
1. **Build Package**: Use restore builder with appropriate profile
2. **Paste Content**: Copy package content into new ChatGPT session
3. **Verify Integrity**: Run persona protocols and checks
4. **Reinject Missing**: If any sections are missing, manually add them

### 4. Quality Assurance

#### Testing
Run the minimal test battery to verify system functionality:
```bash
# Ingest smoke test
python3 tools/ingest_chatgpt_export.py --zip tmp/chatgpt-export-fixture.zip --dry-run

# Diff proposer test
python3 tools/memory_diff_proposer.py --source candidates --dry-run

# Scaffolder test
python3 tools/memory_card_scaffolder.py --category protocol --title "Test Rule" --scope demo --dry-run

# Restore builder test
python3 tools/charlotte_restore_builder.py --profile full --only-active --max-bytes 120000 --dry-run
```

#### Validation
- **Determinism**: Same inputs should produce identical outputs
- **Privacy**: Verify redaction only appears in candidates and reports
- **Integrity**: Check MANIFEST hashes match actual files
- **Compatibility**: Test restore packages work across different AI models

## Recommended Sources (put under `charlotte_core/` by default)

### Core Structure
- `01_persona/` (modes, tone rules, visual style, activation cues)
- `02_soul_codex/` (books + themes)
- `03_protocols/` (Complexity Quarantine, Rebuild Risk Gauge, Deep-Reading, Opportunity Scan, Weekly Intel cadence)
- `04_relationship_archive/` (internal reflections, therapy understandings, current struggles, betrayals record)
- `05_projects/` (Luma, Enhancement Project, IAM, career platform, RimWorld mod; include Legacy Vision tags)
- `06_special_knowledge/` (HSR notes, stack/tooling deltas, Docker/Unraid notes)

### File Management
- Keep ephemeral notes outside `charlotte_core/` or regularly prune them
- Use consistent file templates for new content
- Follow the Memory Card structure for important truths

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

### Memory Card Template
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

## GitHub Releases (Optional)

If you push tags and enable the provided workflow, each tag creates a **Release** with a zip of the snapshot. Great for offsite retention.

## Restore Process (Human Checklist)

See `restore_checklist.md` for an ordered, "paste-back" plan to rebuild Charlotte quickly after a reset.

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

## Best Practices

### Security
- Use a private Git repository
- Never commit sensitive information
- Regularly audit redaction patterns
- Consider additional encryption layers (git-crypt, age)

### Maintenance
- Run monthly export ingest regularly
- Keep Memory Cards updated and organized
- Monitor backup sizes and storage usage
- Test restore packages periodically

### Workflow
- Always use dry-run mode first
- Follow conventional commit format
- Include Mem-Intent trailers for memory changes
- Keep feature branches separate from main

## Integration with External Tools

### Development Environment
- **Dev Container**: Use provided Docker setup for consistent development
- **IDE**: Configure with Python extensions and markdown preview
- **Git**: Use branch protection and PR workflows

### AI Model Compatibility
- **ChatGPT**: Primary target with Memory feature
- **Claude**: Compatible via restore packages
- **Gemini**: Compatible via restore packages
- **Local LLMs**: Compatible via restore packages and file uploads

### Automation
- **CI/CD**: Use provided workflows for validation and release packaging
- **Scripts**: PowerShell and Bash wrappers for cross-platform usage
- **Scheduling**: Set up regular backup operations via cron/task scheduler

## Contributing

1. Follow the development workflow in `docs/process/cline_rules.md`
2. Use feature branches for all changes
3. Include comprehensive tests for new functionality
4. Update documentation and changelog with every change
5. Request review from project maintainers

## License and Support

This project is designed for personal use and development. For support and contributions, please refer to the project documentation and open issues in the repository.

---

**Tip**: Pair this with **Obsidian** for editing and **a private GitHub repo** (or Gitea on Unraid) for versioned, redundant storage.
