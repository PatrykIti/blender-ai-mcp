# TASK-155-01-02: Seam-Aware Attachment Alignment Semantics

**Parent:** [TASK-155-01](./TASK-155-01_Attachment_Verdict_Contract_And_Truth_Semantics.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Prevent valid seated organic seams, especially `Head -> Body`, from being
classified as `misaligned_attachment` only because bbox centers are not aligned
on the support/contact axis.

## Repository Touchpoints

- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`
- `blender_addon/application/handlers/scene.py`
- `tests/unit/tools/test_handler_rpc_alignment.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Acceptance Criteria

- attachment verdict logic distinguishes tangential alignment from the contact
  normal/support axis for seated seams
- `Head -> Body` with true contact and expected vertical offset does not become
  `misaligned_attachment` solely from center-Z delta
- embedded seams such as `Snout -> Head` can still require appropriate
  placement/alignment checks
- actual lateral or tangential drift remains actionable and visible in
  truth-followup/correction candidates

## Tests To Add/Update

- Unit:
  - add `Head -> Body` seated-contact fixture in
    `tests/unit/tools/test_handler_rpc_alignment.py`
  - add required-seam truth bundle cases in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - add direct contract expectation in
    `tests/unit/tools/scene/test_scene_contracts.py`
- E2E:
  - extend `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
    for support-axis offset that remains `seated_contact`
  - extend `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
    so the assembled creature path does not escalate valid head/body seating

## Changelog Impact

- include in the TASK-155 changelog entry

## Completion Summary

- changed attachment verdict handling so a passing contact assertion wins over
  generic bbox-center alignment drift for seated organic seams
