# Brain dump — ChatGPT-only Backup & Restore (current scope; future portability)

**Problem & intent**

* Users can lose context/persona when providers change features or models; consumer plans lack enterprise-grade portability.
* Goal: a **local-first, deterministic** way to **backup, organize, and rehydrate** a ChatGPT persona + chats + assets—fast.
* Treat ChatGPT Memory as **cache**; the **backup repo** is canonical. Rehydration = ordered “restore packs.”
* Long-term: cross-model portability (Claude/Gemini/local) so users aren’t trapped; start **ChatGPT-only**.

**Primary user outcomes**

* “I can always pull a complete copy of my ChatGPT world, offline.”
* “I can rebuild my persona and working state in a new session in minutes.”
* “I can browse/search my history locally and generate new restore packs on demand.”
* “I don’t need to be technical to do it.”

**Data we care about (ChatGPT export, today)**

* Conversations (titles, message trees, timestamps, model hints).
* User/account metadata.
* Feedback and shared links (when present).
* Assets: images/audio/attachments referenced in conversations.
* Emerging: Memories (UI-managed; we’ll capture equivalents as **Memory Cards** from content, not via Memory API).

**MVP surfaces (ChatGPT-only)**

* **Export → Ingest → Restore** three-step flow (wizard + CLI parity).
* **Watch Folder** (e.g., Downloads) OR **drag-and-drop** ZIP.
* **Intake**: copy, canonical rename (`chatgpt_export_YYYY-MM-DD_HH-MM-SS_sha12.zip`), manifest (hashes, counts, source path).
* **Normalize**: transcripts to Markdown; assets to `/assets` with `images_manifest.json`; meta to JSON.
* **Organizer**: mine for **persona/modes/protocols/projects/relationship context** → propose **Memory Cards** (YAML/MD) with routing confidence; spill low-confidence to `unclassified.md`.
* **Restore Builder**: emit chunked, paste-ready packs (Persona → Protocols → Modes → Projects → Special); include **Integrity Check** prompts; options for `minimal` vs `full`.
* **Explorer UI**: filter by conversation/persona/project; quick search; “Build restore from selection.”

**Reliability & trust (user-facing)**

* Determinism: UTC timestamps, stable ordering, SHA-256 manifests; repeats with same inputs produce identical outputs.
* Safety rails: Zip-Slip defense, zip-bomb heuristics, size caps, asset count parity checks.
* Privacy: local-first by default; **we never modify** the user’s original ZIP—only copy; redaction only in reports/candidates.
* Compliance posture: **no UI scraping** or automated extraction from ChatGPT; the export is **user-initiated**.

**Naming & detection (intake)**

* Never depend on the vendor filename; treat it as opaque.
* Accept if: valid ZIP (stable size), contains `user.json` & `conversations.json`, basic schema sanity (list of convos; mapping nodes with messages).
* Canonical rename after SHA-256; keep a manifest mapping original→canonical.

**Onboarding & guidance**

* First-run coach marks: “Request export,” “Drop ZIP here,” “Review proposed memories,” “Build restore.”
* Checklists per step with expected outputs and simple pass/fail receipts.
* Troubleshooting: “Link expired,” “Partial download,” “Unknown export,” “Asset mismatch.”

**What we will **not** do (for MVP)**

* No account automation, credential storage, scraping, or background data pulls from ChatGPT.
* No cloud sync by default; no multi-LLM importers yet.

**Future directions (not in MVP, but on deck)**

* **Adapters** for Claude/Gemini/etc. (official exports/Takeout first).
* **Encrypted cloud vault** (zero-knowledge, client-held keys) + scheduled export reminders.
* **Knowledge-pack builder**: distill books/notes into Memory Cards + restore addenda.
* **Persona Portability Profile** (JSON) that third-party tools can consume.
* **Team mode**: multiple personas, audit trails, redaction templates.

**Why this wedge is winnable**

* Most tools miss **rehydration UX** and **deterministic integrity**.
* Solo/creator market underserved versus enterprise.
* Our stance—**local-first, deterministic, persona-centric**—is opinionated and trustworthy.
