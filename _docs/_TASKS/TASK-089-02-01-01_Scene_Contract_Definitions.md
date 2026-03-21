# TASK-089-02-01-01: Scene Contract Definitions

**Parent:** [TASK-089-02-01](./TASK-089-02-01_Core_Structured_Scene_Context_Inspection.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-089-02](./TASK-089-02_Structured_Scene_Context_and_Inspection_Contracts.md)  

---

## Objective

Implement the **Scene Contract Definitions** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/domain/tools/scene.py`

---

## Planned Work

### Slice Outputs

- define concrete contract envelopes/schemas for the target capability family
- wire contracts through handler/adapter integration without changing domain ownership
- ensure renderer/serialization paths preserve structured-first guarantees

### Implementation Checklist

- touch `server/adapters/mcp/contracts/scene.py` with explicit change notes and boundary rationale
- touch `server/domain/tools/scene.py` with explicit change notes and boundary rationale
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

### Concrete DoD by Touchpoint

- `server/adapters/mcp/contracts/scene.py`
  - defines versionable contract models for at least: mode/selection, object inspection, snapshot state, snapshot diff
  - each contract includes explicit required/optional fields and validation rules
  - serializer output is deterministic across repeated runs on identical input
- `server/domain/tools/scene.py`
  - interface-level return contracts remain framework-agnostic
  - domain signatures do not import adapter/framework contract classes directly

---

## Atomic Work Items

1. Implement schema/envelope definitions and integration in listed touchpoints.
2. Add contract tests for valid payloads, invalid payloads, and compatibility mode.
3. Capture representative before/after payload examples.
4. Document required and optional fields with ownership notes.
