# 332. TASK-166 owner seam relocation and viewport proof hardening

Date: 2026-05-09

## Summary

- moved the TASK-166 packet policy / packet execution owner seam fully into
  `server/adapters/mcp/areas/reference_compare_packets.py`, including:
  - packet planning helpers
  - compare-time segmentation sidecar collection/merge
  - packet extraction / ranking execution
  - packet synthesis and diagnostics emission helpers
- removed the old `server/application/services/reference_compare_packets.py`
  seam so the live code no longer mixes MCP adapter contracts into an
  application-layer module
- kept `server/adapters/mcp/areas/reference.py` orchestration-first by routing
  staged compare through the dedicated helper seam and passing the runtime test
  doubles explicitly for packet compare execution
- rewired the compare-time segmentation path so
  `server/adapters/mcp/vision/reference_support.py` is back to RU-oriented
  optional support, while compare-time packet sidecars live on the staged
  compare owner seam
- hardened the Blender-backed viewport restore proof lane by replacing flaky
  byte-for-byte JPEG equality with direct `get_view_state()` restoration checks

## Runtime / Contract Notes

- public staged compare / iterate contracts are unchanged; this slice only
  relocates internal owner seams and stabilizes the Blender E2E proof lane
- compare-time packet sidecars are still advisory-only and additive, but they
  are now owned by the staged compare seam instead of the RU support module
- the viewport restore expectation is state-based, not image-byte-based; the
  updated E2E proof now validates the actual restore contract directly

## Validation

- `git diff --check`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --all-files --show-diff-on-failure`
