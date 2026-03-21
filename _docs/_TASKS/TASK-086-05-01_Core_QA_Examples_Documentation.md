# TASK-086-05-01: Core Surface QA, Examples, and Documentation

**Parent:** [TASK-086-05](./TASK-086-05_Surface_QA_Examples_and_Documentation.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-086-03](./TASK-086-03_LLM_First_Surface_Simplification_and_Hidden_Args.md), [TASK-086-04](./TASK-086-04_Compatibility_Adapters_and_Dispatcher_Alignment.md)

---

## Objective

Implement the core code changes for **Surface QA, Examples, and Documentation**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
---

## Planned Work

- snapshot tests for public surface schemas
- update:
  - `README.md`
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `_docs/_PROMPTS/*`
---

## Acceptance Criteria

- docs and prompt examples use the new public surface consistently
- regressions in naming or parameter visibility are caught by tests
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
