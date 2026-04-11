# TASK-155-03: Guided Tool UX And Response Budget

**Parent:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Reduce avoidable model drift from raw schema noise and oversized checkpoint
responses on the shaped guided surface.

## Repository Touchpoints

- `server/adapters/mcp/areas/scene.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/discovery/search_surface.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- common macro/assert argument mistakes are normalized where safe or returned
  with actionable guided errors
- checkpoint responses have a compact LLM-oriented mode with bounded candidates
  and next actions
- seam checks discourage overly broad tolerances that mask small-part gaps
- docs and tests describe the exact compact/guided behavior

## Tests To Add/Update

- Unit:
  - `tests/unit/tools/scene/test_macro_attach_part_to_surface_mcp.py`
  - `tests/unit/tools/scene/test_scene_mcp_tools_batch.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`
  - `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
  - `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
  - `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
  - `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`

## Changelog Impact

- include in the TASK-155 changelog entry when this subtask ships

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-155-03-01](./TASK-155-03-01_Macro_And_Assert_Argument_Canonicalization.md) | Normalize common guided macro/assert parameter slips or produce actionable errors |
| 2 | [TASK-155-03-02](./TASK-155-03-02_Compact_Checkpoint_Response_Mode.md) | Add a compact checkpoint payload path for long guided sessions |
| 3 | [TASK-155-03-03](./TASK-155-03-03_Seam_Assertion_Tolerance_And_Semantic_Check_Guidance.md) | Keep seam validation from passing with overly broad tolerances |

## Completion Summary

- added guided call argument canonicalization for common macro/assert mistakes,
  compact checkpoint capture trimming, and seam guidance updates
