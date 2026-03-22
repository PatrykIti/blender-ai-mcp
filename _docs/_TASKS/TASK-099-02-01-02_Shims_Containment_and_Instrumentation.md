# TASK-099-02-01-02: Shims Containment and Instrumentation

**Parent:** [TASK-099-02-01](./TASK-099-02-01_Core_Runtime_Guards_and_Containment.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)

---

## Objective

Keep the temporary compatibility shim explicit, bounded, and instrumented until it can be removed.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/runtime_compat.py`
- `_docs/`

---

## Planned Work

- restrict shim behavior to the known mismatch
- document or instrument when the shim is active

### Containment Detail

- avoid broad mutation when the expected upstream symbol already exists
- consider exposing diagnostics or log markers when shim activation occurs
- keep the mutation limited to the known Docket dependency surface

---

## Acceptance Criteria

- the repo does not silently normalize the shim as a permanent runtime layer
