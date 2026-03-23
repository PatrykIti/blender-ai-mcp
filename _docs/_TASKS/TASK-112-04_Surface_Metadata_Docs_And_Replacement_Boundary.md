# TASK-112-04: Surface Metadata, Docs, and Replacement Boundary

**Priority:** 🟡 Medium  
**Category:** MCP UX  
**Estimated Effort:** Small  
**Dependencies:** TASK-112-02, TASK-112-03  
**Status:** ⏳ To Do

---

## Objective

Make the new sculpt path visible and explicitly replace the old brush path where it is not fit for LLM automation.

---

## Scope

- update public tool docs and summaries
- update router metadata under `server/router/infrastructure/tools_metadata/sculpt/`
- update prompt docs if they reference sculpt flows
- explicitly mark old `sculpt_brush_*` tools as:
  - replaced by deterministic sculpt-region tools where applicable
  - non-primary and removable from the public LLM-facing sculpt path
- ensure new programmatic sculpt tools are the recommended LLM-facing tools

---

## Acceptance Criteria

- docs do not imply that brush setup tools are the best automation path
- metadata examples prefer programmatic sculpt tools
- replacement/removal posture is explicit instead of leaving a vague compatibility story
