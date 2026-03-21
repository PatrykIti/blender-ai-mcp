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
- add auth/visibility parity checks for discovery (`search_tools` / `call_tool`)
- benchmark visible tool count and payload size
- update:
  - `_docs/_MCP_SERVER/README.md`
  - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
  - `README.md`

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-05-01](./TASK-084-05-01_Core_Discovery_Tests_Benchmarks_Docs.md) | Core Discovery Tests, Benchmarks, and Docs | Core implementation layer |
| [TASK-084-05-02](./TASK-084-05-02_Tests_Discovery_Tests_Benchmarks_Docs.md) | Tests and Docs Discovery Tests, Benchmarks, and Docs | Tests, docs, and QA |

---

## Acceptance Criteria

- the repo has a measurable before/after view of discovery payload size
- documentation clearly explains when to use search-first discovery
- discovery path parity is proven for auth and visibility filtering
