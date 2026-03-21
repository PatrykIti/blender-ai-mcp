# TASK-084-05: Discovery Tests, Benchmarks, and Docs

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-084-03](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md), [TASK-084-04](./TASK-084-04_Search_Execution_and_Router_Aware_Call_Path.md)

---

## Objective

Measure and document the effect of moving from flat discovery to search-first discovery.

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
