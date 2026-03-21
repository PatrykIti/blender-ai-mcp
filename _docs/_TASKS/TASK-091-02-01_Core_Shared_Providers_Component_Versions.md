# TASK-091-02-01: Core Shared Providers with Component Versions

**Parent:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)  

---

## Objective

Implement the core code changes for **Shared Providers with Component Versions**.

---

## Repository Touchpoints

- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/providers/router_tools.py`
- `server/adapters/mcp/providers/workflow_tools.py`
- `server/adapters/mcp/platform/public_contracts.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`

---

## Planned Work

- Implement the primary code changes described in the parent task.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- Core implementation is complete and aligned with the parent scope.

---

## Atomic Work Items

1. Assign explicit baseline versions to the current public contracts on shared providers without duplicating handler implementations.
2. Add alternate versions only for capabilities whose public name, parameter contract, or response contract actually changes.
3. Keep internal canonical tool names and dispatcher mappings unversioned unless the internal execution contract truly changes.
