# TASK-112-05: Tests for Programmatic Sculpt Tools

**Priority:** 🟡 Medium  
**Category:** Testing  
**Estimated Effort:** Medium  
**Dependencies:** TASK-112-02, TASK-112-03  
**Status:** ✅ Done

**Completion Summary:** Added focused unit coverage for the region engine and the new sculpt handlers, plus Blender-backed e2e smoke coverage for `sculpt_deform_region`, `sculpt_inflate_region`, and `sculpt_pinch_region`.

---

## Objective

Add deterministic unit and e2e coverage for the new sculpt region tool family.

---

## Scope

- unit tests:
  - region selection
  - falloff weighting
  - symmetry behavior
  - payload/result contracts
- e2e tests:
  - local deformation actually changes geometry
  - smoothing reduces local irregularity
  - inflate/pinch change shape in the expected direction
- contract/docs alignment tests where useful

---

## Acceptance Criteria

- new sculpt tools are covered by fast unit tests
- at least the first-wave programmatic deform tool has Blender-backed e2e coverage
- regressions in geometry effect vs “setup only” semantics are detectable in CI
