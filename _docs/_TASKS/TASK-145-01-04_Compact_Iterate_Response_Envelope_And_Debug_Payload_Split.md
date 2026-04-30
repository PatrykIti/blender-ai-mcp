# TASK-145-01-04: Compact Iterate Response Envelope And Debug Payload Split

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ✅ Done
**Priority:** 🔴 High

## Objective

Reduce normal `reference_iterate_stage_checkpoint(...)` payload size so LLM
clients do not need to use ad hoc Python/grep/file parsing just to extract
`loop_disposition`, `current_step`, `correction_focus`, or top repair actions.

Recent guided squirrel runs returned 10k-16k token checkpoint payloads even in
`preset_profile="compact"`. The closed slice reduces the duplicated nested
`compare_result` debug payload while intentionally preserving actionable
top-level truth/candidate/route/handoff summaries for LLM execution. A stricter
small-envelope contract remains umbrella closure work under
[TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md).

## Repository Touchpoints

- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/areas/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/vision/test_reference_stage_truth_handoff.py`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`

## Closed Slice Acceptance Criteria

- normal guided compact iterate response exposes a slimmer model-facing envelope
  while preserving top-level structured summaries:
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
- duplicated nested debug fields move out of the default nested `compare_result`:
  - full `truth_bundle.checks[*].gap/alignment/overlap/contact_assertion`
  - full `compare_result`
  - full candidate evidence
  - full silhouette metrics
- compact mode avoids duplicating the same large structures inside the nested
  `compare_result`; top-level structured summaries remain part of the current
  response contract
- this leaf does not add a new debug retrieval tool; full debug/detail delivery
  and stricter small-envelope parity remain explicit umbrella follow-up work
  tracked by
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
- response size is protected by unit tests that assert the compact response
  debug split and bounded field presence

## Tests To Add/Update

- Unit:
  - compact iterate response omits full nested compare debug fields by default
  - compact response advertises that heavy debug fields were omitted
  - compact response still carries enough top findings for LLM execution
  - budget/capability diagnostics show final request cap, not only assistant
    policy budget
  - contract payload parity for the compact response envelope is carried by the
    open TASK-145-03-03 regression lane before umbrella closure
  - rich/debug detail remains covered by the open TASK-145-03-03 regression lane
- E2E:
  - guided stage iterate returns compact payload suitable for direct LLM reading

## Validation Category

- Closed-slice unit lane:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- Contract parity lane before TASK-145 umbrella closure:
  `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
  carried by [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
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
- the closed scope does not claim that all top-level truth/candidate/route/handoff
  fields were removed from the iterate contract; those actionable summaries still
  ship today and stricter compact-envelope parity remains open under TASK-145-03-03
- E2E validation for direct LLM-readability is deferred to
  [TASK-145-03-03](./TASK-145-03-03_Regression_Pack_For_Planner_And_Sculpt_Handoff.md)
  before TASK-145 can close
- `test_contract_payload_parity.py` was listed as a contract owner for this
  response shape, but no parity validation was recorded in the implementation
  closeout. That parity gate is carried forward by TASK-145-03-03 before the
  umbrella can close.

## Completion Summary

- compact iterate responses now set `debug_payload_omitted=true` and slim the
  nested `compare_result` by omitting duplicated heavy debug fields
- top-level iterate fields still carry actionable truth/candidate/route/handoff
  summaries for LLM execution
- no dedicated debug retrieval tool was added in this slice; full rich/debug
  retrieval remains open umbrella work tracked by TASK-145-03-03
- validation: `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- contract parity validation was not recorded for this closed slice; the
  explicit `test_contract_payload_parity.py` gate remains required under
  TASK-145-03-03 before TASK-145 umbrella closure
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
- E2E not run in this leaf closeout; the required end-to-end compact-stage
  regression is tracked under TASK-145-03-03
