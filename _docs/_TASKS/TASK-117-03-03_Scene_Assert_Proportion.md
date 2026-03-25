# TASK-117-03-03: Scene Assert Proportion

**Parent:** [TASK-117-03](./TASK-117-03_Spatial_Assertions_Containment_Symmetry_Proportion.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Add `scene_assert_proportion` so workflows can validate explicit ratios instead
of only absolute dimensions.

---

## Design Direction

Support at least:

- one-object internal ratios such as width:height
- two-object proportions such as leg thickness vs tabletop thickness
- ratio ranges with tolerance

Expected outputs should expose:

- `passed`
- `expected_ratio`
- `actual_ratio`
- `delta`
- `tolerance`

Implementation should reuse `scene_measure_dimensions` and any shared ratio
helpers instead of duplicating math inside MCP wrappers.

---

## Acceptance Criteria

- workflows can validate proportions without outer-LLM arithmetic
- ratio semantics stay stable across scene/object checks
