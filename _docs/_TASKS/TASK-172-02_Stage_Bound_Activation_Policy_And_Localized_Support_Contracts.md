# TASK-172-02: Stage-Bound Activation Policy And Localized Support Contracts

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Depends On:** [TASK-172-01](./TASK-172-01_Internal_Vision_Capability_Inventory_And_Prerequisite_Diagnostics.md)
**Status:** ✅ Done
**Completed:** 2026-05-22
**Priority:** 🔴 High
**Objective:** Define exactly when RU refresh may merge already-available optional support artifacts and when staged compare/iterate may actively invoke localized optional perception, while keeping that support packet-bounded, advisory-only, and on the current public surfaces.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_images_runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/router.py`, `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/contracts/reference.py`, `server/adapters/mcp/contracts/quality_gates.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- heavy optional perception is not invoked by default for every reference or packet
- each localized invocation path names one bounded reason such as missing part ambiguity, anchor ambiguity, seam uncertainty, or local mask need
- first-wave active text-conditioned localization remains compare/iterate-only unless a later follow-on explicitly widens RU scope
- emitted contracts remain additive support evidence and do not become a second truth or gate authority path
- compare-time activation reasons and packet-local support stay readable through
  the existing compact feedback/status carriers instead of spawning a parallel
  guidance surface
- unit coverage proves the no-invocation default on at least one RU refresh path
  and one compare-packet path when no localized trigger reason exists

## Implementation Notes

- do not build a new global trigger engine; keep activation policy on the seams
  that already own reference refresh and packet compare:
  - `reference_images(...)` / RU refresh
  - staged compare packet planning
  - staged iterate follow-up
- this leaf owns policy and support-contract vocabulary only; concrete adapter
  work for localization and segmentation lands in `TASK-172-03` and
  `TASK-172-04`
- RU refresh may surface previously collected or lightweight optional support
  notes, but first-wave active text-conditioned grounding stays off the default
  reference-context establishment path
- keep `reference_compare_packets.py` as the durable compare-time execution
  owner; `vision/reference_support.py` remains RU-only unless a shared helper
  is explicitly extracted first
- current guided/reference feedback owners already project compare diagnostics,
  evidence summaries, and next-tool guidance through
  `build_reference_orchestrator_feedback(...)` and `router_get_status(...)`;
  extend those seams when localized invocation reasons need to surface outside
  the packet payload itself
- likely owner functions/classes:
  - `refresh_reference_understanding_summary(...)`
  - `_optional_support_needs_refresh(...)`
  - `build_compare_packets(...)`
  - `execute_compare_packets(...)`
  - `ComparePacketPolicy`
  - `ReferenceComparePacketContract`
  - `build_reference_orchestrator_feedback(...)`
  - `_build_compare_segmentation_request_payload(...)`
  - `resolve_active_compare_scope(...)`
- invocation reasons should land on one explicit typed seam:
  - one additive `localized_support_reason` field on
    `ReferenceComparePacketContract`
  - compare policy decisions on `ComparePacketPolicy`
  - payload builders such as `_build_compare_segmentation_request_payload(...)`
  do not leave them as free-form ad hoc fields
- define one small normalized vocabulary for invocation reasons, for example:
  - `part_missing_ambiguity`
  - `anchor_ambiguity`
  - `attachment_gap`
  - `seam_unclear`
  - `mask_needed`
- localized support payloads should carry bounded scope:
  - packet id or compare slice
  - reference ids / view ids
  - target role labels or target objects where already known
  - optional focus pair or local region hint
- preserve the current rule that optional perception may inform support
  evidence, planner hints, or operator diagnostics, but not final completion

## Pseudocode

```python
if packet.localized_support_reason in {"seam_unclear", "part_missing_ambiguity"}:
    payload = _build_compare_segmentation_request_payload(
        packet=packet,
        capture_subset=captures,
        reference_subset=references,
    )
```

## Runtime / Security Contract Notes

- no default full-image heavy pass
- no implicit adapter startup during unrelated guided steps
- no heavy grounding runs during default RU attach/list/clear flows in the
  first wave
- localized support requests must stay bounded in image count, region scope, and
  returned artifacts

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`

## Changelog Impact

- record the new activation-policy and support-contract vocabulary in the first
  `TASK-172` runtime entry that ships this leaf

## Completion Summary

- normalized compare-time optional support around one packet-local
  `localized_support_reason` field on `ReferenceComparePacketContract`
- kept active localized support bounded to compare-time packet execution
  instead of broad RU-time or whole-image heavy passes
- made the optional segmentation sidecar no-op cleanly on packets that have no
  localized-support trigger reason, even when the sidecar is configured

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- localized support policy and transport proof
