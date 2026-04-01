# TASK-119: Existing Public Surface Hardening After TASK-113

**Priority:** 🔴 High  
**Category:** Product Surface Hardening  
**Estimated Effort:** Large  
**Dependencies:** TASK-113, TASK-114, TASK-115, TASK-116, TASK-117, TASK-118  
**Status:** ✅ Done

**Completion Summary:** The existing public/model-facing surface is now hardened: aliases, grouped build-tool contracts, metadata/discovery wording, guided escape-hatch visibility, public docs/prompts, and regression/benchmark baselines have all been aligned with the post-`TASK-113` product model.

---

## Objective

Bring the existing public/model-facing tool surface into full alignment with the
post-`TASK-113` product model before adding a broader macro layer.

---

## Business Problem

The repo now has the right strategic model, but not every high-value public tool
fully expresses it yet:

- some grouped/public tools still carry pre-`TASK-113` semantics or wording
- some result envelopes and output schemas are inconsistent across the public layer
- some metadata/discovery examples still bias toward low-level manual flows
- some guided-surface escape hatches are still looser than the intended product model

If those gaps remain, a new macro layer will be built on top of a still-misaligned
public foundation.

---

## Business Outcome

If this wave is done correctly, the repo gains:

- one hardened public surface for grouped/high-value tools
- tighter consistency between code, metadata, docs, prompts, and guided visibility
- less ambiguity about when models should use grouped tools vs escape hatches
- a cleaner substrate for the later macro-tool wave

---

## Scope

This umbrella covers:

- grouped/public tool semantics and return-shape hardening
- metadata/discovery/visibility drift cleanup
- final docs/prompt closure for the hardened public surface
- regression and benchmark protection for the post-hardening state

This umbrella does **not** introduce new macro tools yet.
It prepares the existing public layer for that next wave.

---

## Success Criteria

- high-value grouped/public tools speak one coherent product language
- public result contracts are consistent enough for later macro composition
- guided visibility/discovery behavior matches the documented product model
- prompts/docs stop teaching older manual-first patterns on production surfaces

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-119-01](./TASK-119-01_Public_Tool_Semantics_And_Contract_Hardening.md) | Harden grouped/public tool semantics, result envelopes, and public argument behavior |
| 2 | [TASK-119-02](./TASK-119-02_Metadata_Discovery_And_Visibility_Drift_Cleanup.md) | Clean up router metadata, discovery wording, and guided escape-hatch boundaries |
| 3 | [TASK-119-03](./TASK-119-03_Docs_Prompts_And_Regression_Hardening.md) | Finish docs/prompt closure and protect the hardened public surface with regression coverage |
