# TASK-145-01-05: Mesh-Aware Organic Seating Repair For Rounded Parts

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Stop relying on bbox-contact repair for rounded organic parts such as
icosphere-based heads, tails, and limbs when the truth layer reports mesh-surface
gap or overlap.

Recent runs show a repeated failure mode:

- `macro_align_part_with_contact(... normal_axis="Z")` can move a rounded part
  until bboxes touch
- mesh-surface truth still reports a real gap, e.g. ~0.05 BU
- the LLM then oscillates between overlap, bbox contact, and mesh gap repairs
- explicit-axis side pushes can also move only one object and leave dependent
  attached parts behind

## Repository Touchpoints

- `server/application/tool_handlers/macro_handler.py`
- `server/application/services/spatial_graph.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/scene.py`
- `tests/unit/tools/macro/test_macro_align_part_with_contact.py`
- `tests/unit/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`
- `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`
- `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`

## Acceptance Criteria

- repair planner distinguishes bbox-contact from mesh-surface contact for
  rounded organic parts
- for `head_body`, `tail_body`, and `limb_body` seams with rounded primitives,
  the preferred repair family is mesh-aware seating/attachment, not a blind
  bbox side-push
- `macro_align_part_with_contact` blocks or warns when it can only make bbox
  contact while mesh-surface truth remains separated
- a dedicated mesh-aware seating path or improved `macro_attach_part_to_surface`
  can produce `seated_contact` for rounded parts without forcing LLMs into
  manual transform nudges
- dependent attached parts are not silently left behind when a major anchor
  object is moved

## Tests To Add/Update

- Unit:
  - icosphere-like rounded pair where bbox contact leaves mesh gap
  - overlap -> contact repair should not oscillate into mesh gap
  - macro candidate selection prefers mesh-aware seating for organic rounded
    seams
- E2E:
  - Blender-backed head/body rounded seam repair
  - Blender-backed tail/body rounded seam repair
  - assembled creature checkpoint after repair reports `seated_contact`

## Changelog Impact

- include in the TASK-145 changelog entry when this ships
