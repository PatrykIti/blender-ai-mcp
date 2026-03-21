# TASK-083-06-02: Tests and Docs Platform Regression Harness and Docs

**Parent:** [TASK-083-06](./TASK-083-06_Platform_Regression_Harness_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-06-01](./TASK-083-06-01_Core_Platform_Regression_Harness_Docs.md)

---

## Objective

Add tests and documentation updates for **Platform Regression Harness and Docs**.

---

## Repository Touchpoints

- `tests/unit/router/adapters/test_mcp_integration.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`
- `README.md`

---

## Planned Work

- Add unit/regression tests that cover the new behavior.
- Update docs and examples to reflect the surface change.
- Capture any compatibility or migration guidance if the surface changes.

---

## Acceptance Criteria

- Tests cover the new behavior with minimal regressions.
- Docs reflect the new contracts, surfaces, or policies.

---

## Atomic Work Items

1. Add or update unit tests for the new behavior.
2. Update `_docs/` and public docs as needed.
