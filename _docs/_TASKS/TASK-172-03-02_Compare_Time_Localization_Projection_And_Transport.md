# TASK-172-03-02: Compare-Time Localization Projection And Transport

**Parent:** [TASK-172-03](./TASK-172-03_GroundingDINO_Or_OWL_Localization_For_Packet_Bounded_Part_Ambiguity.md)
**Depends On:** [TASK-172-03-01](./TASK-172-03-01_Localization_Runtime_Config_And_Provider_Boundary.md), [TASK-172-04](./TASK-172-04_SAM_Or_SAM2_Local_Mask_And_Landmark_Support.md)
**Status:** ✅ Done
**Completed:** 2026-05-23
**Priority:** 🔴 High
**Objective:** Invoke packet-bounded localization on staged compare/iterate packets and project the resulting support only through the existing compare-time carriers, keeping literal boxes internal unless a later explicit contract leaf promotes them.
**Repository Touchpoints:** `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/unit/router/application/test_router_contracts.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- compare-time localization runs only for packet-bounded ambiguous scopes that already carry one normalized localized-support reason
- internal localization candidates keep packet/reference/view provenance plus literal box data for downstream mask seeding, but first-wave public transport projects only support-safe crops and optional derived anchors onto existing compare-time carriers
- feedback, transport, and staged compare payloads remain additive and advisory-only, with no new public box field introduced in this leaf

## Implementation Notes

- this leaf is the place where compare-time localization actually joins staged
  compare; do not route it through RU-only `vision/reference_support.py`
- use the expanded segmentation seam from `TASK-172-04` as the public
  projection carrier, so localization can seed or refine masks/crops without
  reopening the base `part_segmentation` contract vocabulary
- compare packets already expose the typed `localized_support_reason` seam from
  `TASK-172-02`; this leaf should reuse that field and extend parity /
  feedback/status projection only where localization-specific transport needs it
- likely owner seams:
  - `build_compare_packets(...)`
  - `execute_compare_packets(...)`
  - `_build_compare_segmentation_request_payload(...)`
  - `collect_compare_time_segmentation_support(...)` or one sibling helper
  - `merge_compare_time_part_segmentation(...)`
  - `build_reference_orchestrator_feedback(...)`
- planner/feedback consumers may summarize the support, but they must not
  treat localization-derived crops or anchors as truth or completion proof

## Pseudocode

```python
if packet.localized_support_reason == "part_missing_ambiguity":
    candidates = collect_compare_time_localization_candidates(packet, captures, references)
    segmentation = collect_compare_time_segmentation_support(
        packet=packet,
        localization_candidates=candidates,
    )
    packet.support_evidence = build_compare_support_evidence(
        silhouette_analysis,
        action_hints=action_hints,
        part_segmentation=segmentation,
    )
```

## Runtime / Security Contract Notes

- localized support remains packet-bounded in image count, region scope, and
  projected payload size
- literal boxes stay internal in this leaf
- transport parity must hold across stdio and Streamable HTTP for any new
  packet fields or support-evidence summaries

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/router/application/test_router_contracts.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` when concrete operator setup
  for localization becomes real

## Changelog Impact

- name the first compare-time localization projection path and its
  advisory-only transport boundary when this leaf ships

## Completion Summary

- compare-time localization now runs only on packets that already carry a
  bounded `localized_support_reason`
- localization candidates remain internal but can seed compare-time
  segmentation through `seed_boxes`
- localization-only runs project support-safe `crop_path` plus derived
  `box_center` anchors onto the existing `part_segmentation` carrier, with no
  public raw box field added
- transport proof now covers localization support over the guided compare
  transport path

## Status / Board Update

- remains nested under `TASK-172-03`; no promoted board-row change by itself

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/router/application/test_router_contracts.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- compare-time localization transport and advisory-projection proof
