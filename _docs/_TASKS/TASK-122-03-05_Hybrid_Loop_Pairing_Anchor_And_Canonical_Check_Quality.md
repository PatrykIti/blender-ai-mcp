# TASK-122-03-05: Hybrid Loop Pairing Anchor and Canonical Check Quality

**Follow-on After:** [TASK-122-03](./TASK-122-03_Hybrid_Vision_Truth_Correction_Loop.md)  
**Board Tracking:** Standalone hybrid-loop follow-on kept open after
`TASK-122-03` and `TASK-122` were closed. `_docs/_TASKS/README.md` tracks it
as its own open item while the historical numbering is preserved for
continuity.  
**Status:** ⏳ To Do  
**Priority:** 🟡 Medium

## Objective

Improve hybrid-loop output quality for assembled-creature stages by:

- choosing a more natural pairing anchor / `primary_target` for object-set and
  collection truth analysis
- ensuring vision-side recommended checks and follow-up tool names stay on
  canonical MCP tool ids instead of drifting into pseudo-tool labels

## Business Problem

Recent real hybrid-loop outputs exposed two quality problems:

- collection/object-set pairing can anchor on an incidental part such as
  `EarLeft`, which produces awkward pair labels like `EarLeft -> Head` instead
  of a more natural structural anchor
- vision-side follow-up suggestions can still drift into non-canonical names
  such as `check_alignment` or `compare_ortho_views`, even when the product
  should speak in canonical MCP tool ids

These issues do not break the loop contract, but they weaken trust in the
result and make downstream automation or operator interpretation less clean.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/adapters/mcp/vision/prompting.py`
- `server/adapters/mcp/vision/parsing.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Acceptance Criteria

- assembled creature object sets and collections no longer default to an
  incidental accessory part as the primary truth/pairing anchor when a more
  structural anchor is available
- hybrid-loop follow-up suggestions use canonical MCP tool ids or remain empty;
  they do not emit made-up tool labels
- prompt/parsing guidance and regression coverage are explicit enough to keep
  this quality bar stable

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_TASKS/README.md`

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_parsing.py`
- `tests/unit/adapters/mcp/test_vision_prompting.py`
- `tests/unit/adapters/mcp/test_vision_external_backend.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py` when Blender-backed
  hybrid outputs are affected

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when this follow-on changes hybrid-loop
  pairing behavior, tool-id guarantees, or product-facing guidance

## Status / Board Update

- keep this task open as a standalone follow-on after the closed `TASK-122-03`
  subtree
- if it is completed, update `_docs/_TASKS/README.md` and refresh the closed
  parent follow-on note
