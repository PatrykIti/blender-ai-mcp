# TASK-091-03-01: Core Version-Filtered Server Composition

**Parent:** [TASK-091-03](./TASK-091-03_Version_Filtered_Server_Composition.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)

---

## Objective

Implement the core code changes for **Version-Filtered Server Composition**.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/version_policy.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_version_policy.py`
---

## Planned Work

- use built-in FastMCP `VersionFilter` in the server factory
- surface configs use `version_lt` or `version_gte` style filters

### Composition Rule

Apply version filters only after provider registration and public naming/contract metadata are already stable.
`VersionFilter` should shape public surfaces, not become a substitute for naming or renderer policy.
---

## Acceptance Criteria

- legacy and `llm-guided` surfaces can coexist on top of the same provider set

---

## Atomic Work Items

1. Add `VersionFilter` selection to profile composition.
2. Add one test for legacy-only exposure and one for llm-guided exposure.
3. Add one test ensuring unversioned internals do not leak unexpectedly into profile-specific public surfaces.
