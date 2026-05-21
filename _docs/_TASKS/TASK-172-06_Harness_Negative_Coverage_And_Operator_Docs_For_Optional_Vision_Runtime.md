# TASK-172-06: Harness, Negative Coverage, And Operator Docs For Optional Vision Runtime

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🟠 High
**Objective:** Add harness support, negative coverage, and operator-facing docs for localized optional perception paths without changing default backend-running semantics or public authority boundaries.
**Repository Touchpoints:** `scripts/vision_harness.py`, `tests/unit/scripts/test_script_tooling.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/integration/test_mcp_transport_modes.py`, `tests/e2e/integration/test_guided_surface_contract_parity.py`, `_docs/_VISION/README.md`, `_docs/_MCP_SERVER/README.md`, `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`
**Acceptance Criteria:**
- the harness can exercise localized optional-perception paths through one explicit opt-in mode or flag without changing the current default backend-running path
- negative coverage proves disabled, unavailable, timeout, and empty-result behavior for optional adapters
- operator docs describe setup, degraded behavior, and advisory-only limits without implying truth or gate authority

## Implementation Notes

- preserve the current default harness semantics unless a new explicit opt-in
  mode is selected
- this leaf owns only the localized-perception delta on harness/docs surfaces;
  generic capability-aware runtime harness/docs closeout remains on
  `TASK-140-06-04`
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
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/integration/test_mcp_transport_modes.py`
- `tests/e2e/integration/test_guided_surface_contract_parity.py`
- `tests/e2e/vision/test_reference_guided_creature_comparison.py` when harness
  subprocess defaults or CLI execution semantics change
- `tests/e2e/vision/test_real_view_variant_model_comparison.py` when harness
  comparison subprocess semantics change

## Docs To Update

- `_docs/_VISION/README.md` only for the localized-perception delta owned by
  `TASK-172`, not the broader capability-summary/harness closeout already owned
  by `TASK-140-06-04`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- record harness mode and operator guidance changes in the first `TASK-172`
  entry that ships this leaf

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py tests/e2e/integration/test_mcp_transport_modes.py tests/e2e/integration/test_guided_surface_contract_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_guided_creature_comparison.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_real_view_variant_model_comparison.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- harness, negative-coverage, and operator-doc proof
