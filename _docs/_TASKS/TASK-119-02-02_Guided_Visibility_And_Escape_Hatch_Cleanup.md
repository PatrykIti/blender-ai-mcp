# TASK-119-02-02: Guided Visibility and Escape Hatch Cleanup

**Parent:** [TASK-119-02](./TASK-119-02_Metadata_Discovery_And_Visibility_Drift_Cleanup.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Guided visibility and escape hatches were tightened: `llm-guided` now has a narrower router entry layer and a smaller, more intentional phased escape-hatch surface that excludes specialist families by default.

---

## Objective

Tighten the guided-surface boundary so the model-facing entry surface stays small
and explicit escape hatches do not quietly become the normal working path.

---

## Implementation Direction

- review `llm-guided` and related profiles for:
  - visible tool set
  - hidden args
  - search visibility
  - `call_tool` reachability
- decide which tools remain explicit public escape hatches and which should be
  fully hidden from production-oriented discovery
- benchmark the result by visible tool count, discovery payload size, and
  search-result quality

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/test_search_surface.py`
- `server/adapters/mcp/test_legacy_flat_pagination_compat.py`
- `server/adapters/mcp/test_code_mode_benchmarks.py`

---

## Acceptance Criteria

- guided surfaces remain intentionally small
- escape hatches are explicit and bounded instead of accidental surface leakage
