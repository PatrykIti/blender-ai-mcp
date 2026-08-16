# TASK-120-02-03: Macro Finish Form Tool

**Parent:** [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `macro_finish_form` now exists as a bounded server-side finishing macro: it applies one controlled preset stack for rounded housing, panel finishing, shell thickening, or smooth subdivision, and returns the shared structured macro report with explicit verification follow-ups.

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
