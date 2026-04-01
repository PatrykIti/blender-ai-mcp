# TASK-091-03: Version-Filtered Server Composition

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)

---

## Objective

Compose separate public surfaces through version filtering instead of forking the entire tool catalog.

## Completion Summary

This slice is now closed.

- built-in `VersionFilter` is now part of surface composition
- version filtering coexists with profile selection and does not replace naming or visibility policy

---

## Planned Work

- use built-in FastMCP `VersionFilter` in the server factory
- surface configs use `version_lt` or `version_gte` style filters

### Composition Rule

Apply version filters only after provider registration and public naming/contract metadata are already stable.
`VersionFilter` should shape public surfaces, not become a substitute for naming or renderer policy.

Do not use `VersionFilter` as the first mechanism for creating `legacy-flat` versus `llm-guided`.
Profile composition should exist first; version filtering is an additive coexistence tool.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-091-03-01](./TASK-091-03-01_Core_Version_Filtered_Composition.md) | Core Version-Filtered Server Composition | Core implementation layer |
| [TASK-091-03-02](./TASK-091-03-02_Tests_Version_Filtered_Composition.md) | Tests and Docs Version-Filtered Server Composition | Tests, docs, and QA |

---

## Acceptance Criteria

- legacy and `llm-guided` surfaces can coexist on top of the same provider set
- version filtering is used only where multiple public contract versions actually exist

---

## Atomic Work Items

1. Add `VersionFilter` selection to profile composition only after the target profile matrix is already stable.
2. Add one test for legacy-only exposure and one for llm-guided exposure where a capability genuinely has multiple public contract versions.
3. Add one test ensuring unversioned internals do not leak unexpectedly into profile-specific public surfaces.
