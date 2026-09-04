# TASK-118-02-02: Scene Configure World

**Parent:** [TASK-118-02](./TASK-118-02_Grouped_Scene_Configure_Tool.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_configure(action="world")` now supports bounded world assignment, `use_nodes` toggles, simple world color updates, and simple background color/strength replay without claiming full world node-graph authorship.

---

## Objective

Add write-side grouped configuration for world/background state.

---

## Design Direction

Support deterministic world-level updates such as:

- world assignment by name
- simple background color/strength updates
- `use_nodes` toggles where appropriate

Do not silently absorb full node-graph authoring into this task; that belongs to
the explicit node-graph track.

---

## Acceptance Criteria

- common world/background changes can be applied deterministically
- node-graph-heavy cases stay behind an explicit handoff boundary
