# TASK-119-03-02: Surface Regression and Benchmark Pack

**Parent:** [TASK-119-03](./TASK-119-03_Docs_Prompts_And_Regression_Hardening.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The hardened public surface is now protected by a dedicated regression/benchmark pack covering visibility, discovery, docs references, contract baseline expectations, and explicit guided-surface phase benchmarks.

---

## Objective

Protect the hardened public surface with focused regression and benchmark tests.

---

## Implementation Direction

- keep visible-tool counts and payload-size baselines intentional
- regression-test:
  - aliasing
  - hidden args
  - output schemas
  - docs references
  - search/call-tool restrictions
- add a small benchmark/memo path for “surface got larger or noisier” regressions

---

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_code_mode_benchmarks.py`
- `_docs/_TESTS/README.md`

---

## Acceptance Criteria

- public-surface hardening remains test-protected
- a later macro-wave can rely on a stable pre-macro baseline
