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

## Replacement Decision

- `sculpt_deform_region` is the public automated replacement for `sculpt_brush_grab`
- `sculpt_brush_grab` should not remain a first-class LLM-facing sculpt write tool after this lands
- if needed, keep a narrow internal/manual helper only until callers are migrated, then remove it from the recommended surface

---

## Acceptance Criteria

- `sculpt_deform_region` works end-to-end through addon, handler, adapter, and docs
- it can cover the main “grab/pull local area” workflow without UI brush strokes
- the old grab brush is no longer part of the recommended public sculpt write path
