# TASK-155-04: Regression And Docs Closeout For Post-Run Reliability

**Parent:** [TASK-155](./TASK-155_Guided_Post_Run_Reliability_Followups.md)
**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Close TASK-155 by proving the runtime fixes with targeted unit and E2E coverage,
then align operator docs, prompt assets, task status, and changelog history.

## Repository Touchpoints

- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_PROMPTS/GUIDED_SESSION_START.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_PROMPTS/README.md`
- `_docs/_TASKS/README.md`
- `_docs/_CHANGELOG/README.md`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Acceptance Criteria

- every implemented TASK-155 behavior has at least one focused unit regression
- transport/E2E coverage proves the end-to-end guided surface behavior for the
  highest-risk flows
- docs and prompt assets describe the shipped runtime behavior, not a desired
  future behavior
- TASK-155 and all completed descendant task files are closed consistently
- a dedicated `_docs/_CHANGELOG/*` entry is added and indexed

## Tests To Add/Update

- Unit:
  - run the focused TASK-155 regression set from TASK-155-01 through TASK-155-03
  - run `tests/unit/adapters/mcp/test_public_surface_docs.py`
- E2E:
  - run the relevant guided integration set:
    `tests/e2e/integration/test_guided_surface_contract_parity.py`,
    `tests/e2e/integration/test_guided_streamable_spatial_support.py`, and
    `tests/e2e/integration/test_guided_inspect_validate_handoff.py`
  - run Blender-backed vision/macro coverage when the behavior changes real
    geometry:
    `tests/e2e/vision/test_reference_stage_assembled_creature_attachment_truth.py`,
    `tests/e2e/tools/macro/test_macro_attach_part_to_surface.py`, and
    `tests/e2e/tools/macro/test_macro_align_part_with_contact.py`

## Changelog Impact

- add and index a dedicated TASK-155 changelog entry during closeout

## Completion Summary

- updated MCP/prompt docs, task board, descendant task statuses, and the
  `_docs/_CHANGELOG/234-*` entry
- focused TASK-155 unit regression pack passed with `157 passed`
- docs/visibility parity passed with `37 passed`
- guided transport E2E passed with `4 passed, 2 skipped`
- Blender-backed vision/macro E2E was attempted and skipped locally because
  the Blender RPC-backed cases were not available in this environment
