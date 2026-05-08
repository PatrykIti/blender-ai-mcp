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
  extraction, conditional ranking, and packet synthesis for the current stage.
- `reference_iterate_stage_checkpoint(...)` should consume packet results and
  the already synthesized staged compare result when deciding loop disposition;
  it must not become a second ranking/synthesis owner flow.
- Existing deterministic gates, `truth_followup`, and `planner_summary` stay in
  the same staged response family; the internal sequencing changes, not the
  public contract ownership.
- `reference_orchestrator_feedback` remains the compact consumer-facing read
  model built from the staged compare result, not a new direct projection from
  raw packet internals.

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_runner.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when two-pass staged compare
  ships

## Status / Board Update

- keep parent `TASK-166` and this subtask aligned in `_docs/_TASKS/README.md`
- when this subtask closes, update child-leaf state and note whether transport
  proof shipped or remains explicit follow-on work

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`

## Acceptance Criteria

- compare no longer mixes extraction and ranking in one always-large payload
- the LLM receives narrower packet questions instead of one whole-model prompt
- extraction and ranking outcomes are independently representable so skipped or
  failed ranking does not erase usable packet evidence
- iterate consumes staged packet synthesis and loop guidance instead of owning a
  second ranking/synthesis pass
