# TASK-083-03-01-01: Surface Profile Settings and Config

**Parent:** [TASK-083-03-01](./TASK-083-03-01_Core_Factory_Composition_Root.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  

---

## Objective

Implement the **Surface Profile Settings and Config** slice of the parent task.

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/settings.py`
- `server/adapters/mcp/surfaces.py`

---

## Planned Work

### Slice Outputs

- deliver profile/bootstrap behavior through composition-root configuration, not side effects
- ensure profile selection resolves deterministic provider and transform sets
- keep startup failure modes explicit and config-driven

### Implementation Checklist

- touch `server/infrastructure/config.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/settings.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/surfaces.py` with explicit change notes and boundary rationale
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

---

## Atomic Work Items

1. Implement config/profile handling in listed touchpoints and document supported modes.
2. Add focused tests for valid profiles, invalid profiles, and default fallback behavior.
3. Capture one before/after bootstrap trace proving composition-root ownership.
4. Document migration notes for downstream tasks that depend on this slice.
