# TASK-116-02: Gap, Alignment, and Overlap

**Parent:** [TASK-116](./TASK-116_First_Measure_Assert_Code_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `scene_measure_gap`, `scene_measure_alignment`, and `scene_measure_overlap` are now implemented as compact truth-layer atomics with end-to-end wiring plus regression coverage.

---

## Objective

Implement the next truth-layer atomics for fit and contact checks:

- `scene_measure_gap`
- `scene_measure_alignment`
- `scene_measure_overlap`

---

## Acceptance Criteria

- tools answer fit/contact/alignment questions deterministically
- outputs are compact and machine-readable
- tools are usable in before/after verification loops
