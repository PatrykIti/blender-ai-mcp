# TASK-172-03: GroundingDINO Or OWL Localization For Packet-Bounded Part Ambiguity

**Parent:** [TASK-172](./TASK-172_Optional_Vision_Capability_Runtime_And_Localized_Perception.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High
**Objective:** Add one optional text-conditioned part-localization adapter family that can produce bounded part/anchor box candidates for ambiguous reference regions during RU refresh or staged compare packets.
**Repository Touchpoints:** `server/adapters/mcp/vision/reference_support.py`, `server/adapters/mcp/vision/config.py`, `server/adapters/mcp/vision/runtime.py`, `server/adapters/mcp/areas/reference_understanding.py`, `server/adapters/mcp/areas/reference_compare_packets.py`, `server/adapters/mcp/contracts/reference.py`, `server/infrastructure/config.py`, `tests/unit/adapters/mcp/test_reference_images.py`, `tests/unit/adapters/mcp/test_vision_runtime_config.py`, `tests/e2e/integration/test_guided_gate_state_transport.py`, `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
**Acceptance Criteria:**
- a default-off part-localization adapter can emit bounded localization candidates for roles such as `tail_mass`, `snout_mass`, `ear_pair`, or limb roles
- localization output is tied to packet/reference/view provenance and remains advisory-only
- localization candidates may seed support evidence or segmentation requests, but cannot pass gates or prove scene truth

## Implementation Notes

- prefer one vendor-neutral contract such as `part_localization_candidates`
  rather than adapter-specific raw payloads on public surfaces
- acceptable first adapter families:
  - GroundingDINO-like text-conditioned boxes
  - OWL / OWL-ViT-style text-conditioned localization
- first use cases should be narrow:
  - missing/ambiguous tail or snout region
  - ear vs eye vs face-attachment ambiguity
  - foreleg vs hindleg local ambiguity
  - anchor ambiguity for already-created parts
- if localization becomes useful outside compare packets, reuse the same typed
  support contract instead of creating a second RU-only output model
- keep DINOv2 dense features out of this first wave; they are not the most
  direct tool for actionable LLM-facing part feedback

## Pseudocode

```python
boxes = localize_parts(
    labels=["tail_mass", "body_core"],
    reference_slice=packet.reference_slice,
)
return SupportEvidence(
    evidence_kind="part_localization",
    authority="support_only",
    packet_id=packet.packet_id,
    candidates=boxes,
)
```

## Runtime / Security Contract Notes

- localization providers remain optional and default-off
- no raw image bytes or oversized model-native payloads on public contracts
- candidate boxes are support evidence only and must not become planner or
  verifier authority on their own

## Tests To Add/Update

- `tests/unit/adapters/mcp/test_vision_runtime_config.py`
- `tests/unit/adapters/mcp/test_reference_images.py`
- `tests/unit/adapters/mcp/test_contract_payload_parity.py` when new public
  fields are added
- `tests/e2e/integration/test_guided_gate_state_transport.py`
- optional harness/eval coverage only behind explicit env/config flags

## Docs To Update

- `_docs/_VISION/REFERENCE_UNDERSTANDING_ROADMAP.md`
- `_docs/_VISION/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` when operator setup for the
  adapter becomes real

## Changelog Impact

- name the chosen localization family and its advisory-only boundary when this
  leaf ships

## Status / Board Update

- board tracking remains on the umbrella `TASK-172`

## Validation Commands

- `git diff --check`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_vision_runtime_config.py tests/unit/adapters/mcp/test_reference_images.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_gate_state_transport.py -q`
- `PYTHONPATH=. poetry run pytest ./tests/unit`

## Validation Category

- optional localization adapter and advisory-support proof
