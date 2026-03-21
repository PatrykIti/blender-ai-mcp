# TASK-085-05: Visibility Observability, Tests, and Docs

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-03](./TASK-085-03_Router_Driven_Phase_Transitions.md), [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md)

---

## Objective

Make visibility decisions observable, testable, and documented.

---

## Planned Work

- add snapshot tests for visible surface by phase and profile
- expose diagnostics such as:
  - current phase
  - active profile
  - hidden category counts
- update:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `README.md`

---

## Acceptance Criteria

- it is easy to inspect why a tool is visible or hidden
- visibility logic is not a black box
