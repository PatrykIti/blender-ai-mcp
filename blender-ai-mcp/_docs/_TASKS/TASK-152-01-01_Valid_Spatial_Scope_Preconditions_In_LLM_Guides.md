# TASK-152-01-01: Valid Spatial Scope Preconditions In LLM Guides

**Parent:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md)
**Status:** ✅ Done
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
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

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

## Planned Code / Doc Shape

```text
Prompt rule:
- Do not call scene_scope_graph()/scene_relation_graph() with no explicit scope
  and assume that this means “inspect the whole scene”.
- Use one of:
  - target_object=...
  - target_objects=[...]
  - collection_name=...
- For creature blockout:
  - first create meaningful primary masses or the build collection
  - then run the spatial gate on that scope
```

## Planned Unit Test Scenarios

- docs parity asserts wording equivalent to:
  - “scene_scope_graph(...) / scene_relation_graph(...) need explicit scope”
  - “scene_view_diagnostics(...) requires explicit scope”
  - “do not satisfy initial spatial gate from blank scene / no scope”

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

## Planned E2E Scenarios

- none directly from this leaf; covered indirectly by the transport leaves in
  `TASK-152-03`

## Changelog Impact

- include in the parent TASK-152 changelog entry

## Completion Summary

- prompt/docs contract now says plainly that spatial tools require explicit
  scope and that the initial spatial gate is only meaningful once a real target
  scope exists
