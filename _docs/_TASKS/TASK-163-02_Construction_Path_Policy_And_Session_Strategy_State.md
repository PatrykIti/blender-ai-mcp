# TASK-163-02: Construction Path Policy And Session Strategy State

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-163](./TASK-163_Vision_Orchestrator_Feedback_Strategy_Normalization_And_Optional_Perception_Adapters.md)
**Objective:** Normalize RU output into a session-owned `reference_strategy_state` without adding a new router strategy flow.
**Repository Touchpoints:** `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/session_capabilities_state.py`, `server/adapters/mcp/session_capabilities_bootstrap.py`, `server/adapters/mcp/areas/reference_understanding.py`
**Acceptance Criteria:** strategy state survives session persistence; canonical planner families remain `macro`, `modeling_mesh`, `sculpt_region`, `inspect_only`; blocked RU states keep deterministic fallback guidance.

## Completion Summary

- added typed `ReferenceStrategyStateContract`
- persisted `reference_strategy_state` in session capability state
- preserved same-goal carry-forward and clear/reset semantics in bootstrap
  helpers
- kept strategy normalization server-owned and internal

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
- `tests/unit/adapters/mcp/test_reference_images.py`

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`

## Changelog Impact

- covered by [318. TASK-163 reference orchestrator feedback core](../_CHANGELOG/318-2026-05-05-task-163-reference-orchestrator-feedback-core.md)

## Status / Board Update

- closed historically under `TASK-163`; future related work should use an
  explicit follow-on task
- does not become its own board row

## Validation Commands

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_reference_images.py -q`
