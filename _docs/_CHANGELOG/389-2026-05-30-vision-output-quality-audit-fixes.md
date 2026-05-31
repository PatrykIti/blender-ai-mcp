# 389. Vision output quality audit fixes

Date: 2026-05-30

## Summary

Closed the concrete code and governance drift found in the Vision Output Quality
audit for `TASK-175` through `TASK-183`. The changes keep vision advisory while
making degraded evidence, model capability limits, geometric support, and task
board status visible and deterministic.

## Changes

- Added the missing field descriptions and public read-order docstrings for
  reference/vision contracts, including silhouette and part-segmentation
  contracts.
- Preserved packet-synthesis truncation accounting by carrying
  `evidence_truncated` / `omitted_count` through capped packet merges.
- Clamped top-level compare `confidence` to `[0, 1]` and range-constrained the
  result contract.
- Wired the optional labeled multi-view grid path into runtime config and
  staged/packet compare transmission behind `VISION_CAPTURE_GRID_ENABLED`, with
  `view_kind="grid"` and grid-aware captions.
- Reflected Blender depth/normal/object-ID pass methods on `ISceneTool`, added
  object-ID index-map based per-object IoU helper coverage, and added the
  support-evidence projection surface. Live per-object IoU population remains
  part of the open auxiliary-channel transmission lane.
- Passed resolved `model_capabilities` into response-schema/key selection,
  replaced raw default provider payload metadata with curated task framing, and
  surfaced provider token usage plus finish reason in capability summaries.
- Exposed a lightweight deterministic silhouette consistency score and
  iterate-loop convergence signal.
- Repaired task governance drift: `TASK-177`, `TASK-179`, `TASK-180`,
  `TASK-181`, and `TASK-182` now describe their remaining integration work
  instead of counting substrates as full runtime completion.

## Tests

Focused validation run during implementation:

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_compare_packets.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_tracks_previous_focus_and_iteration -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_runner.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_parsing.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_vision_capture_bundle.py tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_vision_prompting.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_vision_silhouette.py tests/unit/adapters/mcp/test_vision_external_backend.py tests/unit/adapters/mcp/test_vision_runner.py tests/unit/adapters/mcp/test_reference_images.py::test_reference_iterate_stage_checkpoint_tracks_previous_focus_and_iteration tests/unit/adapters/mcp/test_public_surface_docs.py -q` (238 passed)
- `PYTHONPATH=. poetry run pytest tests/unit/infrastructure/test_env_example.py -q` (2 passed)
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_capture_bundle.py -q` (12 passed after mypy cleanup)
- `PYTHONPATH=. poetry run pytest ./tests/unit` (3580 passed)
- `poetry run python scripts/run_e2e_tests.py` (491 passed, 5 skipped)
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure` (passed)
