# TASK-118-01-01: Scene Inspect Render and Color Management

**Parent:** [TASK-118-01](./TASK-118-01_Read_Side_Scene_State_Expansion.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_inspect(action="render")` and `scene_inspect(action="color_management")` are now implemented with structured read-side payloads for render and color-management settings.

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
