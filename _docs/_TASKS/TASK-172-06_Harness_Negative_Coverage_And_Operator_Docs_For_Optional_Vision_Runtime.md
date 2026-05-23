# TASK-172-06: Harness, Negative Coverage, And Operator Docs For Optional Vision Runtime

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Depends On:** [TASK-172-03-02](./TASK-172-03-02_Compare_Time_Localization_Projection_And_Transport.md)
**Status:** ✅ Done
**Completed:** 2026-05-23
**Priority:** 🟠 High
**Objective:** Add explicit staged-compare/localized-support harness coverage or expand the existing `scripts/vision_harness.py` into that role, then add negative coverage and operator-facing docs for localized optional perception paths without changing default backend-running semantics or public authority boundaries.
**Repository Touchpoints:** `scripts/vision_harness.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `tests/unit/scripts/test_script_tooling.py`, `tests/e2e/vision/test_reference_understanding_fixture_only_harness.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
**Acceptance Criteria:**
- the harness can exercise localized optional-perception paths through one explicit opt-in staged-compare/localized-support mode, or an equivalent new compare-harness subprocess suite, without changing the current default backend-running path
- negative coverage proves disabled, unavailable, timeout, and empty-result behavior for optional adapters
- operator docs describe setup, degraded behavior, and advisory-only limits without implying truth or gate authority

## Implementation Notes

- preserve the current default harness semantics unless a new explicit opt-in
  mode is selected
- this leaf owns only the localized-perception delta on harness/docs surfaces;
  generic capability-aware runtime harness/docs closeout remains on
  `TASK-140-06-04`
- the current `scripts/vision_harness.py` is a raw backend/request runner, not
  yet a staged compare packet harness; this leaf must either expand it into
  that role explicitly or introduce a dedicated compare-harness helper before
  treating it as the primary localized-support owner
- negative coverage must exercise the current packet-local owner seam on
  `reference_compare_packets.py`, not only the raw backend runner, so the
  docs/harness proof matches the shipped localized-support execution path
- likely harness owners:
  - `_run_backend(...)`
  - `_run(...)`
  - any new explicit fixture/adapter mode selector
- negative coverage must prove:
  - disabled optional adapter
  - unavailable optional adapter
  - timeout or empty result on optional adapter
  - no accidental promotion of support evidence into completion truth
- if localized optional perception changes client-visible compare/iterate
  payloads, keep stdio and Streamable HTTP transport parity on the same branch

## Pseudocode

```python
if args.localized_optional_mode == "off":
    run_default_backend_path()
elif args.localized_optional_mode == "packet_support":
    run_backend_with_optional_packet_support()
```

## Runtime / Security Contract Notes

- any new harness flag must keep default execution semantics unchanged
- client-visible compare/iterate payload changes must stay parity-safe across
  stdio and Streamable HTTP
- operator docs must keep external-provider setup, optional sidecar setup, and
  advisory-only boundaries explicit

## Tests To Add/Update

- `tests/unit/scripts/test_script_tooling.py`
- `tests/e2e/vision/test_reference_understanding_fixture_only_harness.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py` when harness
  subprocess defaults, staged packet semantics, or CLI execution semantics
  change
- optional secondary smoke/eval lanes only when the branch widens scope beyond
  localized-support ownership:
  - `tests/e2e/integration/test_mcp_transport_modes.py`
  - `tests/e2e/integration/test_guided_surface_contract_parity.py`
  - `tests/e2e/vision/test_real_view_variant_model_comparison.py`

## Docs To Update

- `_docs/_VISION/README.md` only for the localized-perception delta owned by
  `TASK-172`, not the broader capability-summary/harness closeout already owned
  by `TASK-140-06-04`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- record harness mode and operator guidance changes in the first `TASK-172`
  entry that ships this leaf

## Completion Summary

- `scripts/vision_harness.py` now has one explicit `--mode localized-support`
  path for the packet-local optional support owner seam
- that mode keeps the normal backend-running path unchanged and can exercise:
  - disabled optional support
  - unavailable / timeout localization
  - empty localization results
  - localization-seeded segmentation
- subprocess coverage now proves both the explicit fixture-only seam and the
  live disabled-by-default localized-support CLI path
- unit coverage now proves unavailable / timeout localization, empty results,
  localization-seeded segmentation, and the no-promotion boundary from support
  evidence into truth

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_fixture_only_harness.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_creature_comparison.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- harness, negative-coverage, and operator-doc proof
