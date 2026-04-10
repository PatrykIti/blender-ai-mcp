# TASK-152-01-04: Seam Verdict Interpretation For Guided Creature Blockout

**Parent:** [TASK-152-01](./TASK-152-01_Spatial_Tool_Prompting_And_Seam_Interpretation_Guidance.md)
**Depends On:** [TASK-152-01-03](./TASK-152-01-03_Heuristic_Friendly_Object_Naming_Guidance_And_Gates.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Make the creature-blockout guidance explicit about which seam verdicts are
acceptable for embedded organic parts and which still require correction.

## Repository Touchpoints

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Planned Guidance Shape

- explicitly state:
  - `intersecting` may be acceptable for embedded ear/head or snout/head
    blockout seams
  - `floating_gap` is still actionable for `segment_attachment` seams such as:
    - `head_body`
    - `tail_body`
    - `limb_body`
- add one operator-facing example contrasting:
  - acceptable embedded blockout seam
  - unacceptable hanging/floating segment seam

## Acceptance Criteria

- the prompt/docs contract no longer lets the model rationalize visible
  hanging/floating primary appendages as “expected” blockout state

## Docs To Update

- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-152 changelog entry
