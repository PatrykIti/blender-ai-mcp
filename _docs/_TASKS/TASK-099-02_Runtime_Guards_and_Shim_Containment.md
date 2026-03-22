# TASK-099-02: Runtime Guards and Shim Containment

**Parent:** [TASK-099](./TASK-099_FastMCP_Docket_Runtime_Alignment_and_Shims_Removal.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)

---

## Objective

Contain the temporary compatibility shim and add fail-fast diagnostics for unsupported runtime pairs.

---

## Repository Touchpoints

- `server/adapters/mcp/tasks/runtime_compat.py`
- `server/adapters/mcp/factory.py`
- `server/main.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/`

---

## Planned Work

- add explicit guards for unsupported runtime combinations
- make shim activation visible and scoped
- improve error messaging when task mode is unavailable because of runtime mismatch

### Current Code Reality

Today the shim is activated unconditionally from `factory.py`.
There is no explicit “supported pair” guard and no fail-fast path that explains to maintainers which runtime combination is unsupported.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-02-01](./TASK-099-02-01_Core_Runtime_Guards_and_Containment.md) | Core Runtime Guards and Containment | Core implementation layer |
| [TASK-099-02-02](./TASK-099-02-02_Tests_Runtime_Guards_and_Containment.md) | Tests Runtime Guards and Containment | Tests, docs, and QA |

---

## Acceptance Criteria

- unsupported version pairs fail clearly
- the temporary shim is explicit, bounded, and test-covered
