# TASK-091-01: Versioning Policy and Surface Matrix

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

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

---

## Acceptance Criteria

- every public surface change has an explicit versioning policy

---

## Atomic Work Items

1. Define profile names and their default contract lines.
2. Define version lifecycle rules for introducing, deprecating, and removing public contracts.
3. Add one migration rule for converting current unversioned public tools into explicit `1.0` contracts.
