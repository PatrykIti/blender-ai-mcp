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

- define explicit platform timeout settings for MCP tool execution and task-facing behavior
- ensure timeout configuration is deterministic, validated, and applied through the composition root
- keep invalid timeout values and unsupported combinations fail-fast with explicit errors

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

- timeout config contract is explicit (supported keys, defaults, ranges, invalid-value handling)
- factory/bootstrap applies timeout policy deterministically for target profiles
- invalid timeout config fails fast with actionable diagnostics
- scope remains platform timeout policy only; RPC/addon coordination stays in TASK-093-02-01-02

---

## Atomic Work Items

1. Implement timeout settings and validation rules in listed touchpoints.
2. Add focused tests for default values, valid overrides, and invalid timeout inputs.
3. Capture one before/after execution trace showing timeout policy application.
4. Document timeout policy boundaries vs RPC/addon timeout coordination scope.
