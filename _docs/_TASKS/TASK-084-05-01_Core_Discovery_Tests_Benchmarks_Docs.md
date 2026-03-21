# TASK-084-05-01: Core Discovery Tests, Benchmarks, and Docs

**Parent:** [TASK-084-05](./TASK-084-05_Discovery_Tests_Benchmarks_and_Docs.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-084-03](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md), [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md)

---

## Objective

Implement the core code changes for **Discovery Tests, Benchmarks, and Docs**.

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
---

## Planned Work

- add snapshot tests for `legacy-flat` vs `llm-guided` `list_tools`
- benchmark visible tool count and payload size
- update:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `README.md`
---

## Acceptance Criteria

- the repo has a measurable before/after view of discovery payload size
- documentation clearly explains when to use search-first discovery
---

## Atomic Work Items

1. Implement the leaf scope in the listed touchpoints.
2. Keep the implementation aligned with the parent task boundaries and the existing runtime call path.
