# TASK-166-03-02: Optional PyTorch Perceiver Adapters

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ✅ Done
**Priority:** 🔴 High
**Objective:** Define the optional PyTorch-based perception adapters that can enrich compare packets when lightweight CV is not enough, while keeping compare-time sidecars advisory-only.

## Completion Summary

- staged compare/iterate now execute the optional compare-time segmentation
  sidecar per packet when operators explicitly enable it on runtime config
- packet-local sidecar output now merges into the existing top-level
  `part_segmentation` envelope instead of remaining a disabled/unavailable
  placeholder only
- packet-local `support_evidence` can now carry bounded
  `evidence_kind="part_segmentation"` items, so compare prompts receive compact
  sidecar cues without creating a second perception flow
- sidecar failure or empty output remains advisory-only and degrades to bounded
  `part_segmentation.status="unavailable"` notes instead of blocking staged
  compare or emitting correction authority on its own

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/reference_support.py`
- `server/adapters/mcp/areas/reference_compare_packets.py`
- `server/adapters/mcp/vision/config.py`
- `server/adapters/mcp/vision/runtime.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `_docs/_VISION/README.md`

## Implementation Notes

- Candidate adapters:
  - SigLIP2 / CLIP / DINOv2 for style or coarse similarity signals
  - SAM2-style segmentation for packet-level masks
  - GroundingDINO / OWL-ViT style part proposals for text-conditioned part cues
- Keep them default-off unless one adapter graduates into a clearly justified
  default support path.
- Attach-time global classifier support remains on the existing
  `reference_understanding` bootstrap path from `TASK-163`; this leaf only
  covers compare-time packet-local advisory usage when enabled.
- Reuse of `server/adapters/mcp/vision/reference_support.py` is optional and
  shared-adapter-oriented; compare-time packet evidence now lives on
  `server/adapters/mcp/areas/reference_compare_packets.py` so it does not look
  like an attach-time RU concern or collapse staged compare execution back into
  the RU pipeline.
- If compare-time sidecar execution grows beyond the current helper, keep it on
  the staged compare-specific owner seam and leave RU support code as optional
  shared infrastructure rather than the default execution owner.
- Because the compare-time sidecars must surface through staged compare
  responses, any emitted sidecar artifacts or availability state still route
  through `server/adapters/mcp/areas/reference.py` and the public staged
  contracts, not only through the backend adapter seam.

## Acceptance Criteria

- optional heavy adapters are scoped as advisory-only compare enrichers
- the task family names clear upgrade criteria before anything becomes default-on
- compare-time sidecars cannot become the sole basis for emitted correction
  candidates or packet completion claims

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- compare-time sidecar availability / staged-contract projection tests
- advisory-only negative coverage where available `part_segmentation` support
  evidence does not emit correction candidates or completion claims by itself
- `tests/e2e/integration/test_guided_gate_state_transport.py` when optional
  sidecar surfacing changes client-visible staged compare / iterate payloads

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` only when dedicated
  compare-time sidecar env/config examples are added alongside or instead of the
  existing RU-oriented examples
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when compare-time sidecar
  surfacing ships

## Status / Board Update

- keep parent `TASK-166` and this leaf aligned when compare-time sidecar work
  closes or remains explicit follow-on scope

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `poetry run pytest ./tests/unit`
- `poetry run python scripts/run_e2e_tests.py`
