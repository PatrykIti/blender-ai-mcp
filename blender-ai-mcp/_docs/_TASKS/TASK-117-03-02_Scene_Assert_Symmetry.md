# TASK-117-03-02: Scene Assert Symmetry

**Parent:** [TASK-117-03](./TASK-117-03_Spatial_Assertions_Containment_Symmetry_Proportion.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_assert_symmetry` is now implemented as a deterministic pair-based symmetry check against a chosen mirror axis and coordinate.

---

## Objective

Add `scene_assert_symmetry` so workflows can check whether mirrored parts or
whole-object bounds remain symmetric enough across a chosen axis.

---

## Design Direction

First-wave symmetry may start from bounding boxes and object transforms before
later mesh-level symmetry tools exist.

Expected inputs should cover:

- symmetry axis
- optional left/right object pair
- tolerance

Expected outputs should expose:

- `passed`
- `axis`
- `expected`
- `actual`
- `delta`

---

## Acceptance Criteria

- common “are these mirrored parts still symmetric?” checks are deterministic
- symmetry semantics are explicit, not vision-only judgment calls
