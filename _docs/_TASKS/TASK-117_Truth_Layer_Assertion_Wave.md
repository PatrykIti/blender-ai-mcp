# TASK-117: Truth Layer Assertion Wave

**Priority:** 🔴 High  
**Category:** Truth Layer / Scene Verification  
**Estimated Effort:** Medium  
**Dependencies:** TASK-113, TASK-114, TASK-116  
**Status:** 🚧 In Progress

**Progress Update:** The first implementation slice is already in place: shared assertion result contracts plus `scene_assert_contact` and `scene_assert_dimensions` now exist end-to-end. The remaining work is the higher-order spatial assertion family and the final full-family delivery pass.

---

## Objective

Add the second truth-layer wave so LLM workflows can ask deterministic
pass/fail questions, not only raw measurements.

---

## Business Problem

`TASK-116` solved the first half of the truth problem: the repo now knows how to
measure distance, dimensions, gap, alignment, and overlap.

What it still cannot do cleanly is answer:

- do these parts actually touch?
- are these dimensions within tolerance?
- is this object contained correctly?
- is this proportion acceptable?
- is this shape symmetric enough?

Without explicit assertion tools, the outer LLM still has to interpret raw
numbers ad hoc.

---

## Business Outcome

If this wave is done correctly, the repo gains:

- deterministic `scene_assert_*` tools for high-frequency build validation
- compact pass/fail outputs with expected vs actual values
- clearer router/workflow postconditions for fit, containment, and proportion
- a cleaner handoff from measurement to verification

---

## Scope

This umbrella covers:

- shared assertion result contracts and tolerance semantics
- `scene_assert_contact`
- `scene_assert_dimensions`
- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`
- metadata, docs, and regression coverage for the new assertion family

---

## Success Criteria

- the repo has a first deterministic `scene_assert_*` family on top of `TASK-116`
- assertion tools return compact machine-readable pass/fail payloads
- tolerances and comparison semantics are explicit and stable
- docs position assertions as the next truth-layer step after measurement

---

## Execution Structure

| Order | Subtask | Purpose |
|------|---------|---------|
| 1 | [TASK-117-01](./TASK-117-01_Assertion_Contracts_And_Shared_Semantics.md) | Define common assertion envelopes and comparator/tolerance semantics |
| 2 | [TASK-117-02](./TASK-117-02_First_Assertion_Tools_Contact_And_Dimensions.md) | Implement the first two smallest assertion tools |
| 3 | [TASK-117-03](./TASK-117-03_Spatial_Assertions_Containment_Symmetry_Proportion.md) | Implement higher-order spatial assertions |
| 4 | [TASK-117-04](./TASK-117-04_Metadata_Docs_And_Regression_Coverage.md) | Deliver metadata, docs, and regression coverage |
