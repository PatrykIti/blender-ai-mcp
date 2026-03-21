# TASK-093-02-01-01: Platform Timeout Policy and Config

**Parent:** [TASK-093-02-01](./TASK-093-02-01_Core_Timeout.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-093-02](./TASK-093-02_Tool_and_Task_Timeout_Policy.md)  

---

## Objective

Implement the **Platform Timeout Policy and Config** slice of the parent task.

---

## Repository Touchpoints

- `server/infrastructure/config.py`
- `server/adapters/mcp/factory.py`

---

## Planned Work

### Slice Outputs

- deliver profile/bootstrap behavior through composition-root configuration, not side effects
- ensure profile selection resolves deterministic provider and transform sets
- keep startup failure modes explicit and config-driven

### Implementation Checklist

- touch `server/infrastructure/config.py` with explicit change notes and boundary rationale
- touch `server/adapters/mcp/factory.py` with explicit change notes and boundary rationale
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
