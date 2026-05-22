# 364. TASK-172 harness and family closeout

Date: 2026-05-23

## Summary

Closed the remaining `TASK-172` harness/governance work and finished the full
optional-vision runtime family.

## Changes

- added one explicit `scripts/vision_harness.py --mode localized-support`
  operator path for the packet-local optional support owner seam
- kept the normal backend-running harness path unchanged and made the new
  localized-support path opt-in only
- added harness/subprocess proof and negative coverage for:
  - disabled optional localized support
  - unavailable / timeout localization
  - empty localization results
  - localization-seeded segmentation
- updated Vision/MCP operator docs with localized-support harness examples and
  the shipped localization env surface
- marked `TASK-172-06` done and closed `TASK-172-07` with explicit proof-lane
  accounting
- closed the umbrella `TASK-172` family and moved it to the done board section

## Proof Lanes

- unit:
  - targeted harness/support tests
  - full repo-wide unit suite
- transport / integration:
  - guided gate-state transport coverage for localization and segmentation
    sidecars over stdio and streamable HTTP
- Blender-backed:
  - full `poetry run python scripts/run_e2e_tests.py` runner
- optional live-provider:
  - not required for closeout
  - live OpenRouter vision tests remain explicitly skipped when credentials or
    runtime setup are unavailable

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/scripts/test_script_tooling.py tests/e2e/vision/test_reference_understanding_fixture_only_harness.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q -k 'localized_support or vision_harness or localization_support'`
- `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_env_example.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q -k 'localization_sidecar_transport'`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
