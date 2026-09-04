# TASK-144-03-02: On-Demand Reference Loop Adoption, Docs, And Regressions

**Parent:** [TASK-144-03](./TASK-144-03_Goal_Aware_Disclosure_Guided_Adoption_And_Regression_Pack.md)
**Status:** ✅ Done
**Priority:** 🟠 High
**Depends On:** [TASK-144-03-01](./TASK-144-03-01_LLM_Guided_Disclosure_And_Discovery_Shaping_For_View_Diagnostics.md), [TASK-144-02-02](./TASK-144-02-02_Scene_View_Diagnostics_Surface_RPC_Wiring_And_Metadata.md)

**Completion Summary:** Completed on 2026-04-07. Added bounded on-demand
guided-loop adoption for TASK-144: `reference_compare_current_view(...)` now
emits compact `view_diagnostics_hints` when the active framing/occlusion state
is ambiguous, while the default compare/iterate payloads stay free of a full
embedded view graph. Docs and regression coverage were updated accordingly.

## Objective

Teach the reference-guided loop how to use the new view diagnostics on demand
without turning the current compare/iterate contracts into heavyweight default
payloads.

This leaf also owns the docs and regression pack that keep that boundary
stable.

## Implementation Direction

- keep `reference_compare_current_view(...)` as a bounded capture-then-compare
  wrapper
- keep `reference_compare_stage_checkpoint(...)` /
  `reference_iterate_stage_checkpoint(...)` payloads focused on compare/truth
  outcomes; any inline view diagnostic must be compact and deliberately shaped
- update guided docs/prompting so operators know to call the view diagnostics
  when framing or occlusion ambiguity blocks the next compare/refinement step
- lock the public docs and regression suite so a future change cannot silently
  dump a full view graph into default loop responses

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/`
- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Acceptance Criteria

- the reference-guided loop can request or recommend view diagnostics when
  framing/occlusion ambiguity matters
- the default compare/iterate payloads do not grow into a heavyweight full
  view graph
- docs explain when view diagnostics should be called before another compare,
  capture, or refinement step
- regression coverage protects payload discipline, public docs alignment, and
  the view-space-vs-truth-space boundary

## Docs To Update

- `_docs/LLM_GUIDE_V2.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/vision/`

## Changelog Impact

- include in the parent TASK-144 changelog entry when shipped

## Status / Board Update

- closed on 2026-04-07 with the TASK-144 guided adoption wave
- tracked as completed through the closed parent/subtask state
