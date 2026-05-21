# TASK-172-04: SAM Or SAM2 Local Mask And Landmark Support

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Extend the optional segmentation lane so localized SAM / SAM2-style masks and landmarks can support packet-bounded creature/reference ambiguity without becoming a default full-image heavy pass.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_public_surface_docs.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/README.md`
**Acceptance Criteria:**
- packet-bounded localized masks/landmarks can be returned through the existing segmentation/public support seams
- segmentation stays `advisory_only=True` and failure/absence still degrades to `disabled` or `unavailable`
- localized masks can pair with localization candidates or bounded region hints instead of forcing whole-reference heavy passes

## Implementation Notes

- build on the existing segmentation sidecar seam rather than inventing a
  parallel mask runtime
- concrete owner seams for this leaf:
  - `ReferencePartSegmentationLandmarkContract`
  - `ReferencePartSegmentationContract`
  - `collect_compare_time_segmentation_support(...)`
  - `merge_compare_time_part_segmentation(...)`
  - staged response projection in `reference.py`
- acceptable first support shapes:
  - packet-local mask refs
  - crop refs
  - 2D landmarks for part tips, silhouette anchor points, or seam-adjacent cues
- preferred first use cases:
  - tail silhouette vs detached blob ambiguity
  - snout vs head seating ambiguity
  - ear/head local boundary ambiguity
  - limb/body seam-local cues where deterministic truth still lacks clean
    visual grounding
- if part localization lands first, let localization boxes seed segmentation;
  otherwise keep mask requests bounded to existing packet-local hints

## Pseudocode

```python
segmentation = segment_local_region(
    reference_slice=packet.reference_slice,
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
- `tests/unit/adapters/mcp/test_public_surface_docs.py`
- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- optional harness/eval coverage behind explicit sidecar enablement

## Docs To Update

- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Changelog Impact

- include segmentation-sidecar localization notes in the first `TASK-172`
  changelog entry that ships this leaf

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_reference_compare_packets.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_public_surface_docs.py tests/unit/adapters/mcp/test_vision_runtime_config.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- localized segmentation sidecar and payload proof
