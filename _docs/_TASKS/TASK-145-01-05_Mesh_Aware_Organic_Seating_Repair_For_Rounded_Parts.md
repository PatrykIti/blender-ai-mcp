# TASK-145-01-05: Mesh-Aware Organic Seating Repair For Rounded Parts

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ✅ Done
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

## Closed Slice Acceptance Criteria

- repair planner distinguishes bbox-contact from mesh-surface contact for
  rounded organic parts
- for `head_body`, `tail_body`, and `limb_body` seams with rounded primitives,
  the planner distinguishes safe small contact/gap nudges from
  embedded/intersecting mesh-surface seating:
  - `macro_align_part_with_contact` remains valid for bounded side/gap repairs
    when the pair already has a stable side relation
  - embedded or intersecting rounded seams prefer the mesh-aware
    `macro_attach_part_to_surface` path instead of a blind bbox side-push
- the fix lands as an improved existing `macro_attach_part_to_surface` path,
  not as a second repair flow
- the improved `macro_attach_part_to_surface`
  can produce `seated_contact` for rounded parts without forcing LLMs into
  manual transform nudges

## Remaining Umbrella Closure Work

- `macro_align_part_with_contact` must still block or warn when it can only make
  bbox contact while mesh-surface truth remains separated.
- Dependent attached parts must not be silently left behind when a major anchor
  object is moved.
- Blender-backed head/body, tail/body, and assembled-creature E2E proof remains
  tracked under
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
  and must pass before the TASK-145 umbrella closes.

## Tests To Add/Update

- Unit:
  - icosphere-like rounded pair where bbox contact leaves mesh gap
  - overlap -> contact repair should not oscillate into mesh gap
  - macro candidate selection prefers mesh-aware seating for intersecting or
    embedded organic rounded seams while preserving contact-nudge behavior for
    safe side/gap repairs
- E2E:
  - Blender-backed head/body rounded seam repair
  - Blender-backed tail/body rounded seam repair
  - assembled creature checkpoint after repair reports `seated_contact`

## Validation Category

- Unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/tools/macro/test_macro_align_part_with_contact.py tests/unit/adapters/mcp/test_reference_images.py -q`
- E2E lane before TASK-145 umbrella closure:
  `poetry run pytest tests/e2e/tools/macro/test_macro_attach_part_to_surface.py tests/e2e/tools/macro/test_macro_align_part_with_contact.py tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py -q`
- Docs/preflight:
  `git diff --check`

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md` if promoted board state changes

## Changelog Impact

- include in the TASK-145 changelog entry when this ships

## Status / Closeout Note

- this closed leaf covers the implemented mesh-aware seating policy and
  `macro_attach_part_to_surface` improvement only; the remaining
  `macro_align_part_with_contact` warning/blocking lane and dependent-part guard
  stay open under TASK-145-03-03
- `test_macro_align_part_with_contact.py` was listed in the broader unit lane,
  but the implementation closeout did not record that gate. Its remaining
  warning/blocking coverage is carried forward by TASK-145-03-03 before the
  umbrella can close.
- Blender-backed rounded-part E2E remains required before TASK-145 closure and
  is tracked under
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)

## Completion Summary

- implemented this slice as a planner-selection policy change: intersecting
  organic segment seams now prefer `macro_attach_part_to_surface`
- improved `macro_attach_part_to_surface` with a bounded nearest-point
  mesh-surface nudge after bbox seating, so rounded parts can close small
  mesh gaps without manual transform nudges
- corrected generated surface-side hints so negative-side rounded attachments
  are not sent to the positive side by default
- no new macro was added; the behavior landed as an improved existing
  `macro_attach_part_to_surface`
- validation: `PYTHONPATH=. poetry run pytest tests/unit/tools/macro/test_macro_attach_part_to_surface.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `test_macro_align_part_with_contact.py` was not recorded in this closed-slice
  validation; the remaining align warning/blocking and dependent-part guard
  coverage stays required under TASK-145-03-03
- acceptance closeout: the implemented slice resolves the intersecting /
  embedded rounded-seam mesh-aware seating criteria through
  `macro_attach_part_to_surface`. Broad head/body, tail/body, limb/body E2E
  proof plus the `macro_align_part_with_contact` warning/blocking and
  dependent-part guard remain open umbrella closure work tracked under
  TASK-145-03-03, not a new second flow.
- docs updated: `_docs/_MCP_SERVER/README.md`,
  `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, and
  `_docs/_VISION/README.md`
- changelog recorded:
  `_docs/_CHANGELOG/238-2026-04-14-compact-iterate-and-organic-seating-planner.md`
- board/parent state: leaf closed under the still-open TASK-145 umbrella; no
  `_docs/_TASKS/README.md` board-count change was needed
- pre-commit status for the historical implementation closeout was not recorded
  and should not be reconstructed retroactively; this docs-only closeout repair
  intentionally records only the current docs validation path with
  `git diff --check`
- Blender-backed E2E was not run in this leaf closeout; the rounded head/body,
  tail/body, and assembled-creature E2E proof is deferred to TASK-145-03-03
  before the umbrella can close
