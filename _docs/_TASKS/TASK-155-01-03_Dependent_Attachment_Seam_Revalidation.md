# TASK-155-01-03: Dependent Attachment Seam Revalidation

**Parent:** [TASK-155-01](./TASK-155-01_Attachment_Verdict_Contract_And_Truth_Semantics.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Close the gap where repairing `Head -> Body` can move `Head` without also
moving or revalidating dependent parts such as `Snout`, leaving `Snout -> Head`
broken while the flow continues.

## Repository Touchpoints

- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `server/application/tool_handlers/macro_handler.py`
- `server/adapters/mcp/session_capabilities.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`

## Acceptance Criteria

- when a macro moves a part/anchor involved in existing required seams, the next
  guided truth step surfaces dependent seam revalidation needs
- `Head -> Body` repair cannot silently leave `Snout -> Head` stale/invalid in
  the same active workset
- follow-up payloads either recommend a dependent seam check or preserve an
  attached-subtree relation if that architecture is chosen
- behavior stays deterministic and does not rely on prose-only guidance

## Tests To Add/Update

- Unit:
  - add dependent seam fixtures in
    `tests/unit/adapters/mcp/test_reference_images.py`
  - add macro result/follow-up cases in
    `tests/unit/tools/macro/test_macro_attach_part_to_surface.py` and
    `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- E2E:
  - add or extend an assembled creature E2E in
    `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`
    covering `Head -> Body` repair followed by `Snout -> Head` validation

## Changelog Impact

- include in the TASK-155 changelog entry
