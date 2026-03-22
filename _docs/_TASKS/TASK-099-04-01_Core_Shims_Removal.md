# TASK-099-04-01: Core Shims Removal

**Parent:** [TASK-099-04](./TASK-099-04_Shims_Removal_and_Release_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md)

---

## Objective

Remove the repo-local compatibility shim once the supported runtime pair is validated.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/runtime_compat.py`
- `server/adapters/mcp/factory.py`
- related task/runtime tests

---

## Planned Work

- remove the temporary shim path
- simplify startup/runtime code accordingly

### Removal Detail

- remove the `factory.py` bootstrap dependency on the shim
- remove or simplify any task-bridge assumptions that the shim may still be needed
- update tests that currently assert shimmed alias presence

---

## Acceptance Criteria

- runtime alignment no longer depends on repo-local compatibility patching
