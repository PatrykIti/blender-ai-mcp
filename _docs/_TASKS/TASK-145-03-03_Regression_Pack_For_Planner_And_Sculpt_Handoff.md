# TASK-145-03-03: Regression Pack For Planner and Sculpt Handoff

**Parent:** [TASK-145-03](./TASK-145-03_Guided_Adoption_Visibility_Docs_And_Regression_Pack.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Depends On:** [TASK-145-03-01](./TASK-145-03-01_Planner_And_Sculpt_Delivery_On_LLM_Guided.md), [TASK-145-03-02](./TASK-145-03-02_Planner_First_Prompting_And_Documentation.md)
**Carries Forward:**
- [TASK-145-01-04](./TASK-145-01-04_Compact_Iterate_Response_Envelope_And_Debug_Payload_Split.md)
- [TASK-145-01-05](./TASK-145-01-05_Mesh_Aware_Organic_Seating_Repair_For_Rounded_Parts.md)

## Objective

Build a focused regression pack that locks down:

- planner contract shape
- family-selection boundaries
- sculpt precondition gating
- guided surface / discovery behavior
- planner-first docs and prompt ordering

## Implementation Notes

Regression coverage should be scenario-driven, not only file-list driven.
At minimum, cover:

- relation blocker: unresolved attachment/support/contact/overlap keeps the
  next family on `macro` or `inspect_only`, not `sculpt_region`
- view blocker: missing/poor framing blocks or downgrades sculpt handoff
- local-form positive case: organic local-form signal selects the bounded
  sculpt subset only after structural blockers clear
- compact payload: planner summary is present without full heavy debug graphs
  in compact mode
- contract parity: extend `test_contract_payload_parity.py` to cover the
  reference-stage compare / iterate contracts used by the planner path; do not
  assume the existing parity file already owns those reference contracts
- rich/detail path: richer planner detail is opt-in and uses the same policy
  result as the compact response
- visibility/search: no broad planner/sculpt family is bootstrap-visible on
  `llm-guided`
- guided sculpt execution gate: any handoff-visible sculpt mutator maps to an
  allowed guided family or fails closed before execution
- native visibility refresh: tool visibility does not stay stale after guided
  planner/handoff state changes
- rounded-part macro regression: head/body and tail/body rounded seams still
  prove `seated_contact`, and assembled-creature checkpoints do not regress
  after the mesh-aware seating fix from `TASK-145-01-05`
- macro/dependent-part guard: `macro_align_part_with_contact` still blocks or
  warns on unsafe bbox-only side pushes that can detach dependent parts
- docs/prompts: planner-first read order appears before raw vision prose or
  low-level edit suggestions

## Repository Touchpoints

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`
- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`

## Acceptance Criteria

- unit tests cover the compact planner contract, disclosure rules, and sculpt
  gating policy
- `test_contract_payload_parity.py` includes explicit parity coverage for
  `ReferenceCompareStageCheckpointResponseContract` and
  `ReferenceIterateStageCheckpointResponseContract`
- guided execution tests cover the bounded sculpt subset mapping or fail-closed
  behavior for unmapped `sculpt_*` mutators
- search/visibility regressions guard against planner/sculpt overexposure on
  `llm-guided`
- guided-state tests cover visibility refresh when planner/handoff state
  changes the bounded visible surface
- e2e coverage exercises both truth-driven assembly cases and organic/local
  sculpt-hand-off cases
- E2E coverage also carries the deferred `TASK-145-01-05` rounded-part proof:
  head/body seam, tail/body seam, assembled-creature `seated_contact`, and the
  unsafe dependent-part side-push guard
- docs/eval assets stay synchronized with the shipped contract and policy

## Docs To Update

- `_docs/_VISION/CROSS_DOMAIN_REFINEMENT_ROUTING_EVAL.md`
- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_visibility_policy.py`
- `tests/unit/adapters/mcp/test_guided_mode.py`
- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_guided_surface_benchmarks.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/unit/adapters/mcp/test_prompt_catalog.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_streamable_spatial_support.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/sculpt/test_sculpt_tools.py`

## Validation Category

- Unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_visibility_policy.py tests/unit/adapters/mcp/test_guided_mode.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_guided_surface_benchmarks.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_prompt_catalog.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- E2E lane:
  `poetry run pytest tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_guided_creature_comparison.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py tests/e2e/tools/macro/test_macro_attach_part_to_surface.py tests/e2e/tools/macro/test_macro_align_part_with_contact.py tests/e2e/tools/sculpt/test_sculpt_tools.py -q`
- Docs/preflight:
  `git diff --check`
- Router metadata schema lane when metadata changes:
  `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run check-router-tool-metadata --all-files`

## Changelog Impact

- include in the parent TASK-145 changelog entry when shipped

## Status / Board Update

- no board-count change is needed while TASK-145 remains the promoted open
  board item
