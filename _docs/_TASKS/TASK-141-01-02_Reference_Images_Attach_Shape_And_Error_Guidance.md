# TASK-141-01-02: `reference_images(...)` Attach Shape and Error Guidance

**Parent:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md)
**Depends On:** [TASK-141-01-01](./TASK-141-01-01_Call_Tool_Wrapper_Aliases_And_Cleanup_Flag_Compatibility.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `reference_images(action="attach", source_path=..., ...)` one explicit
guided contract and give repeated batch-attach drift a deterministic recovery
path.

## Business Problem

The public guided surface exposes `reference_images(...)` as a small lifecycle
tool, but creature sessions still guess a batch-upload shape such as
`images=[...]`. That produces avoidable rediscovery cost right at the point
where the model is trying to start a staged reference-driven build.

This leaf owns the product decision for attach-shape ergonomics:

- one canonical attach story
- one explicit compatibility or rejection policy for batch-like drift
- one aligned docs/test story for staged pending-reference behavior

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- the canonical attach shape is `reference_images(action="attach", source_path=..., ...)`
- the guided runtime no longer treats batch-like attach drift as an opaque
  contract mismatch when it can provide specific recovery guidance
- docs/examples show that each reference is attached in its own call
- pending/staged-reference wording stays aligned with the canonical
  one-reference-per-attach story

## Leaf Work Items

- define the compatibility/rejection policy for batch-like attach attempts
- implement actionable attach-shape guidance in the reference image surface
  where the runtime can detect the drift
- align prompt/docs examples to repeat one `attach` call per reference image
- add focused regression coverage for canonical attach and repeated wrong-shape
  attempts

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- update the parent task summary so it explicitly calls out the final
  `reference_images(...)` attach policy when this leaf closes
