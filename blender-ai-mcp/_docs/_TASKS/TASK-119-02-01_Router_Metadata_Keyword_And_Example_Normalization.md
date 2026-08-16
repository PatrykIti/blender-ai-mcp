# TASK-119-02-01: Router Metadata Keyword and Example Normalization

**Parent:** [TASK-119-02](./TASK-119-02_Metadata_Discovery_And_Visibility_Drift_Cleanup.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Router metadata was normalized for the highest-value public layer: keywords, sample prompts, descriptions, and related-tool hints now reflect grouped/public usage and no longer point at stale or non-existent tool paths.

---

## Objective

Normalize router metadata so examples, keywords, and related-tool hints bias the
model toward the intended grouped/public layer.

---

## Implementation Direction

- review high-value metadata files in:
  - `scene/`
  - `mesh/`
  - `system/`
  - `workflow/`-adjacent surfaces where discovery language matters
- rewrite `keywords`, `sample_prompts`, and `related_tools` to prefer:
  - grouped tools over historical atomics
  - macro/workflow-oriented entry points where already available
  - verification-aware follow-up suggestions
- remove examples that imply “pick from the whole low-level catalog”

---

## Repository Touchpoints

- `server/router/infrastructure/tools_metadata/**/*.json`
- `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

---

## Acceptance Criteria

- metadata examples reflect the current product model rather than the historical catalog shape
- metadata remains schema-valid and signature-aligned
