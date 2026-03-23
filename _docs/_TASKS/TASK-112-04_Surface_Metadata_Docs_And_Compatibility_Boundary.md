# TASK-112-04: Surface Metadata, Docs, and Compatibility Boundary

**Priority:** 🟡 Medium  
**Category:** MCP UX  
**Estimated Effort:** Small  
**Dependencies:** TASK-112-02, TASK-112-03  
**Status:** ⏳ To Do

---

## Objective

Make the new sculpt path visible and make the old brush path clearly non-primary for LLM clients.

---

## Scope

- update public tool docs and summaries
- update router metadata under `server/router/infrastructure/tools_metadata/sculpt/`
- update prompt docs if they reference sculpt flows
- explicitly mark old `sculpt_brush_*` tools as:
  - manual/setup-only where applicable
  - compatibility tools, not preferred automated path
- ensure new programmatic sculpt tools are the recommended LLM-facing tools

---

## Acceptance Criteria

- docs do not imply that brush setup tools are the best automation path
- metadata examples prefer programmatic sculpt tools
- compatibility story is explicit instead of implicit
