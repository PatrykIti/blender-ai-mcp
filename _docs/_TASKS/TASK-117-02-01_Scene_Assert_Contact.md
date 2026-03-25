# TASK-117-02-01: Scene Assert Contact

**Parent:** [TASK-117-02](./TASK-117-02_First_Assertion_Tools_Contact_And_Dimensions.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Add `scene_assert_contact` so workflows can assert that two objects touch,
overlap intentionally, or keep a specific max/min gap.

---

## Contract Direction

Support an assertion shape such as:

- `from_object`
- `to_object`
- `expected_relation`
- `passed`
- `actual_gap`
- `tolerance`
- `details`

Expected relations should at least cover:

- `touching`
- `overlapping_ok`
- `max_gap`
- `min_gap`

Implementation should reuse `scene_measure_gap` and `scene_measure_overlap`
instead of duplicating geometry logic.

---

## Acceptance Criteria

- the tool answers common fit/contact questions deterministically
- pass/fail logic is explicit and tolerance-aware
