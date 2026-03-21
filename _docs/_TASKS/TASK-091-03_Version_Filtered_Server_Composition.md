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

- use built-in FastMCP `VersionFilter` in the server factory
- surface configs use `version_lt` or `version_gte` style filters

---

## Acceptance Criteria

- legacy and `llm-guided` surfaces can coexist on top of the same provider set

---

## Atomic Work Items

1. Add `VersionFilter` selection to profile composition.
2. Add one test for legacy-only exposure and one for llm-guided exposure.
3. Add one test ensuring unversioned internals do not leak unexpectedly into profile-specific public surfaces.
