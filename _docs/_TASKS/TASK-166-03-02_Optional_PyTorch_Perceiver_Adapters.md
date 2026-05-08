# TASK-166-03-02: Optional PyTorch Perceiver Adapters

**Parent:** [TASK-166-03](./TASK-166-03_Deterministic_CV_And_Optional_PyTorch_Perceiver_Sidecars.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Define the optional PyTorch-based perception adapters that can enrich compare packets when lightweight CV is not enough, while keeping compare-time sidecars advisory-only.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `server/adapters/mcp/vision/reference_support.py`
- `server/infrastructure/config.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
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
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- compare-time sidecar availability / staged-contract projection tests
- `tests/e2e/integration/test_guided_gate_state_transport.py` when optional
  sidecar surfacing changes client-visible staged compare / iterate payloads

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
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
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
