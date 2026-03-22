# TASK-091-05: Versioned Surface Tests and Documentation

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-04](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md)

---

## Objective

Add coexistence tests and migration documentation for the versioned-surface model.

## Completion Summary

This slice is now closed.

- coexistence/rollback tests now cover the current versioned surface baseline
- public docs describe the contract-line matrix and the guided-surface rollback path

---

## Planned Work

- compatibility snapshots per surface
- docs updates in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-091-05-01](./TASK-091-05-01_Core_Versioned_Tests_Documentation.md) | Core Versioned Surface Tests and Documentation | Core implementation layer |
| [TASK-091-05-02](./TASK-091-05-02_Tests_Versioned_Tests_Documentation.md) | Tests and Docs Versioned Surface Tests and Documentation | Tests, docs, and QA |

---

## Acceptance Criteria

- the migration path between surfaces is documented and testable
