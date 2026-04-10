# TASK-155-01: Attachment Verdict Contract And Truth Semantics

**Parent:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Fix the attachment-verdict failure path seen in the guided run: relation and
checkpoint payloads emit `misaligned_attachment`, but the public relation
verdict contract rejects it, and the current alignment interpretation can turn
valid seated seams into false correction loops.

## Repository Touchpoints

- `server/adapters/mcp/contracts/scene.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`

## Acceptance Criteria

- `scene_relation_graph(...)`, `reference_compare_stage_checkpoint(...)`, and
  `reference_iterate_stage_checkpoint(...)` accept every attachment verdict the
  service can emit
- `misaligned_attachment` remains explicit when it is genuinely needed, instead
  of being silently flattened into a generic verdict
- seated contact for support-style creature seams is not treated as failed only
  because center alignment differs along the support axis
- dependent seams disturbed by attachment repair are revalidated or clearly
  surfaced before the flow continues

## Tests To Add/Update

- Unit:
  - `tests/unit/tools/scene/test_scene_contracts.py`
  - `tests/unit/tools/test_handler_rpc_alignment.py`
  - `tests/unit/adapters/mcp/test_reference_images.py`
  - `tests/unit/adapters/mcp/test_structured_contract_delivery.py`
- E2E:
  - `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
  - `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
  - `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`

## Changelog Impact

- include in the TASK-155 changelog entry when this subtask ships

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-155-01-01](./TASK-155-01-01_Misaligned_Attachment_Relation_Verdict_Contract.md) | Make the relation verdict contract accept `misaligned_attachment` end to end |
| 2 | [TASK-155-01-02](./TASK-155-01-02_Seam_Aware_Attachment_Alignment_Semantics.md) | Avoid false `misaligned_attachment` on valid seated support seams |
| 3 | [TASK-155-01-03](./TASK-155-01-03_Dependent_Attachment_Seam_Revalidation.md) | Revalidate or preserve dependent attached parts after seating macros move an anchor/part |
