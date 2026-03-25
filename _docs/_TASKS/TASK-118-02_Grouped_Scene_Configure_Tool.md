# TASK-118-02: Grouped Scene Configure Tool

**Parent:** [TASK-118](./TASK-118_Scene_Render_World_And_Configuration_Wave.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Add the grouped write-side scene configuration surface instead of reviving a
flat spread of scene-specific write tools.

---

## Expected Public Shape

Introduce a grouped tool such as:

- `scene_configure(action="render", settings=...)`
- `scene_configure(action="color_management", settings=...)`
- `scene_configure(action="world", settings=...)`

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-118-02-01](./TASK-118-02-01_Scene_Configure_Render_And_Color_Management.md) | Write-side render and color-management configuration |
| [TASK-118-02-02](./TASK-118-02-02_Scene_Configure_World.md) | Write-side world/background configuration |

---

## Acceptance Criteria

- the write-side surface stays grouped and bounded
- scene-level settings can be applied deterministically from structured inputs
