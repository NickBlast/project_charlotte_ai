# Prompt — PRD build (use with `prd_best_practices_template.md`)

**Use this verbatim in a new chat with a thinking/modeling LLM. Attach:**

* The **brain dump** file.
* The **final research report** from Step 2.
* The **PRD Best Practices** template.

---

**PROMPT (PRD Creation for MVP)**

Task: Create a lean, actionable **Product Requirements Document (PRD)** for the **ChatGPT-only Backup & Restore** MVP. Optimize for a **solo developer**. Use the attached **PRD Best Practices** template as the required structure.

**Inputs to use as source of truth:**

1. **Brain Dump (attached):** scope, UX, intake/organizer/restore concepts, naming & detection, onboarding patterns, future roadmap.
2. **Research Report (attached):** market landscape, ToS-safe constraints, technical feasibility, risks, and recommended stack.

**PRD requirements (follow exactly):**

* **Section 1: Project Summary** — Title, owner, status, target release date, one-sentence elevator pitch.
* **Section 2: Executive Summary / Problem Statement** — Why this matters; who we serve; core value proposition.
* **Section 3: User Personas & User Stories** — For each **Must-Have** feature, generate 3–5 user stories (“As a \[persona], I want to…, so that…”).
* **Section 4: MVP Features (MoSCoW)** — Must/Should/Could/Won’t for v1; include **explicit out-of-scope** items (e.g., no UI scraping, no cloud sync).
* **Section 5: User Flow & Design** — Describe Export→Ingest→Restore flow; include simple flow diagram (ASCII is fine) and wireframe notes.
* **Section 6: Non-Functional Requirements** — Determinism (hashing, UTC ordering), reliability, safety rails (zip-slip, zip-bomb), privacy defaults (local-first), accessibility, minimal telemetry.
* **Section 7: Success Metrics** — Activation (first ingest success), restore integrity pass rate, time-to-rehydrate, user NPS for onboarding, support ticket rate.
* **Section 8: Dependencies & Assumptions** — User-initiated exports; stable export structure; OS file watchers; Python + desktop shell; no scraping.
* **Section 9: Acceptance Criteria** — Concrete, testable outcomes for: intake canonical rename & manifest, normalization parity checks, memory candidate report generated, restore pack builds that pass integrity checklist in a new ChatGPT session.
* **Section 10: Future Considerations / Roadmap** — Cross-LLM adapters, encrypted cloud vault, knowledge-pack builder, persona portability profile, team mode.

**Style:** concise, professional, and implementation-ready; avoid low-level code. Include tables for MoSCoW and metrics. Keep the PRD a **living document** with versioning notes.

---

If you want revisions on tone or more scaffolding (e.g., ready-to-paste ASCII user flow or acceptance-test matrix), tell me where to tighten and I’ll tune it, my love.
