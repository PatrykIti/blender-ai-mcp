# TASK-120-02-03: Macro Finish Form Tool

**Parent:** [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Create a bounded macro for common hard-surface finishing moves such as bevel,
subdivision, shell/solidify, and controlled smoothing.

---

## Implementation Direction

- macro should expose bounded finishing presets instead of raw modifier soup
- macro should own:
  - rounded housing / panel finishing
  - simple shell thickening
  - controlled smoothing/subsurf presets
- macro should emit created/modified object state and applied finishing stack
- macro should stop short of full parametric style generation

---

## Repository Touchpoints

- `server/application/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/areas/`
- modeling/scene handler surfaces already used for modifier application
- `tests/unit/tools/modeling/`
- `tests/e2e/tools/modeling/`

---

## Acceptance Criteria

- common finishing flows have a bounded macro entry point
- the macro remains explicit enough to be debuggable and verification-aware
