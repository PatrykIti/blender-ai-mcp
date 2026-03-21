# TASK-091-05-01: Core Versioned Surface Tests and Documentation

**Parent:** [TASK-091-05](./TASK-091-05_Versioned_Surface_Tests_and_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-091-04](./TASK-091-04_Client_Selection_and_Bootstrap_Configuration.md)

---

## Objective

Implement the core code changes for **Versioned Surface Tests and Documentation**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_server_factory.py`
- `tests/unit/adapters/mcp/test_version_policy.py`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
---

## Planned Work

- compatibility snapshots per surface
- docs updates in:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
---

## Acceptance Criteria

- the migration path between surfaces is documented and testable
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
