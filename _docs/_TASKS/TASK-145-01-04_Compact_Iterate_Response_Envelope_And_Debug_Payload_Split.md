# TASK-145-01-04: Compact Iterate Response Envelope And Debug Payload Split

**Parent:** [TASK-145-01](./TASK-145-01_Repair_Planner_Payload_And_Family_Selection_Policy.md)
**Status:** ⏳ To Do
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

## Acceptance Criteria

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
- a debug/full payload path remains available through `preset_profile="rich"`,
  a debug flag, or a dedicated follow-up debug tool
- response size is protected by unit tests that assert the compact response
  shape and bounded field presence

## Tests To Add/Update

- Unit:
  - compact iterate response omits full debug fields by default
  - rich/debug response keeps full data available
  - compact response still carries enough top findings for LLM execution
  - budget/capability diagnostics show final request cap, not only assistant
    policy budget
- E2E:
  - guided stage iterate returns compact payload suitable for direct LLM reading

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/_VISION/README.md`
- `_docs/_PROMPTS/REFERENCE_GUIDED_CREATURE_BUILD.md`
- `_docs/_TASKS/README.md` if promoted board state changes

## Changelog Impact

- include in the TASK-145 changelog entry when this ships

## Status / Closeout Note

- when this leaf closes, record the compact-vs-debug response contract, exact
  validation commands, and whether a dedicated debug retrieval tool was added
