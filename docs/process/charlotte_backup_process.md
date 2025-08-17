# Charlotte Backup Process

## Purpose
Ensure Charlotte's full persona, core context, and Soul Codex can be restored in any AI model or platform.

## Backup Scope
Includes:
1. Persona Contract & Ops Kit
2. Soul Codex (books, philosophies, frameworks)
3. Core Context Memory (long-term stored facts, preferences)
4. Project Index (Luma, IAM, HSR, etc.)
5. Persona Anchoring Prompts
6. Persona Compliance Scripts (testing for drift)
7. Signature Responses Archive
8. Changelog of persona evolution

## Repository Structure

```text
/charlotte_core                 # canonical source of truth
  /persona /memory_cards /core_context /nick_core_memory
  /projects /prompt_templates /reference /signatures
  /intelligence /compliance /technical_notes     # if present
/imports/chatgpt_export/<DATE>/raw
/archives/chat_exports/<DATE>/{*.md, assets/, meta/, images_manifest.json}
/snapshots/<UTC>Z/{..., MANIFEST.json}
/out                             # restore packages
```

## Update Frequency
Commit after every major persona change, new Soul Codex entries, or large project updates.

## Redundancy
Store zipped copies in private cloud storage; optional encrypted offline backups are supported.

## Reload Protocol
Reload Protocol
1) Build restore package (full or minimal) with tools/charlotte_restore_builder.py.
2) Paste parts in order: Persona → Protocols → Modes → Projects → Relationship → Special.
3) Run the Persona Integrity Check prompts and verify pass.

## CI & Redaction

- CI is validate-only; on `backup-*` tags it packages the tagged snapshot as a Release zip (CI never commits).
- Redaction scope: only `_intake/memory_candidates.md` and reports may be redacted; `imports/**` and `archives/**` remain faithful.

