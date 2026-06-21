# TASK-184-06: Per-Axis Advisory Reliability Scorecard

**Parent:** [TASK-184](./TASK-184_Vision_3D_Understanding_Audit_Corrections.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Objective:** Add a default-off evaluation scorecard that measures VLM/render agreement by specific 3D-understanding axes instead of one blended confidence score.

**Repository Touchpoints:** `scripts/vision_harness.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/vision/silhouette.py`, `tests/fixtures/vision_eval/`, `tests/unit/scripts/`, `tests/unit/adapters/mcp/`

## Implementation Notes

- Score at least these advisory axes:
  - object identity / mark correspondence
  - directional spatial relation
  - depth ordering
  - support/contact relation
  - shape/profile consistency
- Use deterministic inspection, object-ID, projection diagnostics, and
  silhouette evidence as the comparison substrate.
- Keep the scorecard harness/eval-facing by default; do not emit it in normal
  client payloads unless explicitly requested.

## Runtime / Security Contract Notes

- scorecard values are evaluation telemetry, not gate authority
- VLM self-confidence must not replace deterministic agreement checks
- external-provider live runs remain behind explicit env flags and provider-key
  setup

## Tests To Add/Update

- fixture-level tests for scorecard aggregation and per-axis missing-data
  handling
- negative cases for VLM claims contradicted by deterministic evidence
- script tooling tests for any new harness flags

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_TESTS/README.md`
- `_docs/_VISION/HYBRID_LOOP_REAL_CREATURE_EVAL.md` if the scorecard becomes
  part of that eval lane

## Acceptance Criteria

- scorecard output separates at least object identity, spatial direction, depth,
  contact/support, and shape/profile axes
- missing deterministic evidence yields explicit unavailable/skipped status
- normal guided/runtime payloads do not grow unless the scorecard is explicitly
  enabled

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts tests/unit/adapters/mcp -q`
