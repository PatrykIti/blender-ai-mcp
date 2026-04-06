# TASK-141-01-02: `reference_images(...)` Attach Shape and Error Guidance

**Parent:** [TASK-141-01](./TASK-141-01_Guided_Call_Path_Compatibility_And_Public_Contract_Ergonomics.md)
**Depends On:** [TASK-141-01-01](./TASK-141-01-01_Call_Tool_Wrapper_Aliases_And_Cleanup_Flag_Compatibility.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make `reference_images(action="attach", source_path=..., ...)` one explicit
guided contract and give repeated batch-attach drift a deterministic recovery
path on the real shaped surface used by live creature sessions.

## Business Problem

The public guided surface exposes `reference_images(...)` as a small lifecycle
tool, but a live creature run still treats the first reference step as
high-friction:

- models guess batch-upload shapes such as `images=[...]`
- the attach contract still has to coexist with staged pending-reference
  behavior before/after `router_set_goal(...)`
- the surface must stay understandable even when compare/iterate later run in a
  degraded mode and the operator has to inspect the current reference state

This leaf owns the real active-surface reference-intake story:

- one canonical attach story
- one explicit compatibility or rejection policy for batch-like drift
- one aligned docs, unit, and E2E story for staged reference behavior

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
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
- E2E surface regressions prove that attach/list/remove/clear and staged-goal
  behavior remain consistent on the active guided surface

## Leaf Work Items

- define the compatibility/rejection policy for batch-like attach attempts
- implement actionable attach-shape guidance in the reference image surface
  where the runtime can detect the drift
- align prompt/docs examples to repeat one `attach` call per reference image
- add focused unit plus E2E regression coverage for canonical attach, staged
  pending-reference flow, and repeated wrong-shape attempts

## Docs To Update

- `_docs/_PROMPTS/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`

## Changelog Impact

- include in the parent follow-on changelog entry when shipped

## Status / Board Update

- keep board tracking on `TASK-141`
- update the parent task summary so it explicitly calls out the final
  `reference_images(...)` attach policy and active-surface parity result when
  this leaf closes
