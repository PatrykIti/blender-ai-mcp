# TASK-083-03-01-02: Server Factory and Bootstrap Path

**Parent:** [TASK-083-03-01](./TASK-083-03-01_Core_Factory_Composition_Root.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  

---

## Objective

Implement the **Server Factory and Bootstrap Path** slice of the parent task.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/server.py`
- `server/main.py`
- `server/adapters/mcp/instance.py`

---

## Planned Work

### Slice Outputs

- deliver profile/bootstrap behavior through composition-root configuration, not side effects
- ensure profile selection resolves deterministic provider and transform sets
- keep startup failure modes explicit and config-driven

### Implementation Checklist

- touch `server/adapters/mcp/factory.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/server.py` with explicit change notes and boundary rationale
- touch `server/main.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/instance.py` with explicit change notes and boundary rationale
- add or update focused regression coverage for the slice behavior
- capture before/after evidence tied to the slice outputs

### Review Notes To Attach

- rationale per changed touchpoint and any explicit no-change decisions
- exact test commands and profile/config context used during validation
- deferred work list with safety rationale

---

## Acceptance Criteria

- profile/bootstrap behavior is deterministic and test-covered
- config contract is explicit (supported values, defaults, invalid-value handling)
- no new startup side effects are introduced outside composition root
- slice output remains compatible with parent migration gates

### Concrete DoD by Touchpoint

- `server/adapters/mcp/factory.py`
  - exposes `build_server(surface_profile=...)` as the primary composition entrypoint
  - assembles providers and transforms from explicit profile settings, not import side effects
- `server/adapters/mcp/server.py`
  - runtime startup uses factory-built server instance
  - profile selection and startup errors are logged with actionable diagnostics
- `server/main.py`
  - no direct reliance on global tool-registration side effects
  - bootstrap path supports at least default profile and one non-default profile in tests
- `server/adapters/mcp/instance.py`
  - reduced to compatibility shim or clearly marked transitional module

---

## Atomic Work Items

1. Implement config/profile handling in listed touchpoints and document supported modes.
2. Add focused tests for valid profiles, invalid profiles, and default fallback behavior.
3. Capture one before/after bootstrap trace proving composition-root ownership.
4. Document migration notes for downstream tasks that depend on this slice.
