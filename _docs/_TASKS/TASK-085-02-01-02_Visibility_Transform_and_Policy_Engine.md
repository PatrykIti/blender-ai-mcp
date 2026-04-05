# TASK-085-02-01-02: Visibility Transform and Policy Engine

**Parent:** [TASK-085-02-01](./TASK-085-02-01_Core_Visibility_Engine_Tagged_Providers.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  

**Administrative Note:** Closed with the completed parent implementation wave. The planning sections below are retained as historical slice notes.

**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)  

---

## Objective

Implement the **Visibility Transform and Policy Engine** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/surfaces.py`

---

## Planned Work

### Slice Outputs

- materialize tag wiring and deterministic policy evaluation for visibility decisions
- apply visibility at the transform layer with profile/phase awareness
- preserve explicit override behavior for pinned or always-visible capabilities

### Implementation Checklist

- touch `server/adapters/mcp/transforms/visibility_policy.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/surfaces.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- visibility outcomes are deterministic for profile+phase+tag inputs
- transform-level filtering is test-covered and does not leak disabled components
- policy behavior is observable and debuggable through logs/diagnostics
- slice integrates cleanly with discovery and session-state assumptions

---

## Atomic Work Items

1. Implement tag mapping and visibility policy logic in listed touchpoints.
2. Add focused tests for allow, deny, overlap, and pinned-component behavior.
3. Capture a before/after component listing for at least two phases.
4. Document evaluation order and override semantics.
