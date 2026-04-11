# TASK-155-03-03: Seam Assertion Tolerance And Semantic Check Guidance

**Parent:** [TASK-155-03](./TASK-155-03_Guided_Tool_UX_And_Response_Budget.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Prevent guided seam validation from passing with overly permissive generic
assertions, such as allowing a small `Snout -> Head` gap by using
`scene_assert_contact(max_gap=0.1, allow_overlap=true)`.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/scene.py`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- required seam guidance prefers semantic attachment verdicts over ad hoc broad
  max-gap assertions
- embedded seams can allow overlap/intersection, but still reject meaningful
  visible separation
- segment/support seams keep strict contact requirements unless the runtime
  explicitly chooses a bounded blockout tolerance
- docs make the difference between generic contact assertions and required
  seam validation explicit

## Tests To Add/Update

- Unit:
  - add truth-followup cases in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - add relation graph verdict cases in
    `tests/unit/tools/test_handler_rpc_alignment.py`
  - update docs parity in `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - extend `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
    with a small embedded-seam gap that remains actionable

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- prompt/MCP guidance now steers required seam validation toward attachment
  verdicts and away from broad ad hoc tolerance checks
