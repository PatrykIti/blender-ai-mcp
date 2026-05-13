# TASK-167-02-01: Reference And Vision Debug Profile Instrumentation

**Status:** ✅ Done
**Priority:** 🔴 High
**Parent:** [TASK-167-02](./TASK-167-02_Runtime_Instrumentation_And_Targeted_Log_Routing.md)
**Objective:** Add bounded `reference` and `vision` debug instrumentation to the existing reference attach/RU/compare/iterate/optional-support seams so operators can attribute slow attach paths, blocked readiness, checkpoint compare/iterate timing, backend selection, and optional classifier/segmentation follow-ons directly from the Docker/server terminal.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/vision/reference_support.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`
**Acceptance Criteria:**
- `debug=reference` emits attach/list/remove/clear lifecycle events, active vs pending reference counts, and RU refresh start/finish summaries without dumping raw image payloads
- `debug=reference` also emits bounded compare/iterate start/finish summaries,
  checkpoint labels or target-scope summaries, and key readiness transitions
- `debug=vision` emits RU backend provider/model selection, elapsed time, optional classifier/segmentation invoked vs skipped vs unavailable, and bounded failure reasons
- slow attach/RU sequences can be attributed to RU backend work versus optional support sidecars from the normal Docker/server terminal
- logs stay redacted: no provider secrets, raw image bytes, or unconstrained private paths

## Current Owner / Likely Edit Map

| Path | Current owner seam | Likely edit anchors | Why this leaf owns it |
|------|--------------------|---------------------|-----------------------|
| `server/adapters/mcp/areas/reference.py` | `reference_images(...)`, `reference_compare_stage_checkpoint(...)`, `reference_iterate_stage_checkpoint(...)` public facade | lines 1629-1656 and 1745-1780 | compare/iterate public seams stay here even though attach lifecycle moved into the runtime helper |
| `server/adapters/mcp/areas/reference_images_runtime.py` | `handle_reference_images(...)`, `_attach_reference_image(...)`, `_remove_reference_image(...)`, `_clear_reference_images(...)` | lines 228-427 | active vs pending reference adoption and RU refresh triggering are owned here, not in the thin facade |
| `server/adapters/mcp/areas/reference_understanding.py` | `refresh_reference_understanding_summary(...)` | lines 252-487 | RU backend invocation, cached-summary reuse, blocked/unavailable states, optional-support merge, and final persistence converge here |
| `server/adapters/mcp/areas/reference_compare_packets.py` | packet planning/execution seam | lines around packet planning/execution such as 831, 1373, and 1468 | compare/iterate timing and packet diagnostics ultimately flow through this owner, not only the facade |
| `server/adapters/mcp/vision/reference_support.py` | `_collect_classifier_support(...)`, `_collect_segmentation_support(...)`, `augment_reference_understanding_optional_support(...)` | lines 347-545 | optional support timing/unavailable behavior is owned here |
| `tests/unit/adapters/mcp/test_reference_images.py` | reference/RU proof lane | current attach/RU suites around lines 2940-3005 and related refresh tests | unit proof for attach/RU instrumentation belongs here |
| `tests/unit/adapters/mcp/test_reference_compare_packets.py` | packet-owner proof lane | current packet planning/execution tests | compare/iterate debug instrumentation should prove itself here too |
| `tests/e2e/integration/test_guided_gate_state_transport.py` | transport/runtime proof lane | current attach/list/remove/clear transport path | transport-visible reference/RU logging must not contradict the shipped runtime flow |

## Implementation Notes

- instrument attach in terms of lifecycle phases, not just “success”:
  - attach received
  - active vs pending adoption decision
  - RU refresh start
  - RU backend returned cached/blocked/available/unavailable
  - optional classifier/segmentation follow-on start/finish
- instrument compare/iterate in the same bounded `reference` scope:
  - compare/iterate call start
  - compact target/checkpoint identity
  - compare/iterate end state and elapsed time
- log elapsed durations for RU backend and optional support separately so slow
  attach or compare/iterate paths can be broken down without packet dumps
- keep the log surface observational; do not change attach/RU behavior in this
  leaf

## Pseudocode

```python
if debug_scope_enabled("reference"):
    logger.info("[REFERENCE_DEBUG] attach_start goal=%s active=%d pending=%d", goal, active_count, pending_count)

if debug_scope_enabled("vision"):
    logger.info("[VISION_DEBUG] ru_backend_start provider=%s reference_ids=%s", provider, reference_ids)

summary = await backend.analyze(request)

if debug_scope_enabled("vision"):
    logger.info("[VISION_DEBUG] ru_backend_done status=%s elapsed_ms=%d", summary.status, elapsed_ms)
```

## Runtime / Security Contract Notes

- logs remain summary-level and bounded
- no provider secrets, auth headers, raw image bytes, or full private local
  paths in normal debug output
- debug profiles must not unlock tools, pass gates, or change RU authority

## Error Cases To Cover

- attach with no active goal vs attach on a ready guided goal
- blocked RU because `reference_images_required`
- cached-summary reuse where only optional support refreshes
- RU backend unavailable/error
- classifier timeout/unavailable
- segmentation timeout/unavailable
- compare/iterate success vs blocked/unavailable vs degraded-assist paths

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- unit tests proving profile-gated emission on attach and RU refresh paths
- unit tests proving optional classifier/segmentation unavailability is logged
  as bounded summary-only data
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`

## Docs To Update

- `README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- historical closeout entry ownership belongs to
  [TASK-167-03-02](./TASK-167-03-02_Debug_Profile_Docs_Board_Changelog_And_Final_Proof.md)

## Status / Board Update

- remains nested under `TASK-167-02`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- final E2E/runtime proof for this leaf should be exercised through the
  repo-supported runner and the relevant updated integration coverage:
  - `poetry run python scripts/run_e2e_tests.py`
- if this leaf lands independently instead of only through family closeout,
  also run:
  - `PYTHONPATH=. poetry run pytest ./tests/unit`
  - `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`

## Validation Category

- focused unit tests first
- `git diff --check`
