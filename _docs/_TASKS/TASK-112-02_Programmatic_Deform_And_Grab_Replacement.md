# TASK-112-02: Programmatic Deform and Grab Replacement

**Priority:** 🟡 Medium  
**Category:** Sculpt Write Path  
**Estimated Effort:** Medium  
**Dependencies:** TASK-112-01  
**Status:** ⏳ To Do

---

## Objective

Add `sculpt_deform_region` as the deterministic replacement for `sculpt_brush_grab`.

---

## Scope

- add a new MCP/public tool:
  - `sculpt_deform_region`
- expected contract:
  - `object_name`
  - `center`
  - `radius`
  - `delta`
  - `strength`
  - `falloff`
  - `symmetry_axis` / symmetry flags as needed
- apply weighted displacement to vertices in the selected region
- return a deterministic summary:
  - affected vertex count
  - effective delta
  - applied falloff

---

## Compatibility Decision

- do **not** remove `sculpt_brush_grab` in this task
- `sculpt_brush_grab` stays as manual/setup-only
- `sculpt_deform_region` becomes the recommended automated path

---

## Acceptance Criteria

- `sculpt_deform_region` works end-to-end through addon, handler, adapter, and docs
- it can cover the main “grab/pull local area” workflow without UI brush strokes
- the old grab brush is no longer the recommended LLM path
