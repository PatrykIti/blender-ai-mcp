# TASK-113-02-01: Profile Surface Exposure Matrix

**Parent:** [TASK-113-02](./TASK-113-02_Surface_Exposure_Matrix_And_Hidden_Atomic_Layer.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The intended posture for `legacy-manual`, `legacy-flat`, `llm-guided`, `internal-debug`, and `code-mode-pilot` is now documented and linked from the canonical policy source and MCP docs.

---

## Objective

Define the intended exposure model for each surface/profile.

---

## Exact Documentation Targets

- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/_TASKS/TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md`

---

## Surface Matrix To Define

- `legacy-manual`
  - maintainer/manual-heavy
  - broad but still not necessarily “everything public forever”
- `legacy-flat`
  - compatibility/control baseline
- `llm-guided`
  - small public LLM-facing catalog
  - goal-first by default
- `internal-debug`
  - maintainer/debug
- future production surfaces
  - macro/workflow-first, not atomic-first

---

## Acceptance Criteria

- each surface has a documented public/private tool exposure rule
- no production-oriented surface is described as “full flat catalog by default”
