# TASK-122-02-02-01-03: Truth-Followup Candidate Exposure Without Auto-Apply

**Parent:** [TASK-122-02-02-01](./TASK-122-02-02-01_Repair_Macro_Contract_Inference_And_Candidate_Exposure.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `truth_followup` now exposes `macro_candidates`, and clear gap/contact/alignment pairs can recommend `macro_align_part_with_contact` as a bounded repair option. The loop still does not auto-apply the macro by default.

## Objective

Expose `macro_align_part_with_contact` as a recommended candidate from
truth-followup / loop guidance without turning on automatic execution.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/scene.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`

## Acceptance Criteria

- the current correction flow can recommend the repair macro when the pair state is clear
- no automatic execution path is introduced at this stage

## Docs To Update

- `_docs/_ROUTER/README.md`
- `_docs/_MCP_SERVER/README.md`

## Tests To Add/Update

- `tests/unit/` for candidate exposure and non-auto behavior

## Changelog Impact

- include this scope in the eventual repair-macro changelog entry when it ships

## Status / Board Update

- this leaf is closed
