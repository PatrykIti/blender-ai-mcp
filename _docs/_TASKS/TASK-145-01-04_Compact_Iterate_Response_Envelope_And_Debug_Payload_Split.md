# TASK-145-01-04: Compact Iterate Response Envelope And Debug Payload Split

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Reduce normal `reference_iterate_stage_checkpoint(...)` payload size so LLM
clients do not need to use ad hoc Python/grep/file parsing just to extract
`loop_disposition`, `current_step`, `correction_focus`, or top repair actions.

Recent guided squirrel runs still returned 10k-16k token checkpoint payloads
even in `preset_profile="compact"`. Compact mode currently removes full capture
records, but still returns large nested `truth_bundle`, `compare_result`,
full candidate evidence, silhouette metrics, and duplicated state.

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Closed Slice Acceptance Criteria

- normal guided compact iterate response exposes a small model-facing envelope:
  - `loop_disposition`
  - `current_step`
  - `step_status`
  - `next_actions`
  - assembled target summary
  - top correction focus
  - top truth findings
  - top macro candidates
  - compact vision summary
  - compact budget/capability diagnostics
- heavy debug fields move behind explicit rich/debug delivery:
  - full `truth_bundle.checks[*].gap/alignment/overlap/contact_assertion`
  - full `compare_result`
  - full candidate evidence
  - full silhouette metrics
- compact mode avoids duplicating the same large structures at top level and
  inside `compare_result`
- this leaf does not add a new debug retrieval tool; full debug/detail delivery
  remains an explicit umbrella follow-up tracked by
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
- response size is protected by unit tests that assert the compact response
  shape and bounded field presence

## Tests To Add/Update

- Unit:
  - compact iterate response omits full debug fields by default
  - compact response advertises that heavy debug fields were omitted
  - compact response still carries enough top findings for LLM execution
  - budget/capability diagnostics show final request cap, not only assistant
    policy budget
  - rich/debug detail remains covered by the open TASK-145-03-03 regression lane
- E2E:
  - guided stage iterate returns compact payload suitable for direct LLM reading

## Validation Category

- Unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- E2E lane before TASK-145 umbrella closure:
  `poetry run pytest tests/e2e/vision/test_reference_stage_truth_handoff.py tests/e2e/vision/test_reference_guided_creature_comparison.py -q`
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

- this closed leaf covers the compact default response split only; a dedicated
  debug retrieval tool was not added here and is not required for this leaf's
  `✅ Done` status
- E2E validation for direct LLM-readability is deferred to
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
  before TASK-145 can close

## Completion Summary

- compact iterate responses now set `debug_payload_omitted=true` and slim the
  nested `compare_result` by omitting duplicated heavy debug fields
- top-level iterate fields still carry actionable truth/candidate/route/handoff
  summaries for LLM execution
- no dedicated debug retrieval tool was added in this slice; full rich/debug
  retrieval remains open umbrella work tracked by TASK-145-03-03
- validation: `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- docs updated: `_docs/_MCP_SERVER/README.md`,
  `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`, and
  `_docs/_VISION/README.md`
- changelog recorded:
  `_docs/_CHANGELOG/238-2026-04-14-compact-iterate-and-organic-seating-planner.md`
- board/parent state: leaf closed under the still-open TASK-145 umbrella; no
  `_docs/_TASKS/README.md` board-count change was needed
- pre-commit status for the implementation closeout was not recorded in the
  original leaf closeout; current docs repair is covered by `git diff --check`
- E2E not run in this leaf closeout; the required end-to-end compact-stage
  regression is tracked under TASK-145-03-03
