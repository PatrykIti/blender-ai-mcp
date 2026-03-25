# TASK-117-03: Spatial Assertions, Containment, Symmetry, Proportion

**Parent:** [TASK-117](./TASK-117_Truth_Layer_Assertion_Wave.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `scene_assert_containment`, `scene_assert_symmetry`, and `scene_assert_proportion` are now implemented end-to-end on top of the measure layer with shared assertion contracts and regression coverage.

---

## Objective

Implement the higher-order assertion tools that still recur frequently in LLM
modeling failures:

- `scene_assert_containment`
- `scene_assert_symmetry`
- `scene_assert_proportion`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-117-03-01](./TASK-117-03-01_Scene_Assert_Containment.md) | Assert that one object sits inside another with optional clearance |
| [TASK-117-03-02](./TASK-117-03-02_Scene_Assert_Symmetry.md) | Assert bilateral or axis-based symmetry with explicit tolerance |
| [TASK-117-03-03](./TASK-117-03-03_Scene_Assert_Proportion.md) | Assert ratios/proportion relationships between dimensions or objects |

---

## Acceptance Criteria

- these assertions can be used directly in workflow postconditions
- each tool states expected vs actual relation explicitly
