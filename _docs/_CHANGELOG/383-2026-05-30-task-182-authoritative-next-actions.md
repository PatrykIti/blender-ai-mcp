# 383. TASK-182-02 authoritative_next_actions channel consolidation

Date: 2026-05-30

## Summary

Implemented the channel-consolidation half of `TASK-182-02`: the compact
orchestrator feedback now exposes a single `authoritative_next_actions` list that
merges the 4-6 overlapping advisory channels (`next_actions`, `correction_focus`,
`recommended_support_tools`, `recommended_repair`) into one deterministic-first,
ranked, deduplicated to-do list. The orchestrator reads one ordered list instead
of reconciling several channels with non-obvious precedence.

## Changes

- `server/adapters/mcp/contracts/reference.py`: added
  `authoritative_next_actions: list[str]` to
  `ReferenceOrchestratorFeedbackContract` (read-first consolidated channel; the
  detailed channels remain).
- `server/adapters/mcp/areas/reference_feedback.py`: added
  `_consolidate_authoritative_next_actions(...)` (deterministic `next_actions`
  first, then correction targets, then a bounded repair suggestion, then support
  tools; case-insensitive dedup preserving first occurrence; capped) and wired it
  into `build_reference_orchestrator_feedback`.

## Tests

- `tests/unit/adapters/mcp/test_reference_orchestrator_feedback.py`: ranking +
  dedup + repair/support inclusion, and the bounded/empty cases
- `ruff`/`mypy` clean; full `tests/unit` green

## Follow-on

The deterministic-first **layered exit** half of `TASK-182-02` (hard non-VLM gate
first — registry part-count + required contacts via `scene_assert_contact` —
with the VLM verdict only as a tiebreaker, and the full Critic/Verify re-render
loop of `TASK-182`) remains open: it wires into
`transforms/quality_gate_verifier.py` and the staged-compare orchestration and
warrants its own E2E-validated pass.

## Research Basis

IR3D-Bench (arXiv:2506.23329) layered-metric ordering; SayPlan (arXiv:2307.06135)
single consolidated next-step. Re-measure on `tests/fixtures/vision_eval`.
