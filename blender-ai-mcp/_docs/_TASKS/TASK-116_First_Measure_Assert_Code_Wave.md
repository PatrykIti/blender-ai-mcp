# TASK-116: First Measure/Assert Code Wave

**Priority:** 🔴 High  
**Category:** Truth Layer / Scene Verification  
**Estimated Effort:** Medium  
**Dependencies:** TASK-113, TASK-114  
**Status:** ✅ Done

**Completion Summary:** The first deterministic truth-layer scene family is now implemented end-to-end: `scene_measure_distance`, `scene_measure_dimensions`, `scene_measure_gap`, `scene_measure_alignment`, and `scene_measure_overlap` all exist across addon, server, MCP, metadata, docs, and regression coverage.

---

## Objective

Implement the first deterministic measure/assert atomic family so LLM workflows can verify proportions, spacing, and alignment without relying on visual intuition alone.

---

## Why This Wave Is First

`TASK-114` showed that the repo already has useful inspection and before/after tools, but still lacks the compact truth-layer atomics that should answer:

- how far apart are these things?
- what are the actual dimensions?
- is there a gap or contact?
- are these parts aligned?
- do these objects overlap?

These questions are the highest-frequency failure cases in current LLM modeling.

---

## Scope

This first code wave covers:

- `scene_measure_distance`
- `scene_measure_dimensions`
- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`

Implementation may be split into smaller delivery waves, but these five belong
to the same first-family rollout.

---

## Success Criteria

- the repo has a first deterministic truth-layer family for scene/object measurement
- the new tools return compact machine-readable outputs
- the first-wave tools are documented as the preferred truth source for fit/proportion checks

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-116-01](./TASK-116-01_Distance_And_Dimensions.md) | First two smallest atomics: distance + dimensions |
| 2 | [TASK-116-02](./TASK-116-02_Gap_Alignment_And_Overlap.md) | Gap/contact, alignment, and overlap/intersection |
| 3 | [TASK-116-03](./TASK-116-03_Contracts_Docs_And_Metadata.md) | Contracts, router metadata, and public docs for the first-family rollout |
| 4 | [TASK-116-04](./TASK-116-04_Tests_And_Regression_Coverage.md) | Unit/E2E coverage for the new truth-layer atomics |
