# TASK-095-02: Discovery Handoff from LaBSE to FastMCP Search

**Parent:** [TASK-095](./TASK-095_LaBSE_Semantic_Layer_Boundaries.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-095-01](./TASK-095-01_Semantic_Responsibility_Policy_and_Code_Audit.md), [TASK-084-02](./TASK-084-02_Search_Transform_and_Pinned_Entry_Surface.md)

---

## Objective

Remove general MCP tool discovery from the semantic layer and move it onto FastMCP search controls.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-095-02-01](./TASK-095-02-01_Core_Discovery_Handoff_LaBSE_FastMCP.md) | Core Discovery Handoff from LaBSE to FastMCP Search | Core implementation layer |
| [TASK-095-02-02](./TASK-095-02-02_Tests_Discovery_Handoff_LaBSE_FastMCP.md) | Tests and Docs Discovery Handoff from LaBSE to FastMCP Search | Tests, docs, and QA |

---

## Acceptance Criteria

- tool discovery no longer depends on LaBSE classifiers

## Completion Summary

- platform-owned discovery files are covered by boundary tests and stay free of semantic matcher/classifier imports
- MCP tool discovery remains owned by FastMCP search instead of LaBSE-driven classifier paths
