# TASK-091-03: Version-Filtered Server Composition

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)

---

## Objective

Compose separate public surfaces through version filtering instead of forking the entire tool catalog.

---

## Planned Work

- implement `server/adapters/mcp/transforms/versioning.py`
- surface configs use `version_lt` or `version_gte` style filters

---

## Acceptance Criteria

- legacy and LLM-first surfaces can coexist on top of the same provider set
