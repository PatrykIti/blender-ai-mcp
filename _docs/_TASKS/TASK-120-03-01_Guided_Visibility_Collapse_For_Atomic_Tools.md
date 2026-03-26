# TASK-120-03-01: Guided Visibility Collapse for Atomic Tools

**Parent:** [TASK-120-03](./TASK-120-03_Guided_Surface_Collapse_And_Discovery_Preference.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** `llm-guided` visibility is now deliberately smaller and more phase-shaped: bootstrap stays entry-only/search-first, build exposes the bounded macro layer plus targeted escape hatches, and hidden low-level modifier atomics remain unavailable on the shaped public surface.

---

## Objective

Shrink `llm-guided` further by hiding atomics that now have better macro-layer
counterparts.

---

## Implementation Direction

- identify atomics that become redundant on `llm-guided` after macro introduction
- keep internal/debug paths intact
- preserve explicit expert escape hatches only where needed
- keep visibility changes benchmarked and regression-tested

---

## Repository Touchpoints

- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_search_surface.py`

---

## Acceptance Criteria

- `llm-guided` gets smaller or stays similarly small while becoming more capable
- removed atomics still remain available where internal/router execution needs them
