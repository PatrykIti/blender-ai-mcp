# TASK-155-01-01: `misaligned_attachment` Relation Verdict Contract

**Parent:** [TASK-155-01](./TASK-155-01_Attachment_Verdict_Contract_And_Truth_Semantics.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Remove the hard validation blocker where `spatial_graph.py` and
`reference.py` emit `misaligned_attachment`, but `SceneRelationVerdictLiteral`
does not accept it in relation/checkpoint contracts.

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/tools/scene/test_scene_contracts.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- `SceneRelationGraphPayloadContract` accepts relation pairs with
  `relation_verdicts=["misaligned_attachment"]`
- `SceneCorrectionTruthPairContract` and truth-followup/candidate evidence also
  accept the same verdict
- relation/checkpoint tools no longer fail Pydantic validation when a real
  required creature seam emits this verdict
- docs continue to list `misaligned_attachment` as a first-class attachment
  verdict

## Tests To Add/Update

- Unit:
  - add contract coverage in `tests/unit/tools/scene/test_scene_contracts.py`
  - add stage truth/checkpoint coverage in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - keep structured-delivery coverage in
    `tests/unit/adapters/mcp/test_structured_contract_delivery.py` green
- E2E:
  - extend `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
    with a misaligned required seam that validates successfully

## Changelog Impact

- include in the TASK-155 changelog entry
