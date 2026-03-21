# TASK-087-06-01: Core Elicitation Tests and Docs

**Parent:** [TASK-087-06](./TASK-087-06_Elicitation_Tests_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-087-03](./TASK-087-03_Constrained_Choice_and_Multi_Select_Flows.md), [TASK-087-04](./TASK-087-04_Session_Persistence_Retry_and_Cancel_Semantics.md), [TASK-087-05](./TASK-087-05_Tool_Only_Fallback_and_Compatibility_Mode.md)

---

## Objective

Implement the core code changes for **Elicitation Tests and Docs**.

---

## Repository Touchpoints

- `tests/unit/router/domain/entities/test_elicitation.py`
- `tests/unit/router/application/test_router_handler_parameters.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
---

## Planned Work

- unit contract tests
- router handler tests
- compatibility tests for fallback clients
- docs updates in:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `README.md`
---

## Acceptance Criteria

- both interaction modes are documented and regression-tested
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
