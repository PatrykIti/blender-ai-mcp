# TASK-172-03: GroundingDINO Or OWL Localization For Packet-Bounded Part Ambiguity

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one optional packet-bounded text-conditioned localization adapter family that can produce bounded compare-time crop/landmark-style part cues for ambiguous reference regions during staged compare and iterate work, while reusing the existing compare-time optional-perception public carriers.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- a default-off localization adapter can emit bounded compare-time crop/landmark-style cues for roles such as `tail_mass`, `snout_mass`, `ear_pair`, or limb roles on staged compare/iterate packets
- localization output is tied to packet/reference/view provenance and remains advisory-only
- the first compare-time shipping path does not add a new public box contract; it projects localization onto the existing compare-time `part_segmentation` carrier or is split into a follow-on contract leaf before implementation

## Implementation Notes

- first shipping adapter posture:
  - `generic_sidecar` provider family
  - one new dedicated config lane only if the existing segmentation/classifier
    config cannot express localization cleanly
  - vendor-specific behavior stays behind a vendor-neutral internal adapter seam
- this first leaf is compare-time only; RU-side boxed artifact linkage remains
  on the separate RU artifact/readiness owners and is not reopened here
- reuse the existing compare-time optional-perception public carriers:
  - `ReferencePartSegmentationContract`
  - existing compare-time `support_evidence` paths that already use
    `evidence_kind="part_segmentation"`
- map the emitted support onto the current staged owners:
  - `localized_support_reason` on `ReferenceComparePacketContract`
  - `ReferencePartSegmentationContract`
  - `ReferenceComparePacketContract`
  - `_build_compare_segmentation_request_payload(...)`
  - `_normalize_compare_part_segmentation_payload(...)`
  - `collect_compare_time_segmentation_support(...)` or one sibling helper on
    the same staged compare owner seam
  - `merge_compare_time_part_segmentation(...)`
  - compare-packet-local support collection
  - planner / feedback consumers that already read support evidence
- acceptable first adapter families:
  - GroundingDINO-like text-conditioned boxes
  - OWL / OWL-ViT-style text-conditioned localization
- first use cases should be narrow:
  - missing/ambiguous tail or snout region
  - ear vs eye vs face-attachment ambiguity
  - foreleg vs hindleg local ambiguity
  - anchor ambiguity for already-created parts
- this first leaf is packet-scoped on purpose; if RU-scoped localization later
  proves necessary, track it as a follow-on under `TASK-172` instead of
  widening this leaf ad hoc
- if literal boxes are still needed on the compare-time public surface after a
  first crop/landmark projection pass, create one explicit follow-on contract
  leaf before widening `ReferencePartSegmentationContract`
- first compare-time shipping path should therefore project boxes into the
  existing `ReferencePartSegmentationPartContract` fields:
  - `crop_path`
  - `confidence`
  - optional landmark anchors
  rather than adding a new public box field in this leaf
- keep DINOv2 dense features out of this first wave; they are not the most
  direct tool for actionable LLM-facing part feedback

## Pseudocode

```python
boxes = localize_parts(
    labels=["tail_mass", "body_core"],
    reference_ids=packet.reference_ids,
    capture_labels=packet.capture_labels,
)
return ReferencePartSegmentationContract(
    status="available",
    advisory_only=True,
    parts=project_localization_to_crops_and_landmarks(boxes),
)
```

## Runtime / Security Contract Notes

- localization providers remain optional and default-off
- no raw image bytes or oversized model-native payloads on public contracts
- box/crop cues must remain support-only and must not become planner or
  verifier authority on their own

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- optional harness/eval coverage only behind explicit env/config flags

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` when operator setup for the
  adapter becomes real

## Changelog Impact

- name the chosen localization family and its advisory-only boundary when this
  leaf ships

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- optional localization adapter and advisory-support proof
