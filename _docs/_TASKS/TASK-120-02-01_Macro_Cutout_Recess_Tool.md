# TASK-120-02-01: Macro Cutout/Recess Tool

**Parent:** [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `macro_cutout_recess` now exists as a bounded server-side orchestrator over existing atomics: it creates and places a cutter on one bbox face, optionally bevels it, applies a boolean difference, cleans up the helper object, and returns a structured macro report with follow-up verification recommendations.

---

## Objective

Create a bounded macro for “make a recess/cutout here” style tasks, which are
currently too atomic-heavy for normal LLM usage.

---

## Implementation Direction

- macro should orchestrate:
  - cutter creation
  - cutter transform/layout
  - optional cutter bevel/rounding
  - boolean difference/intersection as appropriate
  - cleanup of helper geometry
- macro should return structured process/report data rather than a loose string
- macro should stay bounded to recess/cutout intent, not full shape reconstruction

---

## Repository Touchpoints

- `server/domain/tools/macro.py`
- `server/application/tool_handlers/macro_handler.py`
- `server/adapters/mcp/areas/modeling.py`
- `server/adapters/mcp/contracts/macro.py`
- `server/infrastructure/di.py`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/modeling/macro_cutout_recess.json`
- `tests/unit/tools/macro/`
- `tests/unit/tools/modeling/`
- `tests/unit/adapters/mcp/`

---

## Acceptance Criteria

- common cutout/recess tasks no longer require multiple explicit low-level tool choices
- macro is bounded, inspectable, and verification-friendly
