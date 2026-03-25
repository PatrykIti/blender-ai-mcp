# TASK-117-02-02: Scene Assert Dimensions

**Parent:** [TASK-117-02](./TASK-117-02_First_Assertion_Tools_Contact_And_Dimensions.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Add `scene_assert_dimensions` so workflows can verify width/height/depth against
expected values without LLM-side math.

---

## Contract Direction

Support assertions against:

- exact expected dimensions with tolerance
- per-axis checks
- optional range-based checks when exact values are not appropriate

Expected output should include:

- `object_name`
- `passed`
- `expected`
- `actual`
- `delta`
- `tolerance`
- `axes_checked`

Implementation should reuse `scene_measure_dimensions`.

---

## Acceptance Criteria

- the tool can answer “is this object the right size?” deterministically
- output is compact enough for before/after workflow checks
