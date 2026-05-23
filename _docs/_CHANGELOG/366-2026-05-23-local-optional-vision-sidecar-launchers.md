# 366. Local optional vision sidecar launchers

Date: 2026-05-23

## Summary

Added repo-local segmentation and localization sidecar helpers plus
`run_streamable_openrouter.sh` auto-start support, so the optional compare-time
vision adapters can be launched the same way as the existing classifier sidecar.

## Changes

- added repo-local sidecar servers:
  - `scripts/segmentation_sidecar.py`
  - `scripts/localization_sidecar.py`
  - shared payload/file helpers in `scripts/vision_sidecar_common.py`
- added foreground operator helpers:
  - `scripts/run_segmentation_sidecar.sh`
  - `scripts/run_localization_sidecar.sh`
- taught `scripts/run_streamable_openrouter.sh` to:
  - auto-start the local segmentation sidecar when
    `VISION_SEGMENTATION_ENABLED=true` and `SEGMENTATION_SIDECAR_AUTO_START=true`
  - auto-start the local localization sidecar when
    `VISION_LOCALIZATION_ENABLED=true` and `LOCALIZATION_SIDECAR_AUTO_START=true`
  - derive Docker-safe `host.docker.internal` endpoints for all three
    sidecars
  - forward the full `VISION_LOCALIZATION_*` runtime contract into the
    container
- documented that the first local launch downloads the configured model
  weights automatically, matching the current classifier-sidecar operator flow

## Validation

- `git diff --check`
- `poetry run pytest tests/unit/scripts/test_script_tooling.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `poetry run pre-commit run --all-files --show-diff-on-failure`
