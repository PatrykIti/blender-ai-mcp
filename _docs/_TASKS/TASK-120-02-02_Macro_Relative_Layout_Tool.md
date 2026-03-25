# TASK-120-02-02: Macro Relative Layout Tool

**Parent:** [TASK-120-02](./TASK-120-02_First_Macro_Wave_Form_Cutout_And_Layout.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High

---

## Objective

Create a bounded macro for relative placement and layout between parts.

---

## Implementation Direction

- macro should own tasks such as:
  - align object A to object B
  - apply offsets along chosen axes
  - center/edge/face-oriented placement presets
  - optionally prepare for contact/gap validation
- macro should integrate with deterministic measure/assert follow-up, not guess correctness from prose
- macro should not become a generic transform sandbox

---

## Repository Touchpoints

- scene measurement/assertion layer from `TASK-116/117`
- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/contracts/`
- `server/router/infrastructure/tools_metadata/scene/`
- `tests/unit/tools/scene/`
- `tests/e2e/tools/scene/`

---

## Acceptance Criteria

- common part-layout tasks have one bounded macro path
- macro reports suggest deterministic validation when placement correctness matters
