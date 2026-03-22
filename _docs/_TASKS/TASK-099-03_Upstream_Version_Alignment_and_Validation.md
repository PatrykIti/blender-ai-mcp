# TASK-099-03: Upstream Version Alignment and Validation

**Parent:** [TASK-099](./TASK-099_FastMCP_Docket_Runtime_Alignment_and_Shims_Removal.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-02](./TASK-099-02_Runtime_Guards_and_Shim_Containment.md)

---

## Objective

Choose one supported FastMCP+Docket version pair and validate real task runtime against it.

---

## Repository Touchpoints

- `pyproject.toml`
- `poetry.lock`
- `tests/unit/adapters/mcp/`
- `_docs/`

---

## Planned Work

- choose the supported version pair
- update repo dependencies if needed
- validate real task runtime behavior on the selected pair

### Current Code Reality

The repo currently has:

- broad `fastmcp (>=3.0,<4.0)` declaration
- no explicit top-level Docket dependency declaration in `pyproject.toml`
- lockfile resolution that currently lands on `fastmcp 3.1.1`

This means version alignment work is not just a test step; it is also a dependency-policy step.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-099-03-01](./TASK-099-03-01_Core_Upstream_Version_Alignment.md) | Core Upstream Version Alignment | Core implementation layer |
| [TASK-099-03-02](./TASK-099-03-02_Tests_Upstream_Version_Alignment.md) | Tests Upstream Version Alignment | Tests, docs, and QA |

---

## Acceptance Criteria

- one supported version pair is selected and documented
- real task runtime works on that pair without relying on undefined behavior
