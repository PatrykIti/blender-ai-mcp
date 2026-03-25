# TASK-118-01-01: Scene Inspect Render and Color Management

**Parent:** [TASK-118-01](./TASK-118-01_Read_Side_Scene_State_Expansion.md)  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

---

## Objective

Add grouped read-side inspection for render and color-management settings.

---

## Design Direction

Extend `scene_inspect` with actions such as:

- `render`
- `color_management`

Expected read payload should cover at least:

- render engine and device
- samples and resolution
- output format/path basics
- exposure / gamma / view transform / look

Keep the output deterministic and reconstruction-friendly rather than verbose.

---

## Acceptance Criteria

- render/color-management state can be exported through grouped scene inspection
- payloads are stable enough for later write-side replay
