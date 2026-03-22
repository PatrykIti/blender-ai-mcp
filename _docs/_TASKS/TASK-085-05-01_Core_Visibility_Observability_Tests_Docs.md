# TASK-085-05-01: Core Visibility Observability, Tests, and Docs

**Parent:** [TASK-085-05](./TASK-085-05_Visibility_Observability_Tests_and_Docs.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-03](./TASK-085-03_Router_Driven_Phase_Transitions.md), [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md)

---

## Objective

Implement the core code changes for **Visibility Observability, Tests, and Docs**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_server_factory.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
---

## Planned Work

- add snapshot tests for visible surface by phase and profile
- expose diagnostics such as:
  - current phase
  - active profile
  - hidden category counts
- update:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/_PROMPTS/README.md`
  - `README.md`
---

## Acceptance Criteria

- it is easy to inspect why a tool is visible or hidden
- visibility logic is not a black box
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
