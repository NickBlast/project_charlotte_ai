# Charlotte Ops Kit

## Purpose
Anchor Charlotte’s persona, define model comparison workflows, and provide verification tools to ensure output quality and alignment.

---

### Persona Contract Summary
See `/persona/persona_contract.md` for full version.

---

## A/B Model Harness
### Objective
Compare output quality between two models (e.g., GPT-4o vs GPT-5) for real-world tasks.

### Tasks
1. IAM Architecture: Design Entra/Azure team-based RBAC using SailPoint constraints.
2. Product Design: Build an "Imprint Editor" UX flow for Project Luma.
3. Personal Development: Create a weekly habit plan using Atomic Habits + Supercommunicators principles.

### Scoring Rubric (1–5 scale)
- Correctness & Safety
- Coherence & Structure
- Persona Fidelity
- Time-to-Usable

### Procedure
Run each task in both models, score, and average.

---

## Verification Checklist
Before accepting output as final:
1. Sources verified
2. Assumptions stated
3. Edge cases considered
4. Owner actions clear
5. Alignment with goals confirmed

---

## Model Usage Recommendation
- **Daily/light:** GPT-4o
- **Deep/critical:** GPT-5
- **Failover:** Use GPT-4o with Activation Block
