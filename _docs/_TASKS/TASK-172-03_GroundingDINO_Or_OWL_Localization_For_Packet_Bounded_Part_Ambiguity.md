# TASK-172-03: GroundingDINO Or OWL Localization For Packet-Bounded Part Ambiguity

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one optional packet-bounded text-conditioned localization adapter family that can produce bounded box/crop-style part cues for ambiguous reference regions during staged compare and iterate work, while reusing the existing optional-perception public carriers.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/areas/reference.py`, `server/adapters/mcp/areas/reference_feedback.py`, `server/adapters/mcp/areas/reference_planner.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_compare_packets.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/unit/adapters/mcp/test_contract_payload_parity.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- a default-off localization adapter can emit bounded box/crop-style cues for roles such as `tail_mass`, `snout_mass`, `ear_pair`, or limb roles on staged compare/iterate packets
- localization output is tied to packet/reference/view provenance and remains advisory-only
- localization output reuses the existing optional-perception public carriers instead of introducing a second localization-specific public envelope

## Implementation Notes

- first shipping adapter posture:
  - `generic_sidecar` provider family
  - one new dedicated config lane only if the existing segmentation/classifier
    config cannot express localization cleanly
  - vendor-specific behavior stays behind a vendor-neutral internal adapter seam
- reuse the existing optional-perception public carriers:
  - RU-side `segmentation_artifacts` with `artifact_kind="box"` when the same
    cue is useful during RU refresh
  - compare-time `part_segmentation` / `support_evidence` paths that already
    own optional packet-local artifacts
- map the emitted support onto the current staged owners:
  - `ReferenceUnderstandingSegmentationArtifactContract`
  - `ReferencePartSegmentationContract`
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
- keep DINOv2 dense features out of this first wave; they are not the most
  direct tool for actionable LLM-facing part feedback

## Pseudocode

```python
boxes = localize_parts(
    labels=["tail_mass", "body_core"],
    reference_slice=packet.reference_slice,
)
return ReferencePartSegmentationContract(
    status="available",
    advisory_only=True,
    parts=project_boxes_to_bounded_parts(boxes),
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
