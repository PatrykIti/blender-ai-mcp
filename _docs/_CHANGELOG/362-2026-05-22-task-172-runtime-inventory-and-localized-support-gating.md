# 362. TASK-172 runtime inventory and localized support gating

Date: 2026-05-22

## Summary

Landed the first concrete `TASK-172` runtime slice on the existing optional
vision seams and repaired the biggest task/docs drift around what is already
shipped versus what remains open.

## Changes

- added one internal typed optional capability inventory on the vision runtime
  config seam covering:
  - external model capability metadata
  - optional reference-classifier support
  - optional packet-local segmentation support
  - the planned-but-unshipped part-localization slot
- added a normalized packet-local `localized_support_reason` contract field on
  staged compare packets and used it to gate compare-time optional support
- stopped compare-time segmentation from auto-running on clean/no-trigger
  packets just because the sidecar is configured
- kept the shipped `part_segmentation` carrier advisory-only, packet-bounded,
  and transport-safe while preserving disabled/unavailable degradation
- updated Vision/MCP docs and router tool metadata to document
  `localized_support_reason`, packet-bounded activation, and the clean
  `part_segmentation.status="disabled"` outcome when no localized-support
  trigger exists
- synchronized the active `TASK-172` planning docs with current evidence:
  - `TASK-172-01` and `TASK-172-02` are now marked done
  - `TASK-172-04` is now closed administratively as superseded because its
    shipped segmentation-sidecar scope already lives on earlier owner tasks
  - `TASK-172`, `TASK-172-05`, `TASK-172-06`, and `TASK-172-07` remain open
    where real runtime or governance work still exists

## Validation

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`

## Notes

- this entry does not close the full `TASK-172` umbrella
- text-conditioned localization, heavy-local lifecycle ownership, the explicit
  localized-support harness lane, and final board/changelog closeout remain
  open under the existing `TASK-172` family
