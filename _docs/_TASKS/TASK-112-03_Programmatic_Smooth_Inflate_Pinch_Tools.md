# TASK-112-03: Programmatic Smooth, Inflate, and Pinch Tools

**Priority:** 🟡 Medium  
**Category:** Sculpt Write Path  
**Estimated Effort:** Medium  
**Dependencies:** TASK-112-01  
**Status:** ✅ Done

**Completion Summary:** Added `sculpt_smooth_region`, `sculpt_inflate_region`, and `sculpt_pinch_region` across domain, handler, addon, MCP adapter, dispatcher, metadata, docs, and tests. These tools now cover the core local smoothing and local expand/contract workflows without relying on brush-stroke UI paths.

---

## Objective

Add deterministic local smoothing and local shape-adjustment sculpt tools on top of the shared region engine.

---

## Scope

- `sculpt_smooth_region`
- `sculpt_inflate_region`
- `sculpt_pinch_region`

Expected behavior:

- `sculpt_smooth_region`
  - local smoothing with `iterations`, `strength`, `radius`, `falloff`
- `sculpt_inflate_region`
  - move vertices along normals outward/inward in a local region
- `sculpt_pinch_region`
  - pull vertices toward the center of influence in a local region

---

## Acceptance Criteria

- each tool is deterministic and geometry-driven
- each tool has clear structured parameters and a concise result summary
- each tool is usable by LLMs without viewport/event dependence
