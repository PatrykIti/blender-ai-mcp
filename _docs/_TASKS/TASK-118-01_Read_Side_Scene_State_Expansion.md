# TASK-118-01: Read-Side Scene State Expansion

**Parent:** [TASK-118](./TASK-118_Scene_Render_World_And_Configuration_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Extend grouped read-side scene inspection so the repo can inspect appearance and
render state, not only geometry/object data.

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-118-01-01](./TASK-118-01-01_Scene_Inspect_Render_And_Color_Management.md) | Inspect render and color-management state |
| [TASK-118-01-02](./TASK-118-01-02_Scene_Inspect_World.md) | Inspect world/background state |

---

## Acceptance Criteria

- `scene_inspect` gains deterministic scene-level read actions
- output is compact and reconstruction-friendly
