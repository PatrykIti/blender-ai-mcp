# TASK-120-02-01: Macro Cutout/Recess Tool

**Parent:** [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

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

- likely new server-side orchestration in `server/application/services/` or `server/application/tool_handlers/`
- `server/adapters/mcp/areas/` and `server/adapters/mcp/contracts/`
- `server/router/infrastructure/tools_metadata/`
- existing scene/modeling/mesh handlers and their tests

---

## Acceptance Criteria

- common cutout/recess tasks no longer require multiple explicit low-level tool choices
- macro is bounded, inspectable, and verification-friendly
