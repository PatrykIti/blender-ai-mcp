# TASK-112-06: Programmatic Crease Region and Final Public Surface Cleanup

**Priority:** 🟡 Medium  
**Category:** Sculpt Write Path / MCP Surface  
**Estimated Effort:** Small  
**Dependencies:** TASK-112-03  
**Status:** ✅ Done

**Completion Summary:** Added `sculpt_crease_region` and removed the remaining brush-dependent sculpt setup tools from the public MCP sculpt surface. Their user-intent semantics are now absorbed by the deterministic region-tool family and updated router metadata.

---

## Objective

Finish the public sculpt-surface replacement wave by removing the last brush-driven write tools that were still visible in MCP.

---

## Scope

- add `sculpt_crease_region`
- remove public exposure of:
  - `sculpt_brush_crease`
  - `sculpt_brush_clay`
  - `sculpt_brush_blob`
  - `sculpt_brush_snake_hook`
  - `sculpt_brush_draw`
- update router metadata and local config examples so the new region tools are the only public write-side sculpt path

---

## Acceptance Criteria

- `sculpt_crease_region` works end-to-end
- the public sculpt surface no longer exposes the remaining brush-dependent write tools
- metadata/docs/config examples point to the deterministic region-tool family
