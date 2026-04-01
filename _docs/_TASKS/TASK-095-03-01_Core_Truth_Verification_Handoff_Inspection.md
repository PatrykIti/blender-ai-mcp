# TASK-095-03-01: Core Truth and Verification Handoff to Inspection Contracts

**Parent:** [TASK-095-03](./TASK-095-03_Truth_and_Verification_Handoff_to_Inspection_Contracts.md)  
**Status:** ✅ Done  
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

### Slice Outputs

- define concrete contract envelopes/schemas for the target capability family
- wire contracts through handler/adapter integration without changing domain ownership
- ensure renderer/serialization paths preserve structured-first guarantees

### Implementation Checklist

- touch `server/router/application/router.py` with explicit change notes and boundary rationale
- touch `server/router/application/engines/tool_correction_engine.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/contracts/scene.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/contracts/mesh.py` with explicit change notes and boundary rationale
- touch `tests/unit/router/application/test_tool_correction_engine.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- contract schemas are explicit, stable, and test-covered
- handler->adapter mapping is deterministic and backward-compatible where required
- invalid payloads fail fast with contract-level errors
- slice contracts are ready for higher-level audit/versioning integration

---

## Atomic Work Items

1. Implement schema/envelope definitions and integration in listed touchpoints.
2. Add contract tests for valid payloads, invalid payloads, and compatibility mode.
3. Capture representative before/after payload examples.
4. Document required and optional fields with ownership notes.
