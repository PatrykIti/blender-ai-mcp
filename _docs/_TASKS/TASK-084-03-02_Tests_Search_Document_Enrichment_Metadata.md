# TASK-084-03-02: Tests and Docs Search Document Enrichment from Metadata and Docstrings

**Parent:** [TASK-084-03](./TASK-084-03_Search_Document_Enrichment_from_Metadata_and_Docstrings.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-084-03-01](./TASK-084-03-01_Core_Search_Document_Enrichment_Metadata.md)

---

## Objective

Add tests and documentation updates for **Search Document Enrichment from Metadata and Docstrings**.

## Completion Summary

This slice is now closed.

- discovery tests now cover enriched public-name search behavior on the preview surface
- metadata/document enrichment is exercised through the search-surface and tool-inventory test suite

---

## Repository Touchpoints

- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `_docs/`

---

## Planned Work

### Regression Scenarios (Required)

1. search/discovery happy path: expected tools are discoverable and callable through the intended public path.
2. pinned-entry behavior: pinned tools remain visible while non-pinned tools are hidden from flat listing.
3. negative query path: irrelevant query returns bounded, deterministic results without leaking hidden tools.
4. router/dispatcher parity: discovered execution path matches direct execution behavior for the same tool call.

### Metrics To Capture

- `tools/list` payload size before/after (bytes)
- visible tool count per surface profile (`legacy-flat` vs `llm-guided`)
- top-N discovery relevance sanity check on curated queries

### Documentation Deliverables

- update task-linked docs with a before/after summary tied to the captured metrics
- document exact test commands, fixtures, and profile/config used during validation
- record compatibility or migration notes when behavior differs between surfaces

---

## Acceptance Criteria

- all required regression scenarios are implemented and passing in CI/local test runs
- metrics are captured with baseline vs post-change values and attached to the task update
- docs include the regression matrix and explain expected behavior boundaries
- no untracked regressions are observed on related router/dispatcher/platform paths

---

## Atomic Work Items

1. Implement the required regression scenarios in focused unit/integration tests.
2. Run the target suites, collect metric outputs, and compare to baseline values.
3. Update docs with regression matrix, metric table, and migration/compatibility notes.
4. Verify adjacent surfaces for spillover regressions and document the result.
