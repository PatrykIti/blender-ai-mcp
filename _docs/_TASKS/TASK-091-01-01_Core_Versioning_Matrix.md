# TASK-091-01-01: Core Versioning Policy and Surface Matrix

**Parent:** [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md)  

---

## Objective

Implement the core code changes for **Versioning Policy and Surface Matrix**.

---

## Repository Touchpoints

- `server/adapters/mcp/version_policy.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/platform/public_contracts.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_version_policy.py`

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

1. Define one explicit matrix mapping surface profiles to preferred contract lines and deprecation policy.
2. Convert current public contracts into explicit baseline `1.x` lines only after public naming and renderer rules are frozen.
3. Keep version policy owned by the platform layer rather than scattered across area modules or router metadata.
