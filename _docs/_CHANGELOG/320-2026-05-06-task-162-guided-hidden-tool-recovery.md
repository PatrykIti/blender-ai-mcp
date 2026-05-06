# 320. TASK-162 guided hidden-tool recovery and visibility alignment

Date: 2026-05-06

## Summary

- hardened the guided discovery proxy in
  `server/adapters/mcp/discovery/search_surface.py` so `call_tool(...)` now
  distinguishes:
  - truly unknown public tool ids
  - known guided tools hidden by the current surface/phase
  - known guided tools hidden specifically because
    `spatial_refresh_required` re-armed the live spatial gate
- made the spatial-refresh recovery message derive from the live pending
  `required_checks` list instead of a static recovery paragraph
- aligned guided handoff wording and live surface instructions so
  `guided_handoff` is treated as continuation context while
  `router_get_status().visibility_rules` stays the authoritative current
  surface after visibility transitions
- removed attachment-alignment mutators from the shaped
  `inspect_validate` surface during refresh-barrier states where guided policy
  would fail-close `attachment_alignment` anyway
- expanded proof lanes across unit, stdio, Streamable HTTP, guided parity, and
  inspect/validate coverage so hidden-tool failures read as recoverable contract
  errors instead of apparent disconnects

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_search_surface.py -q`
  - result on this machine: `57 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_visibility_policy.py -q`
  - result on this machine: `18 passed`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_server_factory.py -q`
  - result on this machine: `6 passed`
- outside sandbox:
  - `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_search_first_call_tool_boundary.py tests/e2e/integration/test_guided_streamable_spatial_support.py tests/e2e/integration/test_guided_surface_contract_parity.py tests/e2e/integration/test_guided_inspect_validate_handoff.py tests/e2e/router/test_guided_manual_handoff.py -q`
  - result on this machine: `18 passed`
  - `poetry run python scripts/run_e2e_tests.py`
  - result on this machine: attempted, but the spawned Blender-backed runner
    blocked on `Address already in use` for RPC port `8765` while another
    active Blender/RPC process already held that port
