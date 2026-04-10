# TASK-152-01-01: Valid Spatial Scope Preconditions In LLM Guides

**Parent:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Spell out the real preconditions for guided spatial-tool usage so the model
does not try to satisfy `establish_spatial_context` with empty scope or
meaningless helper objects.

## Repository Touchpoints

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Planned Guidance Shape

- explicitly say:
  - `scene_scope_graph(...)` / `scene_relation_graph(...)` need
    `target_object`, `target_objects`, or `collection_name`
  - `scene_view_diagnostics(...)` also requires explicit scope
  - on creature blockout, do not try to satisfy the initial spatial gate until
    a real target scope exists, e.g.:
    - primary masses already exist
    - or the build collection exists
    - or there is a meaningful part set to inspect

## Acceptance Criteria

- no prompt asset suggests that the spatial gate can be satisfied from a blank
  scene call with no scope
- at least one prompt asset includes a positive example using
  `scene_scope_graph(target_object=..., target_objects=[...])` or
  `collection_name=...`

## Docs To Update

- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
