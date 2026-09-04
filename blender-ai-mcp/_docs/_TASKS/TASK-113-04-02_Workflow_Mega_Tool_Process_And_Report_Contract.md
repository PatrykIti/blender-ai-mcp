# TASK-113-04-02: Workflow/Mega Tool Process and Report Contract

**Parent:** [TASK-113-04](./TASK-113-04_Macro_And_Workflow_Tool_Design_Rules.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

---

## Objective

Define bounded workflow/mega tools as process tools with explicit internal phases and structured reporting.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `_docs/_ROUTER/README.md`
- docs for future workflow/macro tool areas

---

## Required Rules

- workflow/mega tools must remain bounded
- they can orchestrate:
  - atomic tools
  - macro tools
  - rule checks
  - before/after capture
  - measure/assert calls
- they must return structured outputs:
  - what they did
  - what changed
  - what passed/failed
  - recommended next step if verification failed

---

## Acceptance Criteria

- workflow/mega-tool docs define process boundaries and result contracts, not just “multi-step helper”
**Completion Summary:** Workflow/mega tools are now explicitly documented as bounded process tools with required structured reporting for what changed, what passed, what failed, and what should happen next.
