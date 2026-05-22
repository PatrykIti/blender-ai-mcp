# TASK-172-03: GroundingDINO Or OWL-ViT / OWLv2 Packet Localization For Part Ambiguity

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Depends On:** [TASK-172-02](./TASK-172-02_Stage_Bound_Activation_Policy_And_Localized_Support_Contracts.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one optional packet-bounded text-conditioned localization adapter family that can produce bounded compare-time localization candidates for ambiguous reference regions during staged compare and iterate work, keep those candidates tied to packet/reference/view provenance, and project only support-safe crops or derived anchor hints on the current public carriers.
**Repository Touchpoints:** `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- a default-off localization adapter can emit bounded compare-time localization candidates for roles such as `tail_mass`, `snout_mass`, `ear_pair`, or limb roles on staged compare/iterate packets
- localization output is tied to packet/reference/view provenance and remains advisory-only
- the first shipped compare-time path projects localization onto the existing `part_segmentation` public carrier with no new public box field on the compare-time surface

## Execution Structure

| Order | Leaf | Purpose |
|------|------|---------|
| 1 | [TASK-172-03-01](./TASK-172-03-01_Localization_Runtime_Config_And_Provider_Boundary.md) | Add the default-off localization runtime/config seam and one internal provider-neutral candidate contract without widening public compare payloads yet |
| 2 | [TASK-172-03-02](./TASK-172-03-02_Compare_Time_Localization_Projection_And_Transport.md) | Invoke packet-bounded localization on staged compare/iterate and project only support-safe crops/derived anchors through the existing compare-time carriers |

## Implementation Notes

- keep this subtask split so the repo can land runtime/provider plumbing before
  it widens compare-time transport; do not hide provider contract work,
  compare-time projection, and potential operator packaging inside one
  oversized implementation pass
- first shipping adapter posture:
  - `generic_sidecar` provider family
  - one new dedicated config lane only if the existing segmentation/classifier
    config cannot express localization cleanly
  - vendor-specific behavior stays behind a vendor-neutral internal adapter seam
- this subtask remains compare-time only; the public projection leaf
  intentionally follows the existing segmentation seam expansion from
  `TASK-172-04`, while RU-side boxed artifact linkage remains on the separate
  RU artifact/readiness owners and is not reopened here
- keep `reference_compare_packets.py` as the durable compare-time execution
  owner; do not turn the RU-specific `vision/reference_support.py` helper into
  the default packet-evidence execution seam
- internal localization candidates may keep literal box data for downstream
  segmentation seeding, but first-wave public transport stays support-only
  through:
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
  - GroundingDINO-like phrase-grounded boxes
  - OWL-ViT / OWLv2-style open-vocabulary localization
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
  - optional derived anchor hints
  rather than adding a new public box field in this leaf
- keep DINOv2 dense features out of this first wave; they are not the most
  direct tool for actionable LLM-facing part feedback

## Pseudocode

```python
localization_candidates = localize_parts(
    labels=["tail_mass", "body_core"],
    reference_ids=packet.reference_ids,
    capture_labels=packet.capture_labels,
)
return ReferencePartSegmentationContract(
    status="available",
    advisory_only=True,
    parts=project_localization_to_crops_and_landmarks(localization_candidates),
)
```

## Runtime / Security Contract Notes

- localization providers remain optional and default-off
- no raw image bytes or oversized model-native payloads on public contracts
- box/crop cues must remain support-only and must not become planner or
  verifier authority on their own

## Tests To Add/Update

- split across the execution leaves above:
  - `TASK-172-03-01` owns runtime/config/provider tests
  - `TASK-172-03-02` owns compare-time transport, packet, and staged-surface
    validation

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
- keep `TASK-172-03-01` and `TASK-172-03-02` nested under this subtask while
  the localization family stays open

## Validation Commands

- `git diff --check`
- child leaves own the exact validation commands; run the combined `TASK-172-03`
  proof only after both leaves land

## Validation Category

- optional localization adapter and advisory-support proof
