# TASK-122-02-02-01: Repair Macro Contract, Inference, and Candidate Exposure

**Parent:** [TASK-122-02-02](./TASK-122-02-02_macro_align_part_with_contact.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The MVP contract, inference path, and candidate exposure for `macro_align_part_with_contact` are now in place. The repair macro has a distinct pair-repair input model, bounded nudge behavior, and candidate exposure from `truth_followup` without any auto-apply path.

## Objective

Implement the technical MVP for `macro_align_part_with_contact` as a
truth-driven repair macro instead of another generic placement tool.

## Technical Direction

The MVP should:

- accept one explicit pair: `part_object` + `reference_object`
- accept one repair target:
  - `target_relation = "contact"` or
  - `target_relation = "gap"` with explicit `gap`
- infer `normal_axis` automatically when possible, while still allowing an
  explicit override when the caller knows it
- preserve the current contact side by default when the inferred side is clear
- compute one bounded minimal nudge instead of a full bbox re-layout
- return before/after truth summary and deterministic verification hints
- expose the macro as a recommended candidate from truth-followup / loop
  guidance, but not auto-execute it in the loop

## Repository Touchpoints

- `server/domain/tools/`
- `server/application/tool_handlers/`
- `server/adapters/mcp/areas/`
- `server/adapters/mcp/contracts/`
- `server/adapters/mcp/dispatcher.py`
- `server/router/infrastructure/tools_metadata/`
- `tests/unit/`
- `tests/e2e/`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

## Acceptance Criteria

- the technical MVP has one clear contract that distinguishes repair from fresh placement
- the macro can infer enough pair state from truth tools to compute a bounded minimal nudge
- the macro can be recommended by the current truth-followup / later loop policy without needing auto-apply

## Docs To Update

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ROUTER/README.md` when recommendation / loop-policy wording changes

## Tests To Add/Update

- `tests/unit/` for contract, handler, MCP wrapper, and recommendation-path coverage
- `tests/e2e/` when real Blender geometry validates the repair behavior

## Changelog Impact

- add a `_docs/_CHANGELOG/*.md` entry when the repair macro MVP ships

## Status / Board Update

- this subtask is closed; its leaves now describe the completed MVP slices

## Leaf Breakdown

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-122-02-02-01-01](./TASK-122-02-02-01-01_Truth_Driven_Pair_Input_And_Side_Preservation.md) | Define the repair input model and side-preservation rules from current truth state |
| 2 | [TASK-122-02-02-01-02](./TASK-122-02-02-01-02_Minimal_Nudge_And_Before_After_Truth_Summary.md) | Implement bounded minimal-nudge behavior plus before/after truth summary output |
| 3 | [TASK-122-02-02-01-03](./TASK-122-02-02-01-03_Truth_Followup_Candidate_Exposure_Without_Auto_Apply.md) | Expose the macro as a candidate from truth-followup / loop guidance without turning on automatic execution |
