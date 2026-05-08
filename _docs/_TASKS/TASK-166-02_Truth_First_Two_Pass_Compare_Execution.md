# TASK-166-02: Truth-First Two-Pass Compare Execution

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Split compare into deterministic preflight + narrow visual extraction first, then bounded correction ranking only when needed.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/areas/reference_planner.py`
- `server/adapters/mcp/areas/reference_feedback.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/runner.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Implementation Notes

- Pass 1:
  - deterministic truth preflight
  - narrow packet question
  - 3-5 visual mismatches max
- Pass 2:
  - correction ranking
  - support-tool hints
  - packet synthesis where needed

## Current Flow Integration

- `reference_compare_stage_checkpoint(...)` should become the owner of packet
  extraction and packet synthesis for the current stage.
- `reference_iterate_stage_checkpoint(...)` should consume packet results and
  only invoke ranking/synthesis when packet extraction produced actionable
  mismatches.
- Existing deterministic gates, `truth_followup`, and `planner_summary` stay in
  the same staged response family; the internal sequencing changes, not the
  public contract ownership.
- `reference_orchestrator_feedback` remains the compact consumer-facing read
  model built from the staged compare result, not a new direct projection from
  raw packet internals.

## Acceptance Criteria

- compare no longer mixes extraction and ranking in one always-large payload
- the LLM receives narrower packet questions instead of one whole-model prompt
- extraction and ranking outcomes are independently representable so skipped or
  failed ranking does not erase usable packet evidence
