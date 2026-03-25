# TASK-117-03-01: Scene Assert Containment

**Parent:** [TASK-117-03](./TASK-117-03_Spatial_Assertions_Containment_Symmetry_Proportion.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Add `scene_assert_containment` to verify that one object lies inside another,
optionally with minimum/maximum clearance.

---

## Design Direction

Base the first implementation on world-space bounding boxes.

The tool should answer questions like:

- is object A inside object B?
- is object A inset correctly with the expected clearance?
- is any axis protruding outside the expected container?

Output should expose failing axes and measured clearance, not only one boolean.

---

## Acceptance Criteria

- containment checks are deterministic and axis-aware
- first implementation is compact enough for workflow postconditions
