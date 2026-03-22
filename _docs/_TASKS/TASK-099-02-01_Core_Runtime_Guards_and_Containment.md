# TASK-099-02-01: Core Runtime Guards and Containment

**Parent:** [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md)

---

## Objective

Implement repo-side guards and make the temporary task-runtime shim explicit and bounded.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/runtime_compat.py`
- `server/adapters/mcp/factory.py`
- `server/main.py`

---

## Planned Work

- add runtime guard logic
- contain where the shim can activate
- surface clear failure messages for unsupported task-runtime combinations

### Guard Detail

- scope guard checks to task-enabled surfaces or task-mode activation paths
- avoid forcing global shim activation for server builds that do not need task execution
- make failure mode explicit at startup and/or first task-mode usage

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-02-01-01](./TASK-099-02-01-01_Runtime_Version_Guards_and_Error_Surfaces.md) | Runtime Version Guards and Error Surfaces | Guard / failure-mode slice |
| [TASK-099-02-01-02](./TASK-099-02-01-02_Shims_Containment_and_Instrumentation.md) | Shims Containment and Instrumentation | Shim-bounding slice |

---

## Acceptance Criteria

- guard behavior and shim containment exist in core repo code
