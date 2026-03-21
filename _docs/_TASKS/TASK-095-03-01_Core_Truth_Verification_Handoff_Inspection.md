# TASK-095-03-01: Core Truth and Verification Handoff to Inspection Contracts

**Parent:** [TASK-095-03](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md), [TASK-089-03](./TASK-089-03_Structured_Mesh_Introspection_Contracts.md)

---

## Objective

Implement the core code changes for **Truth and Verification Handoff to Inspection Contracts**.

---

## Repository Touchpoints

- `server/router/application/router.py`
- `server/router/application/engines/tool_correction_engine.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/mesh.py`
- `tests/unit/router/application/test_tool_correction_engine.py`
---

## Planned Work

- Implement the concrete leaf scope implied by the parent task in the listed touchpoints.
- Keep responsibilities aligned with Clean Architecture and `RESPONSIBILITY_BOUNDARIES.md`.
- Avoid introducing new bootstrap side effects outside the platform composition root.

---

## Acceptance Criteria

- semantic confidence is not used as a proxy for scene truth
---

## Atomic Work Items

1. Identify every place where semantic confidence currently leaks into truth-like decisions.
2. Replace those decisions with explicit inspection contract checks.
3. Add tests proving scene truth no longer depends on semantic score alone.