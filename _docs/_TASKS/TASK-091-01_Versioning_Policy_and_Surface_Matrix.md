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
  - `llm-first-v1`
  - `internal-debug`

---

## Acceptance Criteria

- every public surface change has an explicit versioning policy
