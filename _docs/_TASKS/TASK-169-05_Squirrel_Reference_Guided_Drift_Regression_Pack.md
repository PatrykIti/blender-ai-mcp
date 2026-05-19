# TASK-169-05: Squirrel Reference-Guided Drift Regression Pack

**Parent:** [TASK-169](./TASK-169_Reference_Guided_Quality_Drift_Regression_And_Runtime_Authority.md)
**Status:** ✅ Done
**Completed:** 2026-05-19
**Priority:** 🔴 High
**Objective:** Turn the recent low-poly squirrel failure into one explicit regression family spanning transcript-state, packet-priority, and Blender-backed proof lanes.
**Repository Touchpoints:** `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_quality_gate_verifier.py`, `tests/unit/adapters/mcp/test_search_surface.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/router/test_guided_manual_handoff.py`, `tests/e2e/vision/`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/application/tool_handlers/router_handler.py`, `_docs/_TEST_IMAGES/squirrel-front.png`
**Acceptance Criteria:**
- the observed squirrel drift is encoded as executable regression cases rather than operator memory
- the family covers both state/contract drift and Blender-backed visual-quality drift
- the regression pack stays grounded on the current guided/reference owners rather than a fake mock-only workflow

## Execution Structure

| Order | Task | Purpose |
|------|------|---------|
| 1 | [TASK-169-05-01](./TASK-169-05-01_Transcript_State_And_Packet_Priority_Regression_Cases.md) | Encode the transcript-derived state and packet-priority failures as unit/integration regressions |
| 2 | [TASK-169-05-02](./TASK-169-05-02_Blender_Backed_Squirrel_Proof_Lane.md) | Add one Blender-backed two-reference squirrel proof lane that fails on the bad blockout class |

## Implementation Notes

- keep squirrel as the motivating anchor but reuse the current generic creature
  and guided/reference seams
- prefer typed session/packet assertions first, then a Blender-backed visual
  proof lane for the whole result

## Runtime / Security Contract Notes

- regression coverage must stay on existing public/runtime seams instead of
  inventing squirrel-only hidden tools or alternate guided paths
- repo-owned squirrel fixtures should be preferred over ad hoc temp-path
  operator inputs whenever a deterministic regression can be pinned locally

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_quality_gate_verifier.py`
- `tests/unit/adapters/mcp/test_search_surface.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/router/test_guided_manual_handoff.py`
- one new Blender-backed squirrel proof lane under `tests/e2e/vision/`

## Docs To Update

- `_docs/_TESTS/README.md`
- `_docs/_VISION/README.md` if the new proof lane changes operator guidance

## Changelog Impact

- add/update the historical `_docs/_CHANGELOG/*` entry when this slice lands

## Completion Summary

- the squirrel regression now has both typed state/contract coverage and one
  deterministic Blender-backed proof lane on the current guided/reference path
- the repo-owned proof lane distinguishes early broad silhouette authority
  from the old vertical primitive-stack failure class with deterministic scene
  assertions

## Status / Board Update

- closed with parent `TASK-169`

## Validation Commands

- `git diff --check`
- proof lanes are owned by the child tasks below

## Validation Category

- regression-pack planning only at this level
