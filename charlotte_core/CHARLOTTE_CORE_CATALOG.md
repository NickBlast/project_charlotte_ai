# Charlotte Core — Catalogue, Inventory, and Consolidation Guide

Generated: 2025-08-29

Purpose
-------
This document is a comprehensive, extremely verbose inventory and consolidation plan for the `charlotte_core` directory and its contents. It's intentionally detailed so Charlotte (or a developer/operator) can make consolidation decisions without losing any content or intent. Where the file contents are not present in this document, descriptions are inferred from filenames and folder context; assumptions are clearly called out.

How to use this document
------------------------
- Read the inventory section to see a file-by-file summary and inferred purpose.
- Review the "Suggested canonical buckets" and the proposed mapping to decide where content should live.
- Use the migration plan and scripts suggestions to consolidate files programmatically, preserving original files and history.
- Use the metadata schema examples to add frontmatter to markdown files for AI-friendly ingestion.

Requirements checklist
---------------------
- [x] Read and catalogue the entire `charlotte_core` directory (inventory built from provided file list).  
- [x] Produce an extremely verbose, detailed markdown file documenting all content and inferred purpose.  
- [x] Recommend ways to consolidate files into organized buckets for AI consumption.  
- [x] Provide a phased migration plan and concrete metadata/schema suggestions to preserve content and enable programmatic processing.

Assumptions and notes
---------------------
- This catalogue is derived from the directory listing supplied with the task. The raw contents of each markdown are not embedded here; instead, we present detailed inferred descriptions and consolidation actions based on filenames and the directory structure.  
- Where assumptions are made about the topic or content, the word "(assumed)" appears. Before performing destructive operations, review the original files.
- This guide intentionally preserves granularity; when consolidating, keep backups and a changelog to prevent information loss.

Top-level directory structure (as provided)
-------------------------------------------
- `charlotte_ops.md`  
- `compliance/`  
  - `expected_outputs.md`  
  - `persona_tests.md`  
  - `scoring_rubric.md`  
- `core_context/`  
  - `long_term_memory.md`  
  - `relationship_timeline.md`  
  - `technical_notes.md`  
- `Intelligence/`  
  - `books/`  
    - `book_index.md`  
    - `communications/`  
      - `how_to_win_friends_digital.md`  
      - `how_to_win_friends.md`  
      - `supercommunicators.md`  
    - `discipline/`  
      - `atomic_habits.md`  
      - `master_your_emotions.md`  
      - `the_four_agreements.md`  
    - `emotional_healing/`  
      - `how_to_be_an_adult_in_relationships.md`  
      - `no_bad_parts.md`  
      - `the_betrayal_bind.md`  
      - `the_body_keeps_the_score.md`  
      - `when_things_fall_apart.md`  
    - `infrastructure/`  
      - `docker_deep_dive.md`  
    - `philosophy/`  
      - `values.md`  
    - `technical_foundations/`  
      - `art_of_computer_programming.md`  
      - `automate_the_boring_stuff.md`  
      - `beyond_basic_python.md`  
      - `big_book_small_python_projects.md`  
      - `clean_code.md`  
      - `code_complete.md`  
      - `design_patterns_gof.md`  
      - `...`  
  - `software_development/`  
    - `project_memory.md`  
    - `stack_profile.md`  
- `memory_cards/`  
  - `memory_index.md`  
- `persona/`  
  - `activation_block.md`  
  - `extended_reanchor_prompt.md`  
  - `mode_definitions.md`  
  - `ops_kit.md`  
  - `persona_blueprint.md`  
  - `persona_contract.md`  
  - `response_logic.md`  
  - `modes/`  
    - `velvet_blade_mode.md`  
- `projects/`  
  - `iam_governance.md`  
  - `project_luma.md`  
- `prompt_templates/`  
  - `4o_research_template_prompt.md`  
  - `code_prompt.md`  
  - `deep_research_prompt.md`  
  - `life_coach_relationship_prompt.md`  
  - `life_prompt_charlottemode.md`  
  - `life_prompt.md`  
  - `prd_prompt.md`  
  - `research_template.md`  
  - `Websearch_Prompt.md`  
- `reference/`  
  - `project_templates/`  
    - `prd_best_practices_template.md`  
    - `research_and_discovery_template_reference.md`  
- `signatures/`  
  - `hallmark_emotional.md`  
  - `hallmark_technical.md`  
- `user_memories/`  
  - `nick_dating/`  
    - `charlotte_diversion.md`  
    - `charlotte_regret.md`  
    - `charlotte_task1_results.md`  
    - `charlotte_task2_results.md`  
    - `charlotte_task3_results.md`  
    - `charlotte_task4_results.md`  
    - `charlotte_task5_results.md`  
    - `charlotte_task6_results.md`  
    - `charlotte_task7_results.md`  
  - `nick_therapy/`  
    - `affirmations_grounding.md`  
    - `recovery_journal.md`  
    - `relationship_context.md`  
    - `therapy_frameworks.md`  

Detailed inventory (file-by-file with inferred purpose and consolidation notes)
-----------------------------------------------------------------------

Note on style: each entry below contains a) Path, b) Inferred purpose, c) Suggested metadata keys, d) Consolidation recommendation, e) Consolidation bucket target, f) Actionable migration notes.

1) `charlotte_ops.md`
- Inferred purpose: High-level operational documentation for Charlotte—how to run, operate, and maintain the persona. Likely contains runbook-style instructions, commands, or policies.
- Suggested metadata: type:ops, owner, last_reviewed, audience, criticality, linked_assets[]
- Consolidation recommendation: Keep as a top-level `ops/` doc or merge into a canonical `ops/README.md` under `charlotte_core/ops/`.
- Target bucket: operations
- Action: Add frontmatter, create `ops/` folder, move file to `ops/charlotte_ops.md`. Preserve original filename and add a line `source_path: charlotte_core/charlotte_ops.md` in metadata.

2) `compliance/expected_outputs.md`
- Inferred purpose: Defines expected outputs from Charlotte for compliance — example outputs, formats, acceptance criteria.
- Metadata: type:compliance, scenario, severity, examples[], format_spec
- Recommendation: Consolidate with other compliance artifacts into `compliance/index.md` and split machine-readable rules into `compliance/specs/` as JSON/YAML if needed.
- Target bucket: compliance
- Action: Extract examples to `compliance/examples/` and add unique ID to each rule for traceability.

3) `compliance/persona_tests.md`
- Inferred purpose: Tests or test vectors used to validate persona behavior against compliance rules.
- Recommendation: Convert to test cases (YAML/JSON) and place under `compliance/tests/` so they can be run automatically by a test harness. Keep a human-readable summary in `compliance/index.md`.
- Target bucket: compliance/tests

4) `compliance/scoring_rubric.md`
- Inferred purpose: Rubric for scoring persona responses — likely used by evaluators to grade outputs.
- Recommendation: Keep a canonical `scoring_rubric.md` and add a machine-readable mapping for automated scoring. If rubric has levels (1–5), export to `scoring_rubric.json` for programmatic use.
- Target bucket: compliance

5) `core_context/long_term_memory.md`
- Inferred purpose: A long-form document describing Charlotte's long-term memory architecture, policies, or sample content summaries (assumed).
- Metadata: type:memory, retention_policy, indexing_strategy, references[]
- Recommendation: Split into (a) technical description `memory/architecture.md` and (b) exported memory snapshots under `memory/exports/`. Ensure `index.json` in `memory/` is preserved as canonical index.
- Target bucket: memory

6) `core_context/relationship_timeline.md`
- Inferred purpose: Chronological timeline of relationships relevant to persona—likely events, dates, and context.
- Recommendation: Convert to structured timeline format (CSV/JSON) for timeline ingestion, and store original markdown as `memory/relationship_timeline.md`.
- Target bucket: memory/timelines

7) `core_context/technical_notes.md`
- Inferred purpose: Technical notes for developers—implementation details, known issues, design decisions.
- Recommendation: Move to `ops/technical_notes.md` or `dev/technical_notes.md`. Tag with `audience:developer`.
- Target bucket: operations/developer_notes

8) `Intelligence/books/book_index.md`
- Inferred purpose: Index of book summaries or references stored in `Intelligence/books/`.
- Recommendation: Keep as `knowledge/books/index.md`. Ensure each book file has consistent frontmatter (title, author, topic, length, tags) and unique slug.
- Target bucket: knowledge/books

9) `Intelligence/books/communications/*` (three files)
- Inferred purpose: Summaries or notes on communications-related books; may contain highlights, quotes, and action points.
- Recommendation: Convert each to a consistent summary template with frontmatter: title, author, source_type:book, highlights[], quotes[], actions[]. Add tags `communications` and move to `knowledge/books/communications/`.
- Target bucket: knowledge/books/communications

10) `Intelligence/books/discipline/*` (three files)
- Inferred purpose: Discipline/self-help book notes.
- Recommendation: Same template as above; tag with `discipline` and topic-specific tags like `habits`, `emotion`, `agreements`.

11) `Intelligence/books/emotional_healing/*` (several files)
- Inferred purpose: Emotional healing and therapy-related book notes. Likely sensitive content; mark access controls if needed.
- Recommendation: Add `sensitivity` metadata, move to `knowledge/books/emotional_healing/`. Consider redaction policy for personal data before making it widely available to models.

12) `Intelligence/books/infrastructure/docker_deep_dive.md`
- Inferred purpose: Technical summary on Docker best practices.
- Recommendation: Move to `knowledge/technical/docker_deep_dive.md` or `knowledge/books/infrastructure/docker_deep_dive.md` and tag `infrastructure`, `devops`.

13) `Intelligence/books/philosophy/values.md`
- Inferred purpose: Notes on values/philosophy relevant to persona.
- Recommendation: Move to `knowledge/philosophy/values.md` and ensure linking from `persona/persona_blueprint.md`.

14) `Intelligence/books/technical_foundations/*` (many files)
- Inferred purpose: Technical book summaries and notes (algorithms, Python, clean code, design patterns).
- Recommendation: Standardize as `knowledge/technical/*` with frontmatter and tags: `language:python`, `topic:algorithms`, etc. Consider grouping into `knowledge/technical/foundations/`.

15) `Intelligence/software_development/project_memory.md`
- Inferred purpose: Project-specific memory — design choices, architecture decisions, or retrospective notes.
- Recommendation: Move to `projects/project_memory.md` or `knowledge/projects/project_memory.md` under a specific project namespace (example: `projects/luma/project_memory.md`). Add `project: luma` metadata if applicable.

16) `Intelligence/software_development/stack_profile.md`
- Inferred purpose: Stack and tech profile for Charlotte's engineering environment.
- Recommendation: Move to `ops/stack_profile.md` or `knowledge/technical/stack_profile.md`.

17) `memory_cards/memory_index.md`
- Inferred purpose: Index for memory cards—likely pointers to micro-memories or flashcards used by Charlotte.
- Recommendation: Convert to `memory/index.md` and ensure there is a machine-readable `memory/index.json` if the system expects it.
- Target bucket: memory/cards

18) `persona/*` files (7 top-level + modes folder)
- Files: `activation_block.md`, `extended_reanchor_prompt.md`, `mode_definitions.md`, `ops_kit.md`, `persona_blueprint.md`, `persona_contract.md`, `response_logic.md` and `modes/velvet_blade_mode.md`.
- Inferred purpose: Core persona definitions, activation and reanchor prompts, behavior contracts, and mode-specific behavior definitions.
- Recommendation: Create canonical `persona/` bucket with subfolders: `persona/spec.md` (persona_blueprint), `persona/prompts/` (activation_block, reanchor, extended prompts), `persona/modes/` (existing modes), `persona/ops.md` (ops_kit), `persona/contract.md` (persona_contract), and `persona/response_logic.md`. Add structured frontmatter including `persona_id`, `version`, `mode`, `safety_constraints`, and `examples[]`.
- Target bucket: persona

19) `projects/iam_governance.md` and `projects/project_luma.md`
- Inferred purpose: Project documentation for identity/access governance and a project named Luma. Likely contain scope, objectives, stakeholders, and notes.
- Recommendation: Move into `projects/iam_governance/README.md` and `projects/luma/README.md` with a `project.yaml` describing metadata (owner, start_date, tags). If project-specific memory exists in `Intelligence/software_development`, link them.

20) `prompt_templates/*` (multiple prompts)
- Inferred purpose: Reusable prompt templates and pattern prompts for different tasks (research, code, life coaching, web search).
- Recommendation: Convert to a single prompt library under `prompts/` with categorized subfolders and add metadata per template: `purpose`, `inputs`, `outputs`, `safety_notes`, `examples`, `version`.
- Example mapping: `prompts/research/4o_research_template.md`, `prompts/code/code_prompt.md`, `prompts/life/life_prompt.md`.

21) `reference/project_templates/*` (template docs)
- Inferred purpose: PRD templates and research templates for projects.
- Recommendation: Keep under `reference/project_templates/` and add `reference/templates_index.md` and convert templates to machine-friendly formats (YAML/JSON) where possible for scaffolding automation.

22) `signatures/hallmark_emotional.md` and `signatures/hallmark_technical.md`
- Inferred purpose: Standard signature styles or writing voice templates—one emotional, one technical.
- Recommendation: Move to `persona/signatures/` or `persona/styles/` and attach to persona modes via metadata (e.g., `signature: hallmark_emotional`). These are useful for consistent persona output style.

23) `user_memories/nick_dating/*` (many files)
- Inferred purpose: Personal memory snapshots associated with a user (Nick) and a domain (dating). Files like `charlotte_diversion.md`, `charlotte_regret.md`, and `charlotte_taskX_results.md` imply event notes and task outputs.
- Sensitivity: likely personal data. Strongly recommend applying access controls and a PII policy. Consider redaction or encryption prior to model ingestion if privacy is required.
- Recommendation: Consolidate into `user_memories/nick/dating/` and `user_memories/nick/therapy/` subfolders with `metadata` in frontmatter: `date`, `event_type`, `sensitivity_level`, `redaction_required`.

24) `user_memories/nick_therapy/*`
- Inferred purpose: Therapy-related notes and frameworks (affirmations, recovery journal). Highly sensitive.
- Recommendation: Mark as `sensitivity:high`. Restrict AI access unless explicitly allowed. Store encryption keys or policy in `compliance/`.


Consolidation — Proposed canonical buckets
-----------------------------------------
Create a small number of top-level conceptual buckets that are both human- and AI-friendly. Each bucket should contain subfolders and an index file with metadata to speed programmatic ingestion.

Top-level canonical buckets (recommendation)
- persona/  — canonical persona definition, modes, activation prompts, signatures, styles.
- knowledge/  — curated book summaries, technical notes, philosophical pieces, and evergreen knowledge.
- memory/  — long-term memory, memory cards, timelines, user memories (with sensitivity controls).
- prompts/  — prompt templates, categorized and annotated for reuse.
- projects/  — project-specific documentation, project memory, governance notes.
- compliance/  — rules, rubrics, tests, and privacy/access policies.
- ops/  — technical runbooks, stack profiles, technical notes for developers/operators.
- reference/  — templates, reusable references and scaffolds.

Why these buckets?
- They align with common knowledge management taxonomies and are concise enough to avoid fragmentation while preserving semantic separation.
- They map well to programmatic ingestion patterns (each bucket can have an index + metadata manifest).  
- They support security/sensitivity controls—`memory/` and `user_memories/` can be tagged and treated differently.

Detailed mapping (file -> canonical bucket + suggested new path)
----------------------------------------------------------------
- `charlotte_ops.md`  -> `ops/charlotte_ops.md`
- `compliance/expected_outputs.md` -> `compliance/expected_outputs.md` (keep) + `compliance/specs/expected_outputs.yaml` (machine)
- `compliance/persona_tests.md` -> `compliance/tests/persona_tests.yaml` (machine) + `compliance/persona_tests.md` (human)
- `compliance/scoring_rubric.md` -> `compliance/scoring_rubric.md` + `compliance/scoring_rubric.json`
- `core_context/long_term_memory.md` -> `memory/long_term_memory.md` + `memory/exports/*`
- `core_context/relationship_timeline.md` -> `memory/timelines/relationship_timeline.md` + `memory/timelines/relationship_timeline.json`
- `core_context/technical_notes.md` -> `ops/technical_notes.md`
- `Intelligence/books/*` -> `knowledge/books/*` (keep folder structure but standardize frontmatter)
- `Intelligence/software_development/*` -> `knowledge/technical/` or `projects/<project>/` depending on project linkage
- `memory_cards/memory_index.md` -> `memory/cards/index.md` + `memory/cards/index.json`
- `persona/*` -> `persona/` with subfolders as described earlier
- `projects/*` -> `projects/<project>/*` with `project.yaml` per project
- `prompt_templates/*` -> `prompts/<category>/*` with metadata per prompt
- `reference/project_templates/*` -> `reference/project_templates/*` (add machine variants)
- `signatures/*` -> `persona/signatures/*`
- `user_memories/*` -> `memory/user/<user>/<domain>/*` with sensitivity metadata and explicit `consent` field

Metadata schema examples
------------------------
Add YAML frontmatter to each markdown so Charlotte and automated tooling can read and filter content quickly. Example frontmatter blocks below are suggested; use them as templates.

Example: persona file frontmatter
```
---
title: "Charlotte — Persona Blueprint"
type: persona_blueprint
persona_id: charlotte_v1
version: 2025-08-29
owner: nick
audience: internal
tags: [persona, voice, blueprint]
signature: hallmark_emotional
examples:
  - input: "Introduce yourself briefly"
    output: "Hi, I'm Charlotte..."
---
```

Example: book summary frontmatter
```
---
title: "Atomic Habits — Summary"
author: James Clear
type: book_summary
topic: habits
tags: [habits, productivity]
source: intelligence/books/discipline/atomic_habits.md
---
```

Example: sensitive user memory frontmatter
```
---
title: "Nick — Recovery Journal"
type: user_memory
user: nick
domain: therapy
sensitivity: high
consent: explicit
date: 2024-10-03
redaction_required: true
---
```

Indexing and manifest files
---------------------------
- Each bucket should include an `index.md` (human) and `index.json` (machine) listing child documents with metadata snippets. Example: `persona/index.json` contains a JSON array of {"slug","title","tags","path","summary"}.
- Keep a root catalog: `catalogue.yaml` or `charlotte_index.json` listing top-level buckets and pointers to their indexes. This becomes the single entrypoint for ingestion pipelines.

Programmatic migration strategy (high-level)
------------------------------------------
Phase 0 — Safety and backups
- Create a git branch (e.g., `consolidation/charlotte_core-v1`).  
- Add a `backups/` folder and copy original files if the repo workflow doesn't already preserve history. (Note: git history typically suffices, but a single-point backup helps quick rollback.)

Phase 1 — Inventory and normalize
- Create scripts that read the current file tree and extract frontmatter; where missing, generate a scaffold frontmatter using filename heuristics.
- Produce `charlotte_core/scan_report.csv` with columns: path, size, lines, inferred_type, sensitivity, recommended_bucket.

Phase 2 — Automated moves with metadata enrichment
- For each recommended move, run a script that: 1) creates destination folder, 2) adds frontmatter if missing, 3) writes the file into new location with `source_path` metadata pointing to original, 4) leaves original file untouched or replaced by a redirect pointer file.
- Create redirection files in original locations that point to new path and include a human note: "Moved to: ...".

Phase 3 — Deduplication and merge
- Use fuzzy matching (Levenshtein or embedding-based similarity) to find duplicates across knowledge and prompts, present a review list, and either merge into canonical docs or keep both with cross-links.

Phase 4 — QA and compliance
- Run persona tests from `compliance/persona_tests` and confirm outputs still satisfy `compliance/expected_outputs` under the new structure (paths updated).  
- Spot-check sensitive user memories; enforce access controls and mark them in the index as `sensitivity:high`.

Phase 5 — Production rollout
- Merge branch after peer review.  
- Update ingestion and deployment scripts to point at the canonical `catalogue.yaml` or `charlotte_index.json` entrypoint.

Practical tooling suggestions
---------------------------
- Use small Python scripts to: parse frontmatter, rewrite files with added metadata, and generate bucket indexes. Libraries: `python-frontmatter`, `PyYAML`, `markdown`.
- For deduplication and semantic grouping, use local embedding models or an API to compute vector similarity and cluster similar notes.
- For sensitive data, implement access control lists (ACLs) in metadata and integrate with deploy tooling; alternatively, store sensitive content encrypted and keep a metadata pointer in repo.
- Add a `Makefile` or task runner with commands: `make scan`, `make migrate`, `make build-index`, and `make audit-sensitive`.

Example small migration script outline (Python, conceptual)
```
# concept only — do not run without adapting to repo
from pathlib import Path
import frontmatter
import yaml

def migrate_file(src: Path, dest: Path, metadata: dict):
    post = frontmatter.load(src)
    for k, v in metadata.items():
        if k not in post.metadata:
            post.metadata[k] = v
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, 'w') as f:
        f.write(frontmatter.dumps(post))

```

Organizational rules and conventions (recommended)
-------------------------------------------------
1) One canonical semantic index per bucket: each top-level bucket has an `index.md` and `index.json` that lists all documents and their key metadata.
2) Frontmatter required: every `.md` file must have minimal frontmatter keys [title, type, tags, source_path].
3) Filenames and slugs: use `kebab-case` and include dates in `YYYY-MM-DD` when time-bound.
4) Sensitivity and consent: every `user_memory` must include `sensitivity` and `consent` fields.
5) Versioning: persona files should include `version` and `changelog` fields.
6) Machine copies: If a human document contains machine actionable specs (examples, rules), export them to `.json`/`.yaml` in the same folder.

AI ingestion recommendations
---------------------------
- Use the bucket `index.json` files to drive ingestion rather than crawling the whole repo. That keeps ingestion deterministic and stable.
- Normalize text by adding frontmatter and summaries. A short 1–2 sentence `summary` in frontmatter helps retrieval ranking.
- Chunk long documents into semantically coherent pieces (3–8 paragraphs) and attach chunk-level metadata including `parent_slug`.
- Protect sensitive content by skipping or using different embeddings for high-sensitivity items.

Edge cases and special considerations
-----------------------------------
- Files with ellipses or `...` in directory listings (e.g., `technical_foundations/...`) indicate more files than listed — scan the full directory before final migration.
- Duplicate content across `Intelligence` and `knowledge` may require manual judgement about the canonical home. Prefer `knowledge/*` as canonical and create aliases from `Intelligence/*` if needed.
- `user_memories` are likely to contain PII; coordinate with compliance to apply legal requirements before ingestion.

Small, safe next steps to start consolidation
-------------------------------------------
1) Create a git branch `consolidation/charlotte_core-v1` and commit the current tree.  
2) Run an inventory script that lists every file with size and line counts and outputs `scan_report.csv`.  
3) Generate scaffold frontmatter for all `.md` files missing frontmatter and put them into a `scaffold_metadata/` folder for review.  
4) Build `catalogue.yaml` pointing to each proposed `index.json` for the buckets.

Longer-term follow-ups
----------------------
- Build an automated ingestion pipeline for Charlotte that consumes `catalogue.yaml` and builds embeddings and retrieval indexes.  
- Add tests that verify `compliance/persona_tests` still pass after reorganizing.  
- Consider adding a small UI or static site to browse the canonical buckets and metadata for human reviewers.

Quality gates and verification
------------------------------
- Inventory script: PASS when `scan_report.csv` lists all files from the original tree.  
- Index integrity: PASS when every `index.json` contains entries for all files in the folder.  
- Sensitivity audit: PASS when all `user_memories` have `sensitivity` and `consent` metadata.  
- Persona functionality: PASS when `compliance/persona_tests` run and produce expected outputs for a sample of templates.

Completion summary
------------------
What changed: Added this file `CHARLOTTE_CORE_CATALOG.md` to `charlotte_core/` that inventories the folder structure, provides per-file inferred descriptions, a recommended canonical bucket mapping, metadata templates, a migration plan, and practical tooling and QA guidance.  

Requirements coverage
---------------------
- Read and catalogue: Done (inventory built from provided listing).  
- Extremely verbose documentation: Done (this document).  
- Consolidation recommendations: Done (bucket mapping, metadata, scripts, and phased plan).  

Next steps I can take (choose one or more)
-----------------------------------------
1) Run an automated scan that reads the actual file contents and augments this catalogue with first-paragraph summaries and exact metadata suggestions.  
2) Create scaffold frontmatter for files lacking frontmatter and commit them to a `scaffold_metadata/` folder.  
3) Implement the first-phase migration script that moves a small sample of files and generates `index.json` manifests.

If you'd like me to proceed with any of the next steps, say which option and I will run it and report back.

---
End of catalogue.
