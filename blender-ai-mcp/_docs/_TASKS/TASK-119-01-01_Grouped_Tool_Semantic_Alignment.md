# TASK-119-01-01: Grouped Tool Semantic Alignment

**Parent:** [TASK-119-01](./TASK-119-01_Public_Tool_Semantics_And_Contract_Hardening.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** Grouped/high-value public tools were aligned around the current product model: aliases, examples, and model-facing wording now consistently treat grouped tools as the intended public working layer.

---

## Objective

Audit and fix grouped/high-value public tools so their docstrings, parameter
wording, and usage examples consistently express the current product model.

---

## Implementation Direction

- review grouped tools such as `scene_context`, `scene_inspect`, `scene_configure`,
  `mesh_inspect`, `mesh_select`, `mesh_select_targeted`, `workflow_catalog`,
  `search_tools`, and `call_tool`
- remove or rewrite wording that still implies flat-catalog/manual-first usage
- ensure every grouped/public tool clearly states:
  - what it owns
  - what it does not own
  - what follow-up verification is expected
- normalize public aliases and hidden-argument behavior for `llm-guided`

---

## Repository Touchpoints

- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/platform/naming_rules.py`
- `server/adapters/mcp/transforms/public_params.py`
- `tests/unit/adapters/mcp/test_aliasing_transform.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

---

## Acceptance Criteria

- grouped/public tool docstrings no longer teach the older low-level product story
- alias and hidden-argument behavior remains explicit and regression-tested
