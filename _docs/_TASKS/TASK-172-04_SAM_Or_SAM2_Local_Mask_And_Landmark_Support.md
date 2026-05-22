# TASK-172-04: SAM Or SAM 2 Packet-Local Mask, Crop, And Derived-Anchor Support

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Depends On:** [TASK-172-02](./TASK-172-02_Stage_Bound_Activation_Policy_And_Localized_Support_Contracts.md)
**Status:** ⏭️ Superseded
**Superseded By:** [TASK-128-03](./TASK-128-03_Optional_Part_Segmentation_Sidecar_And_Part_Aware_Perception.md), [TASK-163-06](./TASK-163-06_Default_Off_Segmentation_Sidecar_And_Artifact_Linkage.md), [TASK-166](./TASK-166_Hierarchical_Reference_Compare_Perceived_Evidence_And_Budget_Control.md)
**Priority:** 🔴 High
**Objective:** Extend the optional segmentation lane so packet-local SAM-family masks, crops, and optional derived anchors can support creature/reference ambiguity without becoming a default full-image heavy pass.
**Repository Touchpoints:** `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_silhouette.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `tests/e2e/vision/test_reference_understanding_runtime_surface.py`, `_docs/_VISION/README.md`
**Acceptance Criteria:**
- packet-bounded localized masks/crops and optional derived anchors can be returned through the existing segmentation/public support seams
- segmentation stays `advisory_only=True` and failure/absence still degrades to `disabled` or `unavailable`
- localized masks can pair with localization candidates or bounded region hints instead of forcing whole-reference heavy passes

## Implementation Notes

- build on the existing segmentation sidecar seam rather than inventing a
  parallel mask runtime
- build directly on the shipped `TASK-128-03` generic segmentation carrier and
  compare-time sidecar seam; do not reopen base provider packaging, part
  vocabulary, or the original `ReferencePartSegmentationContract` ownership
  unless a new follow-on is created explicitly
- treat the SAM-vs-SAM 2 provider choice as an implementation detail on the
  same seam; an image-packet baseline may ship on a SAM-compatible predictor,
  while SAM 2 is justified when its image predictor or future tracking path
  materially helps
- keep `reference_compare_packets.py` as the durable compare-time execution
  owner; do not move packet-local segmentation execution onto the RU-specific
  `vision/reference_support.py` seam unless shared helpers are extracted first
- concrete owner seams for this leaf:
  - `ReferencePartSegmentationLandmarkContract`
  - `ReferencePartSegmentationContract`
  - `ReferenceComparePacketContract`
  - `collect_compare_time_segmentation_support(...)`
  - `_build_compare_segmentation_request_payload(...)`
  - `merge_compare_time_part_segmentation(...)`
  - staged response projection in `reference.py`
- acceptable first support shapes:
  - packet-local mask refs
  - crop refs
  - optional derived 2D anchors for part tips, silhouette anchor points, or
    seam-adjacent cues
- preferred first use cases:
  - tail silhouette vs detached blob ambiguity
  - snout vs head seating ambiguity
  - ear/head local boundary ambiguity
  - limb/body seam-local cues where deterministic truth still lacks clean
    visual grounding
- landmarks on the current contract are derived anchors from masks/crops unless
  a provider already emits an equivalent bounded point set; do not require
  SAM- or SAM 2-native landmark output
- if part localization lands first, let localization boxes seed segmentation;
  otherwise keep mask requests bounded to existing packet-local hints

## Pseudocode

```python
segmentation = segment_local_region(
    reference_ids=packet.reference_ids,
    capture_labels=packet.capture_labels,
    seed_boxes=localization_candidates,
    max_parts=4,
)
return ReferencePartSegmentationContract(
    status="available",
    advisory_only=True,
    parts=segmentation.parts,
)
```

## Runtime / Security Contract Notes

- segmentation must remain optional and non-fatal
- localized masks/landmarks are not proof of completion or contact
- preserve current packet-budget and artifact-link boundaries

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_reference_compare_packets.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- `tests/e2e/vision/test_reference_understanding_runtime_surface.py`
- optional harness/eval coverage behind explicit sidecar enablement

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- include segmentation-sidecar localization notes in the first `TASK-172`
  changelog entry that ships this leaf

## Administrative Note

- the shipped packet-local segmentation runtime is already owned historically
  by the earlier segmentation-sidecar task family above
- `TASK-172-04` remains as a historical planning slice only; the current
  `TASK-172` work tightens activation policy around that shipped seam instead
  of reopening its provider/runtime ownership

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/vision/test_reference_understanding_runtime_surface.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- localized SAM-family segmentation sidecar and payload proof
