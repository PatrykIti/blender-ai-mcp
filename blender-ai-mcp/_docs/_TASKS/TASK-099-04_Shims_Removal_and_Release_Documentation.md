# TASK-099-04: Shims Removal and Release Documentation

**Parent:** [TASK-099](./TASK-099_FastMCP_Docket_Runtime_Alignment_and_Shims_Removal.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-099-03](./TASK-099-03_Upstream_Version_Alignment_and_Validation.md)

---

## Objective

Remove the repo-local runtime compatibility shim and close the task with release/docs updates.

---

## Planned Work

- remove or neutralize `runtime_compat.py`
- update release/docs/test notes to reflect the supported runtime baseline

### Previous Code Reality

Before completion, `runtime_compat.py` was a real behavioral dependency:

- factory called it
- task bridge assumed it might be needed
- one unit test asserted the alias existed

This final slice removed those assumptions rather than only deleting the file.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-04-01](./TASK-099-04-01_Core_Shims_Removal.md) | Core Shims Removal | Core implementation layer |
| [TASK-099-04-02](./TASK-099-04-02_Tests_Shims_Removal_and_Release_Documentation.md) | Tests Shims Removal and Release Documentation | Tests, docs, and QA |

---

## Acceptance Criteria

- the repo-local shim is gone or no longer behaviorally required
- release/docs/test guidance reflects the final aligned runtime baseline

## Completion Summary

- `runtime_compat.py` is removed
- factory and task bridge now rely on explicit runtime policy instead of mutation-based compatibility patching
- release/platform docs now describe the aligned no-shim baseline
