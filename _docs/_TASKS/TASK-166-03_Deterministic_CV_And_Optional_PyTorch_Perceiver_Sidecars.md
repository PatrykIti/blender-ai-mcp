# TASK-166-03: Deterministic CV And Optional PyTorch Perceiver Sidecars

**Parent:** [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)  
**Status:** ⏳ To Do  
**Priority:** 🔴 High
**Objective:** Feed compact image evidence into compare packets through always-on deterministic CV support evidence and optional heavier PyTorch-based advisory adapters.

## Repository Touchpoints

- `server/adapters/mcp/areas/reference_silhouette.py`
- `server/adapters/mcp/vision/reference_support.py`
- `server/adapters/mcp/areas/reference.py`
- `server/adapters/mcp/contracts/reference.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `_docs/_VISION/README.md`

## Implementation Notes

- Always-on lightweight CV should pre-chew low-level image facts.
- Optional PyTorch sidecars should enrich packets when they materially improve
  compare quality, but remain advisory-only.

## Current Flow Integration

- Compare-time always-on heuristic CV should extend the existing
  `reference_silhouette.py` seam first, because that is where the current staged
  compare path already emits deterministic silhouette evidence and action hints.
- Always-on CV should feed packet-level evidence slots on the staged compare
  family before the LLM compare question is assembled.
- Optional PyTorch sidecars should extend the existing `reference_support.py`
  seam instead of creating a second parallel perception stack, but the current
  repo entrypoint there is still RU augmentation and must not be mistaken for
  the already-shipped compare-time heuristic CV owner.
- Packet compare should consume these pre-chewed facts so the LLM is asked
  narrower questions rather than raw broad image interpretation.
- Compare-time evidence should extend the staged compare contracts without
  overloading RU-only fields or duplicating `silhouette_analysis` /
  `part_segmentation` as a parallel evidence channel.

## Pseudocode

```text
cv_evidence = build_compare_time_cv(packet, captures, references)
sidecar_evidence = maybe_collect_compare_time_sidecars(packet, runtime_config)
packet_inputs = merge_packet_support_evidence(cv_evidence, sidecar_evidence)
staged_compare = project_packet_support_into_staged_contract(packet_inputs)
```

## Runtime / Security Contract Notes

- Deterministic compare-time CV extends the existing public staged compare
  surface; it must remain compact, machine-readable, and non-authoritative on
  its own.
- Optional sidecars stay default-off and advisory-only, with failures degrading
  to bounded availability notes instead of breaking staged compare.
- Compare-time evidence should not overload RU-only support contracts or create
  a second perception/public-discovery flow.

## Acceptance Criteria

- packet evidence no longer depends only on raw LLM perception
- always-on deterministic CV remains bounded support evidence
- optional heavy adapters stay advisory-only and explicitly bounded
- support evidence lands in the existing staged compare family rather than in a
  second planner/evidence flow

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- targeted unit coverage for compare-time support-evidence shaping in
  `reference_silhouette.py` and staged compare assembly; expand
  `reference_support.py` coverage only when that seam is deliberately extended
  beyond RU
- `tests/e2e/vision/test_reference_stage_silhouette_contract.py`
- selected integration/runtime proof when compare-time packet evidence changes
  the staged public payload

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_TESTS/README.md`

## Changelog Impact

- include in the umbrella `_docs/_CHANGELOG/` entry when compare-time support
  evidence ships

## Status / Board Update

- keep parent `TASK-166` and this subtask aligned in `_docs/_TASKS/README.md`
- call out explicitly whether compare-time CV landed through the silhouette
  seam only or whether optional sidecar extensions also shipped

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_stage_silhouette_contract.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
