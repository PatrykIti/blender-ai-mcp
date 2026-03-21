# TASK-091-01: Versioning Policy and Surface Matrix

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md), [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md), [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Define the surface matrix and the lifecycle rules for public component versions.

---

## Planned Work

- create `server/adapters/mcp/version_policy.py`
- define surfaces such as:
  - `legacy-flat`
  - `llm-guided`
  - `internal-debug`

### Distinction Rule

This task must define two matrices:

- surface profile matrix
- contract version matrix

Example:

- profile `legacy-flat` may prefer contract line `legacy-v1`
- profile `llm-guided` may prefer contract line `llm-v2`

### Activation Gate

Do not use this task to invent contract lines before:

- one stable `llm-guided` public naming baseline exists
- one stable structured contract baseline exists
- there is a real need to keep more than one public contract alive at once

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-091-01-01](./TASK-091-01-01_Core_Versioning_Matrix.md) | Core Versioning Policy and Surface Matrix | Core implementation layer |
| [TASK-091-01-02](./TASK-091-01-02_Tests_Versioning_Matrix.md) | Tests and Docs Versioning Policy and Surface Matrix | Tests, docs, and QA |

---

## Acceptance Criteria

- every public surface change that truly needs coexistence has an explicit versioning policy
- profile composition and contract versioning remain two separate axes

---

## Atomic Work Items

1. Define profile names and their default contract lines only for capabilities that truly need coexistence.
2. Define version lifecycle rules for introducing, deprecating, and removing public contracts.
3. Freeze the initial public naming and contract baseline before converting current unversioned tools into explicit `1.0` contracts.
4. Keep profile composition and versioning as separate axes; do not use versioning to compensate for an unstable profile design.
